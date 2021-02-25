# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: common_processor.py
@time: 2020/5/26 10:22 上午
@desc:
"""
from flask_login import login_user
from . import ProcessorMeta


class AutoLoginPostProcessor(ProcessorMeta):
    def post_process(self, user):
        login_user(user)

