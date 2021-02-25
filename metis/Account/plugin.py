# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: plugin.py
@time: 2020/5/25 11:20 上午
@desc:
"""
from . import impl
from .model import Account
from metis.CommonService.common_validators import (EmailValidator, PasswordValidator, EmailUniquenessValidator)
from metis.CommonService.common_processor import AutoLoginPostProcessor


@impl
def metis_account_gather_registration_validators():
    return [
        EmailValidator(),
        EmailUniquenessValidator(Account)
    ]


@impl
def metis_account_registration_post_processor(info):
    handlers = list()

    handlers.append(AutoLoginPostProcessor())

    for handler in handlers:
        handler.post_process(info)


@impl
def metis_account_gather_login_validators():
    return [
        EmailValidator(),
        PasswordValidator()
    ]


@impl
def metis_account_login_post_processor(info):
    handlers = [
        AutoLoginPostProcessor()
    ]
    for handler in handlers:
        handler.post_process(info)

