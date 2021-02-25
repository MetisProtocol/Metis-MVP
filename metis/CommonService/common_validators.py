# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: common_validators.py
@time: 2020/5/26 9:46 上午
@desc:
"""
import re
from . import ValidatorsMeta
from metis.MetisExecption.MetisError import ValidationError, StopValidation
from metis.Account.model import Account
from metis.utils.helpers import md5


class EmailValidator(ValidatorsMeta):

    """
    验证邮箱地址是否符合规则
    """

    PATTERN = re.compile(r'\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}')

    def validate(self, info):
        match_result = re.match(self.PATTERN, info.email)
        if not match_result:
            raise ValidationError("email", "邮箱格式错误")


class EmailUniquenessValidator(ValidatorsMeta):
    """
    验证邮箱是否已经被注册
    """

    def __init__(self, model):
        self.model = model

    def validate(self, info):
        if self.model.email_exist(info.email):
            raise ValidationError("email", "邮箱地址已被注册")


class PasswordValidator(ValidatorsMeta):

    """
    密码验证器，验证输入密码是否正确
    """

    def validate(self, info):
        user = Account.get_user_by_email(info.email)
        if not user:
            raise ValidationError("password", "账户不存在")
        re_hash_password = md5(user.salt, info.password)
        if re_hash_password != user.password:
            raise ValidationError("password", "账号或密码错误")









