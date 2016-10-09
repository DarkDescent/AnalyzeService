#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'DarkDescent'

import config
import tornado.web
import tornado.ioloop
import tornado.httpserver

#класс отвечает за отображение главной страницы
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if config.tornado_port:
            self.render('index.html', host=config.tornado_host, port=":" + str(config.tornado_port))
        else:
            self.render('index.html', host=config.tornado_host, port="")