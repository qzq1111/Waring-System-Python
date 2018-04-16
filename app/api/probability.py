# coding:utf-8
from app.api.analysis.NB import NBclassifier
from .base import route
from flask import Blueprint, request
from ..entities.models import Sh_A_Share, db, Sh_Share_Warning
from datetime import datetime, timedelta
from jieba import analyse
import jieba
import os
from decimal import Decimal

service_name = 'analysis'
bp = Blueprint(service_name, __name__, url_prefix="/api/" + service_name)


@route(bp, '/', methods=["GET"])
def pro():
    path = os.path.join(os.path.dirname(__file__), 'static')
    userdict = os.path.join(path, 'CompanyName.txt')
    jieba.load_userdict(userdict)
    analyse.set_stop_words(os.path.join(path, 'StopWords.txt'))
    tagpath = os.path.join(path, "TexTrankTags.txt")
    tag_dict = {}
    with open(tagpath, 'r') as f:
        for i in f.readlines():
            k, v = i.strip().split(',')
            tag_dict[k.decode("utf-8")] = Decimal(v)

    date = datetime.strftime(datetime.now() - timedelta(days=180), "%Y-%m-%d")
    qs_code = db.session.query(Sh_Share_Warning.stockcode).all()
    code_list = map(lambda x: x.stockcode, qs_code)
    mappings = []

    for i, code in enumerate(code_list):
        qs = db.session.query(Sh_A_Share.title).filter(Sh_A_Share.bulletindate >= date,
                                                       Sh_A_Share.stockcode == code
                                                       ).all()
        data = ''
        for j in qs:
            data = data + j.title + '\n'
        tag_1 = jieba.analyse.textrank(data, topK=100, withWeight=False, allowPOS=('n', 'g', 'a', 'ad', 'an'))
        sum_ = Decimal(0)
        for tag in set(tag_1) & set(tag_dict.keys()):
            sum_ += tag_dict[tag]
        probability = (sum_ / sum(tag_dict.values())).quantize(Decimal('0.0000'))
        probability = float(probability * 100)
        mappings.append({"stockcode": code, "probability": probability})

    try:
        db.session.bulk_update_mappings(Sh_Share_Warning, mappings)
        db.session.commit()
    except Exception as e:
        print(e)

    return "done"


@route(bp, '/nbm', methods=["GET"])
def analysis_test():
    result = {"pro": 0.0, "data": []}
    base = os.path.join(os.path.dirname(__file__), 'analysis')
    nbclassifier = NBclassifier(clf_path=os.path.join(base, 'clf.m'), vec_path=os.path.join(base, 'vec.m'))
    stop_words = [line.strip().decode('utf-8')
                  for line in open(os.path.join(base, 'StopWords.txt'), 'r').readlines()]
    code = request.args.get("keyword", '600004')
    date = datetime.strftime(datetime.now() - timedelta(days=180), "%Y-%m-%d")
    qs = db.session.query(Sh_A_Share).filter(Sh_A_Share.bulletindate >= date,
                                             Sh_A_Share.stockcode == code).order_by(Sh_A_Share.bulletindate.desc())


    testData = []
    data = []
    for line in qs:
        lines = []
        data.append(dict(code=line.stockcode, date=line.bulletindate.strftime('%Y-%m-%d'),
                         name=line.stockname, title=line.title, url=line.url))
        for word in jieba.cut(line.title):
            if word in stop_words:
                pass
            else:
                lines.append(word)
        testData.append(' '.join(lines))
    if testData:
        predictList = nbclassifier.predictNB(testData)
        # sum_ = 0
        # for i in predictList:
        #     if i == '1':
        #         sum_ += 1
        # probability = (Decimal(sum_) / Decimal(len(predictList))).quantize(Decimal('0.0000'))*100
        # result["pro"] = float(probability)
        for k, v in zip(data, predictList):
            if v == '1':
                k.update({"flag": "预警"})
                result["data"].append(k)
            else:
                k.update({"flag": "不预警"})
                result["data"].append(k)
    return result
