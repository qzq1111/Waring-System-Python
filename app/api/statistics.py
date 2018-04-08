# coding:utf-8
"""
author:qinzhiqiang
date:2018/01/22
"""
from .base import route
from flask import Blueprint, request
from ..entities.models import Sh_A_Share, db, Sh_Share_Warning
from sqlalchemy import func, extract
from datetime import datetime, timedelta

service_name = 'statistics'
bp = Blueprint(service_name, __name__, url_prefix="/api/" + service_name)


@route(bp, '/stockstat', methods=["GET"])
def stockstat():
    result = {"data": []}
    keyword = request.args.get("keyword")
    start = datetime.strftime(datetime.now() - timedelta(days=180), "%Y-%m-%d")
    end = datetime.strftime(datetime.now(), "%Y-%m-%d")
    data_query = db.session.query(Sh_A_Share.bulletindate,
                                  func.count('*').label('count')
                                  ).filter(Sh_A_Share.stockcode == keyword,
                                           Sh_A_Share.bulletindate.between(start, end)
                                           ).group_by(Sh_A_Share.bulletindate).all()
    sql = """
    select bulletindate,count(0) as total from sh_a_share WHERE stockcode='{}'
    AND bulletindate IN (SELECT bulletindate
    FROM sh_a_share WHERE  stockcode='{}' AND bulletindate BETWEEN '{}' AND '{}' AND title LIKE '%重大事项停牌公告')
    GROUP BY bulletindate """.format(keyword, keyword, start, end).decode('utf-8')
    data = db.session.execute(sql)
    result["point"] = map(lambda x: dict(date=str(x.bulletindate), total=x.total), data)
    result["data"] = map(lambda x: dict(name=str(x.bulletindate), value=x.count), data_query)
    return result


@route(bp, '/yearstat', methods=["GET"])
def yearsstat():
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


@route(bp, '/stat', methods=["GET"])
def stat():
    """
    最近五天的公告数
    :return:
    """
    result = {}

    date = datetime.strftime(datetime.now() - timedelta(days=7), "%Y-%m-%d")
    sql = "SELECT bulletindate as date ,COUNT(0) AS count FROM sh_a_share WHERE bulletindate >='{}' GROUP BY bulletindate;".format(
        date)
    data = db.session.execute(sql)
    result["data"] = map(lambda x: dict(date=str(x.date), count=x.count), data)

    date = datetime.strftime(datetime.now() - timedelta(days=1), "%Y-%m-%d")
    sql = "SELECT COUNT(0) as count  FROM sh_a_share WHERE bulletindate ='{}' ".format(date)
    qs_recently = db.session.execute(sql).scalar()
    result["recently_total"] = qs_recently
    sql = "SELECT count(0) as count,MAX(uploadtime) as date FROM sh_a_share"
    qs_total = db.session.execute(sql).first()

    result["total"] = qs_total[0]
    result["date"] = str(qs_total[1])
    result["warning"] = []

    sql = "SELECT datastatus,count(0) as count  FROM sh_share_warning GROUP BY datastatus"
    data_warning = db.session.execute(sql)
    for war in data_warning:
        if war.datastatus == 2:
            result["warning"].append({"name": "发生重大事项停牌公告", "value": war.count})
        elif war.datastatus == 1:
            result["warning"].append({"name": "未发生重大事项停牌公告", "value": war.count})

    return result


@route(bp, '/category', methods=["GET"])
def category():
    """
    某一股票公告分类统计数
    :return:
    """
    result = {}
    keyword = request.args.get("keyword")
    start = datetime.strftime(datetime.now() - timedelta(days=180), "%Y-%m-%d")
    end = datetime.strftime(datetime.now(), "%Y-%m-%d")
    data_query = db.session.query(
        Sh_A_Share.category,
        func.count('*').label("sh_a_count")
    ).filter(
        Sh_A_Share.stockcode == keyword,
        Sh_A_Share.bulletindate.between(start, end)).group_by(Sh_A_Share.category).all()
    result["data"] = map(lambda x: dict(name=x.category, value=x.sh_a_count), data_query)
    return result
