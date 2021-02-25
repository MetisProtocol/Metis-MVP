# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: form.py
@time: 2020/5/19 1:21 下午
@desc:
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextField
from wtforms.validators import DataRequired


class KnowledgeForm(FlaskForm):
    knowledge_name = StringField("", validators=[DataRequired(message='知识管理名称不能为空')])
    knowledge_describe = StringField("", validators=[DataRequired(message='知识管理描述不能为空')])


class KnowledgeDetailForm(FlaskForm):
    knowledge_detail_name = StringField("", validators=[DataRequired(message='知识管理条目不能为空')])
    knowledge_describe = StringField("", validators=[DataRequired(message='知识管理条目描述不能为空')])
    writer_balance = IntegerField("")
    joiner_balance = IntegerField("")
    joiner_excitation = IntegerField("")
    writer_excitation = IntegerField("")


class KnowledgeJoinForm(FlaskForm):
    pass


class KnowledgeInfoForm(FlaskForm):
    knowledge_info_type = StringField("")
    knowledge_info_memo = StringField("")


class KnowledgeInfoEditForm(FlaskForm):
    knowledge_detail_name = StringField("")
    knowledge_describe = StringField("")
    knowledge_detail_writer_pledge = IntegerField("")
    knowledge_detail_joiner_pledge = IntegerField("")
    knowledge_detail_writer_excitation = IntegerField("")
    knowledge_detail_joiner_excitation = IntegerField("")



# class JoinToDACForm(FlaskForm):
#     dac_id = StringField("", validators=[DataRequired(message="id不能为空")])



