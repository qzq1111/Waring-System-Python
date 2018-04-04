# coding:utf-8
"""
author:qinzhiqiang
date:2017/12/15
"""

from functools import wraps
from flask import jsonify


def to_dict(rv):
    if isinstance(rv, dict):
        return rv
    elif isinstance(rv, (list, tuple)) and not isinstance(rv, basestring):
        ds = []
        if len(rv) <= 0:
            return rv
        d0 = rv[0]
        f = getattr(d0, 'to_json', None)

        if (f is None) or (not callable(f)):
            return rv
        for d in rv:
            ds.append(to_dict(d))
        return ds
    else:
        f = getattr(rv, 'to_json', None)
        if (f is None) or (not callable(f)):
            return rv
        return rv.to_json()


def to_jsonify(rv, cnt):
    return jsonify(dict(data=to_dict(rv), total=cnt))


def route(bp, *args, **kwargs):
    kwargs.setdefault('strict_slashes', False)

    def decorator(f):
        @bp.route(*args, **kwargs)
        @wraps(f)
        def wrapper(*args, **kwargs):
            sc = 200
            rv = f(*args, **kwargs)
            if isinstance(rv, (int, long, float)):
                return str(rv)
            elif isinstance(rv, tuple):
                if len(rv) >= 3:
                    return rv[0], rv[1]
                else:
                    return jsonify(dict(to_dict(rv[0]))), rv[1]
            elif isinstance(rv, dict):
                return jsonify(dict(to_dict(rv))), sc
            else:
                return jsonify(dict(data=to_dict(rv))), sc

        return f

    return decorator


class retMsg(object):
    def __init__(self, data, code=200, msg="获取成功"):
        self._data = data
        self.retCode = code
        self.retMsg = msg

    def update(self, data=None, code=None, msg=None):
        if data is not None:
            self._data = data
        if code is not None:
            self.retCode = code
        if msg is not None:
            self.retMsg = msg

    def addField(self, name, value):
        self.__dict__[name] = value

    @property
    def data(self):
        body = self.__dict__
        body['data'] = body.pop('_data')
        return body

    @property
    def isEmpty(self):
        return not bool(self._data)

    @property
    def code(self):
        return self.retCode
