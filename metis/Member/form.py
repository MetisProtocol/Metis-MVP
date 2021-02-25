# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: form.py
@time: 2020/5/20 3:07 下午
@desc:
"""
from flask_wtf import FlaskForm
from wtforms import validators, StringField, IntegerField
from wtforms.validators import DataRequired


class DACMemberRegisterForm(FlaskForm):
    username = StringField("")
    email = StringField("")
    dac = StringField("")
    password = StringField("")
    confirm_password = StringField("")


class TransferForm(FlaskForm):
    private_key = StringField("", validators=[DataRequired(message="请输入私钥地址")])
    receiver_eth = StringField("", validators=[DataRequired(message="请输入接收者公钥")])
    amount = IntegerField("", validators=[DataRequired(message="请输入转账金额")])


