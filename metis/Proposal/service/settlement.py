# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: submit.py
@time: 2020/6/10 7:09 下午
@desc:
"""
import attr
import datetime
from flask_login import current_user
from itertools import chain
from metis.MetisExecption.MetisError import ValidationError, StopValidation, PersistenceError
from metis.CommonService.common_validators import ValidatorsMeta
from metis.SmartContract.contracts import MSC
from metis.Proposal.model import Operation


@attr.s(repr=True, hash=True, cmp=False, frozen=True)
class SettlementInfo:
    work_id = attr.ib()
    current_eth = attr.ib()
    participants_eth = attr.ib()
    publisher_eth = attr.ib()

class SettlementService:
    def __init__(self, plugins, work_orm, msc_orm, db):
        self.plugins = plugins
        self.work_orm = work_orm
        self.msc_orm = msc_orm
        self.db = db

    def settlement(self, info):
        work = self.work_orm.get_work_by_work_id(info.work_id)
        try:
            msc = None
            if work.work_status == 3:
                self._out_one_msc_from_chain(info)
            elif work.work_status == 4 or work.work_status == 5:
                self._out_all_msc_from_chain(info)
                msc = self._fresh_msc_state(info)
            work = self._fresh_work_state(info)
            db_list = [work] if not msc else [work, msc]
            # self._out_promise_from_chain(info)
            self._store(db_list)
        except Exception:
            raise
        return

    def _validate_promise_claim(self, info):
        validators = self.plugins.hook.metis_proposal_gather_settlement_validators()
        failures = []

        for validator in chain.from_iterable(validators):
            try:
                validator(info)
            except ValidationError as e:
                failures.append(e.reason)

        if failures:
            raise StopValidation(failures)

    def _out_one_msc_from_chain(self, info):
        msc_record = self.msc_orm.get_formal_by_work_id(info.work_id)
        msc = MSC()
        # publisher out 发布方退出合约
        msc.i_want_out(info.current_eth, msc_record.msc_addr)

    def _out_all_msc_from_chain(self, info):
        msc_record = self.msc_orm.get_formal_by_work_id(info.work_id)
        work = self.work_orm.get_work_by_work_id(info.work_id)
        msc = MSC()
        # publisher out 退出合约
        msc.i_want_out(info.current_eth, msc_record.msc_addr)
        # value = 1 if info.current_eth == info.publisher_eth else 0
        msc.send(info.participants_eth, work.work_excitation-1, info.publisher_eth, msc_record.msc_addr)
        msc.withdraw(info.publisher_eth, msc_record.msc_addr)
        msc.withdraw(info.participants_eth, msc_record.msc_addr)
        Operation.create_operation(work.participants, '收取激励', '收到%s工作的激励%dM Token' % (work.work_name, work.work_excitation), 'Receive incentives from %s %d M Token' % (work.work_name, work.work_excitation))

    # def _out_promise_from_chain(self, info):
    #     msc = MSC()
    #     work = self.work_orm.get_work_by_work_id(info.work_id)
    #     print(work.publisher)
    #     print(work.participants)
    #     msc_record = self.msc_orm.get_formal_by_work_id(info.work_id)
    #     if not msc_record:
    #         msc_record = self.msc_orm.get_effective_promise(work.participants, work.publisher)
    #         msc.i_want_out(info.publisher_eth, msc_record.msc_addr)
    #         msc.i_want_out(info.participants_eth, msc_record.msc_addr)
    #         msc.withdraw(info.publisher_eth, msc_record.msc_addr)
    #         msc.withdraw(info.participants_eth, msc_record.msc_addr)
    #         msc_record.is_effective = 0
    #         msc_record.utime = datetime.datetime.now()
    #         msc_record.save()

    def _fresh_msc_state(self, info):
        msc_record = self.msc_orm.get_formal_by_work_id(info.work_id)
        msc_record.is_effective = 0
        msc_record.utime = datetime.datetime.now()
        return msc_record

    def _fresh_work_state(self, info):
        work = self.work_orm.get_work_by_work_id(info.work_id)
        if work.work_status == 3:
            if info.current_eth == info.publisher_eth:
                work.work_status = 5
            else:
                work.work_status = 4
        elif work.work_status == 4 or work.work_status == 5:
            work.work_status = 6

        work.utime = datetime.datetime.now()
        return work

    def _store(self, iterable):
        for item in iterable:
            try:
                self.db.session.add(item)
            except Exception:
                self.db.session.rollback()
                raise PersistenceError
        self.db.session.commit()

