# coding:utf-8
"""
author:qinzhiqiang
date:2017/12/15
"""


class Config(object):
    SECRET_KEY = 'rmsobject'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mad123@39.108.60.79/graduation_project?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}