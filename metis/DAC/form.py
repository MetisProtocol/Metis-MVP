# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: form.py
@time: 2020/5/28 12:31 下午
@desc:
"""
from flask_wtf import FlaskForm
from wtforms import StringField


class ActivityDACForm(FlaskForm):

    dac_id = StringField("")
    excitation = StringField("")
