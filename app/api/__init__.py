# coding:utf-8
"""
author:qinzhiqiang
date:2017/12/15
"""
import atexit
import logging
import urllib2
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from ..config import config
from ..core import db, register_blueprints


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # app.config["SQLALCHEMY_ECHO"] = True
    db.init_app(app)
    register_blueprints(app, __name__, __path__)
    return app


scheduler = BackgroundScheduler()

scheduler.start()
atexit.register(lambda: scheduler.shutdown())

log = logging.getLogger('apscheduler.executors.default')
log.setLevel(logging.INFO)
fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(fmt)
log.addHandler(h)


def try_build_probability():
    url = "http://127.0.0.1:81/api/test/"
    res = urllib2.urlopen(url)


scheduler.add_job(
    func=try_build_probability,
    trigger='cron',
    hour=2,
    id='build_time_alert',
    name='build_time_alert',
    replace_existing=True)
