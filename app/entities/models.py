# coding:utf-8
"""
author:qinzhiqiang
date:2017/12/15
"""
from ..core import db


class Ip_Pool(db.Model):
    __tablename__ = 'ip_pool'
    id = db.Column(db.String(36), primary_key=True)
    ip = db.Column(db.String(36), nullable=True)
    updatetime = db.Column(db.DateTime, nullable=True)
    datastatus = db.Column(db.Integer, nullable=True)


class Sh_A_Share(db.Model):
    __tablename__ = 'sh_a_share'
    bulletinid = db.Column(db.String(32), primary_key=True)
    stockcode = db.Column(db.String(6), nullable=True)
    stockname = db.Column(db.String(30), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(255), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    bulletinyear = db.Column(db.Date, nullable=True)  # 公告年份
    bulletindate = db.Column(db.DateTime, nullable=True)  # 公告年份日期
    uploadtime = db.Column(db.DateTime, nullable=True)
    datastatus = db.Column(db.Integer, nullable=True)


class Sh_Share(db.Model):
    __tablename__ = 'sh_share'
    stockcode = db.Column(db.String(6), primary_key=True)
    stockname = db.Column(db.String(30), nullable=True)
    companycode = db.Column(db.String(7), nullable=True)
    companyname = db.Column(db.String(30), nullable=True)
    datastatus = db.Column(db.Integer, nullable=True)

class Sh_Share_Warning(db.Model):
    __tablename__ = 'sh_share_warning'
    stockcode = db.Column(db.String(6), primary_key=True)
    stockname = db.Column(db.String(30), nullable=True)
    datastatus = db.Column(db.Integer, nullable=True)
