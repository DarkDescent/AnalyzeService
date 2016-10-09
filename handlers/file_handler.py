# -*- coding: utf-8 -*-
__author__ = 'DarkDescent'

"""
Модуль ответственнен за получение текста из файла, предоставленного пользователем
Основа - textract (http://textract.readthedocs.org/en/latest/)
"""

import codecs
import os
import re
import shutil
from os.path import expanduser

import patoolib
import textract
import tornado.web
from queueHandle import analyze
from redis import Redis
from rq import Queue
from tornado.web import HTTPError

import config

__UPLOADS__ = expanduser("~") + u"/uploads"
redis = Redis(host=config.redis_host, port=config.redis_port)
queue = Queue(config.queue_name, connection=redis)

class FileHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        tornado.web.RequestHandler.__init__(self, *args, **kwargs)

    @staticmethod
    def prepare_job(file_path, file_name, request_ip, a_ratio, p_check, is_archive, archive_name=u""):
        from queueHandle import job_ids
        # достаем данные из текста
        text = textract.process(file_path)
        # убираем из текста лишние символы (с ними могут начаться ошибки)
        text = re.sub(ur'\t|\n', u' ', text)
        # отправляем обработку текста python-rq
        job = queue.enqueue_call(analyze, args=(text, a_ratio, p_check), result_ttl=-1)
        result = {}
        # узнаем результат создания задачи - если не удалось, то отправляем сообщение об ошибке
        if not job:
            result["text"] = u""
            result["isDone"] = False
            return result
        else:   # если получилось - запоминаем название отдельных файлов (будут названиями задачи на клиентской части
            job.meta["name"] = file_name
            if is_archive:  # а также если мы знаем, что прислали архив - запоминаем название архива (сможем сгруппировать задачи на клиенте)
                job.meta["archive"] = os.path.splitext(archive_name)[0]
            else:
                job.meta["archive"] = ""
            job.save()
            global job_ids
            # сохраняем id задачи, чтобы по нему можно было обращаться к списку задач
            job_ids.append((job.id, file, request_ip))
            # возвращаем переданный текст и результат создания задачи RQ
            result["text"] = text
            result["isDone"] = True
            return result

    # метод проверяет, соответствует ли расширение файла модулю patool
    @staticmethod
    def check_patool_ext(filename):
        file_ext = filename.split(".")[1]
        return file_ext in config.PATOOL_FILES_EXT

    # функция загружает файл, отправленный через Drag and Drop на сайте, считывает из него информацию и отправляет результат клиенту
    def load(self):

        fileinfo = self.request.files['file'][0]    # получаем всю информацию о файле
        accuracy_ratio = float(self.get_argument('accuracy'), 0)
        prefix_check = bool(int(self.get_argument("is_prefix", default=1)))
        fname = fileinfo['filename']

        import sys

        reload(sys)
        sys.setdefaultencoding('utf-8')

        # сохраняем первоначальный файл во временную директорию
        with codecs.open(__UPLOADS__ + u'/' + fname,  mode='w') as fh:
            fh.write(fileinfo['body'])
        # при использовании прокси необходимо передать header Access-Control-Allow-Origin вместе с хостом/портом прокси
        if (config.proxy_is_using):
            self.set_header("Access-Control-Allow-Origin", "http://" + config.proxy_host + ":" + config.proxy_port)

        # проверяем, если у нас расширение файла соответствует модулю Patool (архив)
        if self.check_patool_ext(fname):
            # разархивируем файлы во временную директорию
            patoolib.extract_archive(__UPLOADS__ + u'/'+fname, outdir=(__UPLOADS__ + u"/tmp"), interactive=False)

            # создаем возможность для прохода по файлам
            walk = os.walk(__UPLOADS__ + u"/tmp")
            isWork = True

            # начинаем проходить по временной директории
            for (dirpath, dirnames, filenames) in walk:
                for file in filenames:
                    # узнаем статус всех работ, если все хорошо, то отправляем последний текст, если возникли проблемы, передаем сообщение клиенту
                    resultCheck = self.prepare_job(dirpath + u'/' + file, file, self.request.remote_ip, accuracy_ratio, prefix_check, True, archive_name=fname)
                    isWork = isWork and resultCheck["isDone"]
            # удаляем все файлы из временной директории
            shutil.rmtree(__UPLOADS__ + u"/tmp")
            if not isWork:
                self.finish(u"Не все файлы удалось отправить в очередь")
                return
            else:
                self.finish(resultCheck["text"])

        else:
            # отправляем файл на обработку, если вернули текст, то отправляем его пользователю, в случае неуспеха - отправляем об этом сообщение клиенту
            resultCheck = self.prepare_job(__UPLOADS__ + u'/' + fname, fname, self.request.remote_ip, accuracy_ratio, prefix_check, False)
            if resultCheck["text"] == u"":
                self.finish(u"Не все файлы удалось отправить в очередь")
                return
            else:
                self.finish(resultCheck["text"])


    def post(self, action):
        actions = {
            "upload": self.load
        }
        if actions.get(action):
            actions.get(action)()
        else:
            raise HTTPError(404)

    # обрабатываем особую ситуацию при использовании прокси.
    # При пересылке файлов сначала идет отсылка OPTIONS запроса, только потом POST.
    # Подробная информация - https://developer.mozilla.org/en-US/docs/Web/HTTP/Access_control_CORS#Preflighted_requests
    def options(self, action):
        if (config.proxy_is_using):
            self.set_header("Access-Control-Allow-Origin", "http://" + config.proxy_host + ":" + config.proxy_port)
        self.finish("ok")