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

import tornado.web
from handlers.queue_handler import analyze
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
    def prepare_job(file_path, file_name, request_ip, method, p_check, is_archive, archive_name=u""):
        from handlers.queue_handler import job_ids
        # отправляем обработку текста python-rq
        return analyze(file_path, method=method, prefix=p_check)


    # метод проверяет, соответствует ли расширение файла модулю patool
    @staticmethod
    def check_patool_ext(filename):
        file_ext = filename.split(".")[1]
        return file_ext in config.PATOOL_FILES_EXT

    # функция загружает файл, отправленный через Drag and Drop на сайте, считывает из него информацию и отправляет результат клиенту
    def load(self):

        fileinfo = self.request.files['file'][0]    # получаем всю информацию о файле
        method = self.get_argument("method")
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

        # отправляем файл на обработку, если вернули текст, то отправляем его пользователю, в случае неуспеха - отправляем об этом сообщение клиенту
        resultCheck = self.prepare_job(__UPLOADS__ + u'/' + fname, fname, self.request.remote_ip, method, prefix_check, False)

        filename = "%s_%s.txt" %(method, fname)
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header("Content-Description", 'File Transfer')
        self.set_header("Content-Disposition", 'attachment; filename=%s' % filename)
        with open(filename, mode="w") as fw:
            fw.write(resultCheck)
        self.finish(filename)



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

    def get(self, action):
        if action == "download":
            filename = self.get_argument("filename")
            if not filename:
                self.finish()
                return
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header("Content-Description", 'File Transfer')
            self.set_header("Content-Disposition", 'attachment; filename=%s' % filename)
            fr = open(filename, mode="r")
            _buffer = fr.read()
            self.finish(_buffer)
