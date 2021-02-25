# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: factory.py
@time: 2020/5/25 10:42 上午
@desc:
"""
from flask import current_app
from metis.extensions import db
from ..model import Account
from .Registration import RegistrationService
from .Login import AccountSignService


def account_registration_service():
    return RegistrationService(current_app.pluggy, Account, db)


def account_login_service():
    return AccountSignService(current_app.pluggy, Account, db)

