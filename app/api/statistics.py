# coding:utf-8
"""
author:qinzhiqiang
date:2018/01/22
"""
from .base import route
from flask import Blueprint, request
from ..entities.models import Sh_A_Share, db
from sqlalchemy import func, extract
from datetime import datetime, timedelta

service_name = 'statistics'
bp = Blueprint(service_name, __name__, url_prefix="/api/" + service_name)


@route(bp, '/yearstat', methods=["GET"])
def statistics():
    """
    某一股票公告按照年份统计数
    :return:
    """
    result = {"data": []}
    keyword = request.args.get("keyword")
    data_query = db.session.query(extract('year', Sh_A_Share.bulletindate).label('year'),
                                  func.count('*').label('count')
                                  ).filter(Sh_A_Share.stockcode == keyword).group_by('year').all()
    result["data"] = map(lambda x: dict(name=x.year, value=x.count), data_query)
    return result


@route(bp, '/fivedaystat', methods=["GET"])
def fivedaydata():
    """
    最近五天的公告数
    :return:
    """
    result = {"data": []}
    date = datetime.strftime(datetime.now() - timedelta(days=7), "%Y-%m-%d")
    sql = "select DATE_FORMAT(bulletindate,'%Y-%m-%d') as date ,COUNT(bulletindate) as count " \
          "from sh_a_share where bulletindate  >'{}' GROUP BY date".format(date)
    data = db.session.execute(sql)
    result["data"] = map(lambda x: dict(date=x.date, count=x.count), data)
    return result


@route(bp, '/categorystat', methods=["GET"])
def category():
    """
    某一股票公告分类统计数
    :return:
    """
    result = {"data": []}
    keyword = request.args.get("keyword")
    data_query = db.session.query(Sh_A_Share.category,
                                  func.count('*').label("sh_a_count")
                                  ).filter(Sh_A_Share.stockcode == keyword).group_by(Sh_A_Share.category).all()
    result["data"] = map(lambda x: dict(name=x.category, value=x.sh_a_count), data_query)
    return result


@route(bp, '/stat', methods=["GET"])
def stat():
    """
    统计数据
    :return:
    """
    result = {}
    date = datetime.strftime(datetime.now(), "%Y-%m-%d")
    qs_recently = db.session.query(func.count(Sh_A_Share.bulletinid)).filter(Sh_A_Share.bulletindate == date).scalar()
    qs_total = db.session.query(func.count(Sh_A_Share.bulletinid),func.max(Sh_A_Share.uploadtime)).first()
    result["recently_total"] = qs_recently
    result["total"] = qs_total[0]
    result["date"] = str(qs_total[1])
    return result
