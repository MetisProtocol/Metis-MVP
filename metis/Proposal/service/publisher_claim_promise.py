# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: publisher_claim_promise.py
@time: 2020/6/5 4:37 下午
@desc:
"""
import attr
import logging
import datetime
from itertools import chain
from metis.CommonService.common_validators import ValidatorsMeta
from metis.MetisExecption.MetisError import ValidationError, StopValidation, PersistenceError
from metis.SmartContract.contracts import MToken


@attr.s(hash=True, repr=True, cmp=False, frozen=True)
class PublisherClaimPromiseInfo:
    current_user_uid = attr.ib()
    publisher_uid = attr.ib()
    balance = attr.ib()
    current_user_eth = attr.ib()
    publisher_eth = attr.ib()
    participants = attr.ib()


class PublisherClaimPromiseService:

    def __init__(self, plugins, msc_orm, db):
        self.plugins = plugins
        self.msc_orm = msc_orm
        self.db = db

    def claim(self, info):
        try:
            self._validate_info(info)
            msc = self._transfer_token(info)
            msc = self._fresh_msc_record(msc)
        except Exception:
            raise
        return msc

    def _validate_info(self, info):
        validators = self.plugins.hook.metis_proposal_gather_publisher_claim_promise_validators()
        failures = []

        for validator in chain.from_iterable(validators):
            try:
                validator(info)
            except ValidationError as e:
                failures.append(e.reason)

        if failures:
            raise StopValidation(failures)

    def _transfer_token(self, info):
        token = MToken()
        msc = self.msc_orm.get_effective_promise(info.participants, info.current_user_uid)
        token.transfer(msc.msc_addr, 10, info.publisher_eth)
        return msc

    def _fresh_msc_record(self, msc):
        msc.utime = datetime.datetime.now()
        msc.msc_status = 1
        msc.save()
        return msc


