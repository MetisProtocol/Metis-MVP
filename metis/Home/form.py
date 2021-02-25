# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: form.py
@time: 2020/5/19 1:21 下午
@desc:
"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class GenerateDACForm(FlaskForm):
    dac_name = StringField("", validators=[DataRequired(message='用户名不能为空')])
    dac_describe = StringField("", validators=[DataRequired(message="描述不能为空")])
    file = StringField("")


class JoinToDACForm(FlaskForm):
    dac_id = StringField("", validators=[DataRequired(message="id不能为空")])



