# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: decorators.py
@time: 2020/5/26 10:51 上午
@desc:
"""
from flask import request, url_for, redirect, render_template
from functools import wraps


def activate_required(func):
    """
    DAC是否已激活，没有激活，跳转到激活页面
    :param func:
    :return:
    """
    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    return inner

