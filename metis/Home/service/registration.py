# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: registration.py
@time: 2020/5/19 3:00 下午
@desc:
"""
import attr
import json
from flask import redirect, url_for
from itertools import chain
from ..model import DAC
from metis.Home.service import ValidatorBase, PostProcessorBase
from metis.MetisExecption import ValidationError, StopValidation, PersistenceError


@attr.s(hash=True, cmp=False, repr=True, frozen=True)
class GenerateDACInfo:
    """
    DAC Registration obj, contains all relevant information for validating and create new dac
    """
    dac_name = attr.ib()
    dac_description = attr.ib()
    dac_logo = attr.ib()


class DACNameUniquenessValidator(ValidatorBase):

    def validate(self, dac_info):
        if DAC.is_exists(dac_info.dac_name):
            raise ValidationError("generate_dac", "DAC名称已存在")


class GenerateDACService:

    def __init__(self, plugins, orm, db):
        self.plugins = plugins
        self.dac_orm = orm
        self.db = db

    def register(self, dac_info, account):
        try:
            self._validate_registration(dac_info)
        except StopValidation:
            raise
        dac = self._store_dac(dac_info, account)
        return dac

    def _validate_registration(self, dac_info):
        failures = []
        validators = self.plugins.hook.metis_generate_dac_validators()

        for validator in chain.from_iterable(validators):
            try:
                validator(dac_info)
            except ValidationError as e:
                failures.append(e.reason)

        if failures:
            raise StopValidation(failures)

    def _store_dac(self, dac_info, account):
        try:
            dac = self.dac_orm(dac_info.dac_name, dac_info.dac_description, account.uid)
            if dac_info.dac_logo:
                dac.dac_logo = dac_info.dac_logo
            account_dac = json.loads(account.dac) if account.dac else []
            account_dac.append(dac.dac_id)
            account.dac = json.dumps(account_dac)
            self.db.session.add(dac)
            self.db.session.add(account)
            self.db.session.commit()
        except Exception as e:
            print(e)
            self.db.session.rollback()
            raise PersistenceError("Could not persistence dac")
        return dac



