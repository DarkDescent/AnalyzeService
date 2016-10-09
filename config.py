# -*- coding: utf-8 -*-
__author__ = 'DarkDescent'

"""
Модуль грузит данные конфигураций.
Также он подгружает файлы, содержащие статистики по длине предложения и по количеству частей речи
"""

import yaml

with open("config/main.yml", 'r') as conf_file:
    conf = yaml.load(conf_file)
    language_tool_host = conf["languagetool"]["host"]
    language_tool_port = conf["languagetool"]["port"]
    queue_name = conf["queue"]["name"]
    redis_host = conf["redis"]["host"]
    redis_port = conf["redis"]["port"]
    tornado_port = conf["tornado"]["port"]
    tornado_host = conf["tornado"]["host"]
    proxy_host = conf["proxy"]["host"]
    proxy_port = str(conf["proxy"]["port"])
    proxy_is_using = conf["proxy"]["is_using"]