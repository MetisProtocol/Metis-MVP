# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: sign.py
@time: 2020/5/25 10:42 上午
@desc:
"""
import attr
import logging
from itertools import chain
from metis.MetisExecption.MetisError import ValidationError, StopValidation
from ..model import Account

logger = logging.getLogger()


@attr.s(hash=True, cmp=False, repr=True, frozen=True)
class AccountSignInfo:
    email = attr.ib()
    password = attr.ib()


class AccountSignService:

    def __init__(self, plugins, user, db):
        self.plugins = plugins
        self.user = user
        self.db = db

    def sign(self, info, remote_ip):
        try:
            self._validate_sign(info)
        except StopValidation as e:
            raise
        user = self._fresh_last_ip(info, remote_ip)
        self._post_process(user)
        return user

    def _validate_sign(self, info):
        validators = self.plugins.hook.metis_account_gather_login_validators()
        failures = []

        for validator in chain.from_iterable(validators):
            try:
                validator(info)
            except ValidationError as e:
                failures.append(e.reason)
        if failures:
            raise StopValidation(failures)

    def _post_process(self, info):
        self.plugins.hook.metis_account_login_post_processor(info=info)

    def _fresh_last_ip(self, info, remote_ip):
        user = Account.get_user_by_email(info.email)
        if user:
            user.last_ip = remote_ip
            user.save()
            return user

    def _handle_failures(self):
        pass




