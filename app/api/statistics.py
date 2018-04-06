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


@route(bp, '/stockstat', methods=["GET"])
def stockstat():
    result = {"data": []}
    keyword = request.args.get("keyword")
    data_query = db.session.query(Sh_A_Share.bulletindate,
                                  func.count('*').label('count')
                                  ).filter(Sh_A_Share.stockcode == keyword).group_by(Sh_A_Share.bulletindate).all()
    sql = """
    select bulletindate,count(0) as total from sh_a_share WHERE stockcode='{}' 
    AND bulletindate IN (SELECT bulletindate
    FROM sh_a_share WHERE  stockcode='{}' AND  title LIKE '%重大事项停牌公告')
    GROUP BY bulletindate """.format(keyword, keyword).decode('utf-8')
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


@route(bp, '/fivedaystat', methods=["GET"])
def fivedaystat():
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


@route(bp, '/category', methods=["GET"])
def category():
    """
    某一股票公告分类统计数
    :return:
    """
    c = {"其它": 0,
         "可转债": 0,
         "公司债": 0, "规则": 0,
         "会议资料": 0, "IPO公司公告": 0,
         "第一季度季报": 0, "发行与上市": 0,
         "年报": 0, "半年报": 0, "公司章程": 0,
         "年报摘要": 0, "第三季度季报": 0,
         "半年报摘要": 0, "股权分置": 0,
         "上市公司治理专项活动自查报告和整改计划": 0, }
    result = {}
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
    date = datetime.strftime(datetime.now() - timedelta(days=1), "%Y-%m-%d")
    qs_recently = db.session.query(func.count(Sh_A_Share.bulletinid)).filter(Sh_A_Share.bulletindate == date).scalar()
    qs_total = db.session.query(func.count(Sh_A_Share.bulletinid), func.max(Sh_A_Share.uploadtime)).first()
    result["recently_total"] = qs_recently
    result["total"] = qs_total[0]
    result["date"] = str(qs_total[1])
    return result
