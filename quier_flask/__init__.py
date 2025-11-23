# -*- coding:utf-8 -*-
from flask import Flask
from quier_flask import app_cfg

app = Flask(__name__)

cfg = app_cfg.MCfg(r'cfg.ini')
