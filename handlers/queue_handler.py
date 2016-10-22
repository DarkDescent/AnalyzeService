# -*- coding: utf-8 -*-
__author__ = 'DarkDescent'

"""
Модуль содержит хэндлер для работы с очередями
В результате будет возможность запускать отдельные функции text_analyze, чтобы записать их в очередь и использовать в своей работе
"""

import json
import sys

import regex as re
import tornado.web
from redis import Redis
from rq import Queue
from tornado import websocket
from tornado.web import HTTPError

import config

from methods.backpropagation import main
from methods.cure import cure_new
from methods.kmeans import kmeans_parallel
from methods.naivebayes import newsclassifier

job_ids = []
redis = Redis(host=config.redis_host, port=config.redis_port)
queue = Queue(config.queue_name, connection=redis)


# метод, который будет передан в python-rq для worker-ов
def analyze(data_origin, method, prefix):
    methods = {"kmeans": kmeans_parallel,
               "cure": cure_new,
               "neuron": main,
               "classification": newsclassifier}
    return methods.get(method).main(data_origin)


# def print_smth():
#     print "ABC"

# класс отвечает за создание задачи и отправки ее в очередь (в случае, если текст был передан не через DragnDrop файла
class QueueHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        tornado.web.RequestHandler.__init__(self, *args, **kwargs)
        self.redis_conn = redis
        self.analyze_queue = queue

        reload(sys)
        sys.setdefaultencoding("utf-8")


    def post(self):
        if self.get_argument("type") == "enqueue":      # если нужно поставить новую задачу в очередь
            # получаем аргументы
            text = u"" + self.get_argument("text")
            name = u"" + self.get_argument("name")
            accuracy = float(self.get_argument("accuracy"))
            prefix_check = bool(int(self.get_argument("is_prefix", default=1)))
            if (text == u"") or (name == u"") or not (0 <= accuracy <= 1):  # если какой-либо параметр отсутстсвует, то передаем ошибку 404
                raise HTTPError(404)
            # ставим задачу в очередь, меняем ее название

            text = re.sub(ur'\t|\n', u' ', text)    # убираем лишнее в тексте
            text = re.sub(ur'\.', u'. ', text)  # в некоторых случаях остается точка без последующего пробела
            # создаем задачу и отправляем ее python-rq
            job = self.analyze_queue.enqueue_call(analyze, args=(text, accuracy, prefix_check), result_ttl=-1)
            # запоминаем имя задачи - поскольку данный хэндлер вызывается только если пользователь нажал кнопку для отправки текста,
            # то названия архива не будет (нечего группировать)
            job.meta["name"] = name
            job.meta["archive"] = u''
            job.save()
            global job_ids
            # сохраняем id задачи, чтобы по нему можно было обращаться к списку задач
            job_ids.append((job.id, name, self.request.remote_ip))
            result = {}
            # сохраняем статус постановки задачи в очередь и отправляем результат пользователю
            if job:
                result["status"] = "started"
            else:
                result["status"] = "failed"
            result["name"] = name
            # устанавливаем нужные header-ы (отправляем json - указываем это
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            if (config.proxy_is_using): # при использовании прокси нужно передать этот параметр в заголовке вместе с адресом прокси
                self.set_header("Access-Control-Allow-Origin", "http://" + config.proxy_host + ":" + config.proxy_port)
            self.finish(json.dumps(result))

    # def get(self):
    #     job = self.analyze_queue.enqueue_call(print_smth, args=(), result_ttl=-1)
    #     print job
    #     print "Something"


# класс отвечает за получение информации о работе и очистки очередей из Redis
class JobHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        tornado.web.RequestHandler.__init__(self, *args, **kwargs)
        self.redis_conn = redis
        self.analyze_queue = queue

    def get(self, _type):
        types = {
            "job_take": self.get_job,
            "job_clear": self.clear_jobs,
        }
        if types.get(_type):
            types.get(_type)()
        else:
            raise HTTPError(404)
    # функция получает на вход id задачи, в ответ отправляет данные о задачи и результат ее работы
    def get_job(self):
        id = self.get_argument("job_id")
        global job_ids
        # проходим по списку полученных задач, если номер сооветствует
        for job_id in job_ids:
            if id in job_id:
                job = self.analyze_queue.fetch_job(id)  # получаем результат работы задачи и отправляем ее пользователю
                result = job.result
                if (config.proxy_is_using): # при использовании прокси нужно передать этот параметр в заголовке вместе с адресом прокси
                    self.set_header("Access-Control-Allow-Origin", "http://" + config.proxy_host + ":" + config.proxy_port)
                self.set_header("Content-Description", 'File Transfer')
                self.set_header("Content-Disposition",
                                        "attachment;filename=%s %s.txt" % (job.type, job_id))
                self.set_header("Content-Transfer-Encoding", "text")
                self.finish()
        raise HTTPError(404)

    # функция позволяет удалить все задачи из Redis, которые ассоциированы с данным пользователем
    def clear_jobs(self):
        # получаем адрес пользователя
        ip = self.request.remote_ip
        remove_list = []
        global job_ids
        for i in range(len(job_ids)):
            if job_ids[i][2] == ip: # если IP, записанный в информации о задаче, соответствует адресу пользователя, отправившего запрос
                remove_list.append(i)   # удаляем работу из списка
                job = self.analyze_queue.fetch_job(job_ids[i][0])   # удаляем задачу из очереди Redis
                job.delete()
        job_ids = [v for i, v in enumerate(job_ids) if i not in remove_list]


# класс отвечает за обработку запросов от клиента по сокетам
class SocketHandler(websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        websocket.WebSocketHandler.__init__(self, *args, **kwargs)
        self.redis_conn = redis
        self.analyze_queue = queue

    def check_origin(self, origin):
        return True

    # обработка запроса на открытие соединения
    def open(self):
        print("Opened: ", self.request.remote_ip)

    # обработка запроса на получение информации о сообщении
    def on_message(self, message):
        if message != "status":
            self.write_message("Error")
            return
        # если нужно узнать статус задач
        results = []
        result = {}
        global job_ids
        if len(job_ids) == 0:
            self.write_message("None")
            return

        archives_info = {}
        # для каждой задачи мы записываем ее результат и статус и отправляем все пользователю
        for job_id in job_ids:
            if self.request.remote_ip == job_id[2]: # если ip пользователя совпадает с указанным в информации о задаче
                job = self.analyze_queue.fetch_job(job_id[0])   # получаем подробное описание задачи
                if job is None: # если мы ничего не получили, то, скорее всего, задача была удалена
                    result["status"] = "deleted"
                    result["name"] = job_id[1]
                    results.append(result.copy())
                    job_ids.remove(job_id)
                    continue
                result["name"] = job.meta["name"]   # получаем информацию о названии задачи
                if (job.is_failed == True): # если выполнение задачи провалилось
                    result["status"] = "failed"
                elif (job.is_finished == True): # если задача выполнена
                    result["status"] = "finished"
                    # получаем результат и отправляем клиенту
                    result["id"] = job_id[0]
                    result["results"] = job.result
                elif (job.is_queued == True):   # если задача находится в очереди
                    result["status"] = "queued"
                else:   # если задача начала выполняться
                    result["status"] = "started"

                if result["name"] not in archives_info:
                    archives_info[result["name"]] = []
                archives_info[result["name"]].append(result.copy())
        self.write_message(json.dumps(archives_info))

    # обрабатываем ситуацию, когда клиент закрыл соединение с сервером
    def on_close(self):
        print("Closed ", self.request.remote_ip)