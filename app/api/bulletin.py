# coding:utf-8
"""
author:qinzhiqiang
date:2017/12/15
"""
from .base import route
from flask import Blueprint, request
from ..entities.models import Sh_A_Share, db, Sh_Share_Warning
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from jieba import analyse
import jieba
from wordcloud import WordCloud
from PIL import Image, ImageDraw, ImageFont
import random
import os
from decimal import Decimal

service_name = 'bulletin'
bp = Blueprint(service_name, __name__, url_prefix="/api/" + service_name)


@route(bp, '/', methods=["GET"])
def bulletin_list():
    keyword = request.args.get("keyword", '600000')
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
    result["data"] = map(lambda x: dict(code=x.stockcode, date=x.bulletindate.strftime('%Y-%m-%d'),
                                        name=x.stockname, title=x.title, url=x.url), data)
    return result


@route(bp, '/major', methods=["GET"])
def get_major():
    date = datetime.strftime(datetime.now() - timedelta(days=1), "%Y-%m-%d")
    qs = Sh_A_Share.query.filter(Sh_A_Share.bulletindate == date).all()


@route(bp, '/warning/probability', methods=["GET"])
def warning():
    result = {"pro": 0.0,"url":""}
    code = request.args.get("keyword", '600000')
    date = datetime.strftime(datetime.now() - timedelta(days=180), "%Y-%m-%d")
    qs = db.session.query(Sh_A_Share.title).filter(Sh_A_Share.bulletindate >= date,
                                                   Sh_A_Share.stockcode == code).all()
    data = ''
    for i in qs:
        data = data + i.title + '\n'
    if data:
        jieba.load_userdict(os.path.join(os.path.join(os.path.dirname(__file__), 'static'), 'CompanyName.txt'))
        analyse.set_stop_words(os.path.join(os.path.join(os.path.dirname(__file__), 'static'), 'StopWords.txt'))
        cut_keyword = jieba.analyse.textrank(data, topK=100, withWeight=True, allowPOS=('n', 'g', 'an'))
        keywords = dict()
        for key in cut_keyword:
            keywords[key[0]] = key[1]
        result["pro"] = calculate_probability(keywords=keywords)
        result["url"] = "http://39.108.60.79/image/{}.png".format(code)
        cloud(code=code, keywords=keywords)

    return result


def calculate_probability(keywords):
    """
    计算概率
    :param keywords:
    :return:
    """
    tags_dict = dict()
    with open(os.path.join(os.path.join(os.path.dirname(__file__), 'static'), "TexTrankTags.txt"), 'r') as f:
        for i in f.readlines():
            k, v = i.strip().split(',')
            tags_dict[k.decode("utf-8")] = float(v)
    sum_ = Decimal(0)
    for tag in set(keywords.keys()) & set(tags_dict.keys()):
        sum_ += Decimal(tags_dict[tag])
    probability = (sum_ / Decimal(sum(tags_dict.values()))).quantize(Decimal('0.0000'))
    return float(probability * 100)

r= lambda: random.randint(0,255)

def cloud(code, keywords):
    """
    生成词云图片
    :param code:
    :param keywords:
    :return:
    """
    path = os.path.join(os.path.dirname(__file__), 'static')
    font = os.path.join(path, "simhei.ttf")
    image_path = os.path.join(os.path.dirname(__file__), 'image')
    image = os.path.join(image_path, "{}.png".format(code))
    wc = WordCloud(font_path=font, background_color='white', width=650,
                   height=300, max_font_size=80,
                   max_words=100)
    wc.generate_from_frequencies(keywords)
    img = Image.new(mode="RGBA", size=(1400, 400), color=(255, 255, 255))
    tag_img = Image.open(fp=os.path.join(image_path, "Tags.png"))
    code_img = wc.to_image()
    img.paste(tag_img, box=(10, 100))
    img.paste(code_img, box=(700, 100))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font=font, size=42)
    title = u"关键字词云对比"
    tag_title = u"历史关键字词云"
    code_title = u"{}关键字词云".format(code)
    # draw.line(xy=[(95, 0), (95, 700)], width=1, fill=(0, 0, 0))
    draw.line(xy=[(680, 45), (680, 700)], width=1, fill=(0, 0, 0))
    draw.line(xy=[(0, 45), (1400, 45)], width=1, fill=(0, 0, 0))
    draw.line(xy=[(0, 95), (1400, 95)], width=1, fill=(0, 0, 0))
    # draw.line(xy=[(0, 350), (1400, 350)], width=1, fill=(0, 0, 0))
    draw.text(xy=(500, 5), text=title, font=font, fill=(r(), r(), r()))
    draw.text(xy=(200, 55), text=tag_title, font=font, fill=(r(), r(), r()))
    draw.text(xy=(900, 55), text=code_title, font=font, fill=(r(), r(), r()))
    img.save(image)


@route(bp, '/warning/list', methods=["GET"])
def warning_list():
    result = {"data": []}
    qs = db.session.query(Sh_Share_Warning).order_by(Sh_Share_Warning.probability.desc()).slice(0, 20).all()
    result["data"] = map(lambda i: {"stockcode": i.stockcode,
                                    "name": i.stockname, "probability": float(i.probability)}, qs)
    return result
