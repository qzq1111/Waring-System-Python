# coding:utf-8
"""
author:qinzhiqiang
date:2017/12/15
"""
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
