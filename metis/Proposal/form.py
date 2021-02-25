# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: form.py
@time: 2020/6/1 12:08 下午
@desc:
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired


class AddProposalForm(FlaskForm):
    work_name = StringField("", validators=[DataRequired(message="工作名称不允许为空")])
    work_expiry = StringField("", validators=[DataRequired(message="工作预期天数不能为空")])
    work_excitation = IntegerField("", validators=[DataRequired(message="工作激励不允许为空")])


class ExcitationClaimProposalForm(FlaskForm):
    active_dac_id = StringField("", validators=[DataRequired(message="")])
    active_work_id = StringField("", validators=[DataRequired(message="")])


class ClaimPromiseForm(FlaskForm):
    work_id = StringField("", validators=[DataRequired(message="")])
    publisher = StringField("", validators=[DataRequired(message="")])


class PublisherClaimPromiseForm(FlaskForm):
    publisher = StringField("", validators=[DataRequired(message="")])
    participants = StringField("", validators=[DataRequired(message="")])


class ProposalSubmitForm(FlaskForm):
    work_id = StringField("", validators=[DataRequired(message="")])


class WorkInfoForm(FlaskForm):
    work_type = StringField("")
    work_memo = StringField("")
    enclosure = StringField("")






