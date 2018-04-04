# coding:utf-8
"""
author:qinzhiqiang
date:2017/12/15
"""
from app.api import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)
