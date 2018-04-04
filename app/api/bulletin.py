# coding:utf-8
"""
author:qinzhiqiang
date:2017/12/15
"""
from .base import route
from flask import Blueprint, request
from ..entities.models import Sh_A_Share, db
from sqlalchemy import func, extract
from datetime import datetime, timedelta

service_name = 'bulletin'
bp = Blueprint(service_name, __name__, url_prefix="/api/" + service_name)


@route(bp, '/', methods=["GET"])
def bulletin_list():
    keyword = request.args.get("code", '600000')
    page = request.args.get("page", 1, type=int)
    pagesize = request.args.get("pagesize", 10, type=int)
    begin = request.args.get("start", datetime.strftime(datetime.now() - timedelta(days=31), "%Y-%m-%d"))
    end = request.args.get("end", datetime.strftime(datetime.now(), "%Y-%m-%d"))
    result = {"data": [], "total": 0}
    data_query = Sh_A_Share.query.filter(
        Sh_A_Share.stockcode == keyword, Sh_A_Share.bulletindate.between(begin, end)
    ).order_by(Sh_A_Share.bulletindate.desc())
    result["total"] = data_query.count()
    data = data_query.slice((page - 1) * pagesize, pagesize * page).all()
    result["data"] = map(lambda x: dict(code=x.stockcode,date=x.bulletindate.strftime('%Y-%m-%d'),
                                        name=x.stockname, title=x.title, url=x.url), data)
    return result


@route(bp, '/major', methods=["GET"])
def get_major():
    date = datetime.strftime(datetime.now() - timedelta(days=1), "%Y-%m-%d")
    qs = Sh_A_Share.query.filter(Sh_A_Share.bulletindate == date).all()






