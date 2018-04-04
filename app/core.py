# coding:utf-8
"""
author:qinzhiqiang
date:2017/12/15
"""
from flask_sqlalchemy import SQLAlchemy
import importlib
import pkgutil
from flask import Blueprint

db = SQLAlchemy()


def register_blueprints(app, package_name, package_path):
    rv = []
    for _, name, _ in pkgutil.iter_modules(package_path):
        m = importlib.import_module('%s.%s' % (package_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)
            rv.append(item)
    return rv
