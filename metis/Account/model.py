# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: model.py
@time: 2020/5/25 10:29 上午
@desc:
"""
import logging
import datetime
from metis.extensions import db
from metis.utils.helpers import md5
from random import randint
from string import ascii_letters
from flask_login import UserMixin


error_log = logging.getLogger().error


class Account(db.Model, UserMixin):
    __tablename__ = "metis_account"

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(255), nullable=False, index=True)
    username = db.Column(db.String(255), default='metis_test')
    email = db.Column(db.String(46), nullable=False)
    logo = db.Column(db.String(40), default='robort.jpg')
    salt = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    utime = db.Column(db.DateTime, nullable=False)
    ctime = db.Column(db.DateTime, nullable=False)
    last_ip = db.Column(db.String(20))
    eth_addr = db.Column(db.String(255))

    dac = db.Column(db.Text)    # 属于该用户的所有dac，包括创建的，加入的 [dac_id, ....]

    def __init__(self, email, password):
        self.email = email
        self.uid = self._gen_uid()
        self.salt = self._gen_salt()
        self.ctime = datetime.datetime.now()
        self.utime = datetime.datetime.now()
        self.password = self._gen_password(password)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            error_log(e)
            db.session.rollback()

    @staticmethod
    def _gen_salt():
        words = ascii_letters + "0123456789"
        return ''.join(
            [words[randint(0, 61)] for _ in range(4)]
        )

    def _gen_password(self, password):
        return md5(self.salt, password)

    @staticmethod
    def _gen_uid():
        last_account = Account.query.order_by(Account.uid.desc()).first()
        if not last_account:
            return "MU0000001"
        last_uid = last_account.uid.replace("MU", "")
        new_id = int(last_uid) + 1
        return f"MU{new_id:0>7d}"

    @staticmethod
    def get_user_by_email(email):
        account = Account.query.filter(Account.email == email).first()
        return account

    @staticmethod
    def get_user_by_uid(uid):
        return Account.query.filter(Account.uid == uid).first()

    @staticmethod
    def email_exist(email):
        account = Account.query.filter(Account.email == email).first()
        return True if account else False










