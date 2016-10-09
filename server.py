#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'DarkDescent'

import config
import tornado.web
import tornado.ioloop
import tornado.httpserver
from handlers.main_handler import MainHandler
import os

settings = {
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
}

#оформляем Tornado application
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/*static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
], **settings)

#запускаем сервер
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port=config.tornado_port, address=config.tornado_host)
    tornado.ioloop.IOLoop.instance().start()