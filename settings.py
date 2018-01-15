import os
import siteasy
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from collections import OrderedDict
import logging
import logging.config
import sys

VERSION = "0.1.0"
PLUGINS_PATH = 'plugins'

#get global_config from config.json
CONFIG_FILE = 'config.json'



LOGGING = {
    'version': 1,
    #'formatters':{
    #    'default': {
    #        'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
    #    },
    #},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file':{
            'class': 'logging.FileHandler',
            #'formatter': 'default',
            'filename': 'site.log',
            'mode': 'w',
            #'encoding': 'utf-8',
        },
    },
    'root': {
        'handlers': ['file'],
        'level' : 'DEBUG',
    },
}

logging.config.dictConfig(LOGGING)

f = open(CONFIG_FILE,encoding='utf-8')
global_config = json.loads(f.read(),object_pairs_hook=OrderedDict)
f.close()

global_context = {k:global_config[k] for k in ['logo','footer']}
global_site_map = [] 

env = Environment(
        loader=FileSystemLoader([os.path.join(os.getcwd(),'siteasy','theme',global_config['theme']),os.path.join(os.getcwd(),'siteasy',PLUGINS_PATH)]),
        autoescape=select_autoescape(['html', 'xml'])
    )
