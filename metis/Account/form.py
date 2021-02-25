# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: form.py
@time: 2020/5/25 10:29 上午
@desc:
"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, EqualTo


class AccountRegisterForm(FlaskForm):
    email = StringField("", validators=[DataRequired(message="邮箱不能为空")])
    password = StringField("", validators=[DataRequired(message="密码不能为空")])
    confirm_password = StringField("", validators=[EqualTo('password', message='新密码两次输入不一致')])


class AccountSignForm(FlaskForm):
    email = StringField("", validators=[DataRequired(message="邮箱不能为空")])
    password = StringField("", validators=[DataRequired(message="密码不能为空")])

