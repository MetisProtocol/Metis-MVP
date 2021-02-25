# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: Registration.py
@time: 2020/5/25 10:42 上午
@desc:
"""
import attr
import datetime
import logging
from itertools import chain
from metis.MetisExecption.MetisError import ValidationError, StopValidation
from ..model import Account
from metis.SmartContract.model import Eth
from metis.email import SendMail

debug_log = logging.getLogger().debug
info_log = logging.getLogger().info
error_log = logging.getLogger().error


@attr.s(repr=True, cmp=False, frozen=True, hash=True)
class AccountRegisterInfo:
    email = attr.ib()
    password = attr.ib()
    confirm_password = attr.ib()


class RegistrationService:

    def __init__(self, plugins, user, db):
        self.plugins = plugins
        self.user = user
        self.db = db

    def register(self, info, remote_ip):
        try:
            self._validate_registration(info)
            Eth.generate_eth()
        except StopValidation as e:
            error_log(e.reasons)
            raise
        user, eth = self._store_user(info, remote_ip, Eth.generate_eth())
        self.send_email(info, eth)
        self._post_process(user)
        return user

    def _validate_registration(self, info):
        validators = self.plugins.hook.metis_account_gather_registration_validators()
        failures = []

        for validator in chain.from_iterable(validators):
            try:
                validator(info)
            except ValidationError as e:
                error_log(e.reason)
                failures.append(e.reason)
        if failures:
            raise StopValidation(failures)

    def _handle_failure(self):
        pass

    def _store_user(self, info, remote_ip, eth):
        user = Account(
            email=info.email,
            password=info.password
        )
        user.last_ip = remote_ip
        user.eth_addr = eth.public_key
        eth.is_assigned = 1
        eth.account_uid = user.uid
        eth.utime = datetime.datetime.now()
        eth.save()
        user.save()
        return user, eth

    def send_email(self, info, eth):
        mail = SendMail([info.email.strip(' ')], "register")
        mail.send(eth.private_key, )

    def _post_process(self, user):
        self.plugins.hook.metis_account_registration_post_processor(info=user)









