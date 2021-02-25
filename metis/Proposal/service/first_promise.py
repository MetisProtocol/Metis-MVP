# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: first_promise.py
@time: 2020/6/4 10:49 下午
@desc:
"""
import attr
import datetime
import logging
from flask_login import current_user
from itertools import chain
from metis.MetisExecption.MetisError import StopValidation, ValidationError, PersistenceError
from metis.SmartContract.contracts import MSC
from metis.SmartContract.contracts import MToken, TaskList
from metis.Proposal.model import Operation

logger = logging.getLogger("metis")


@attr.s(hash=True, repr=True, cmp=False, frozen=True)
class FirstPromiseInfo:
    work_id = attr.ib()
    current_user_uid = attr.ib()
    current_user_eth = attr.ib()
    balance = attr.ib()
    publisher_uid = attr.ib()
    publisher_eth = attr.ib()


class FirstPromiseClaimService:

    def __init__(self, plugins, msc_orm, work_orm, db):
        self.plugins = plugins
        self.msc_orm = msc_orm
        self.work_orm = work_orm
        self.db = db

    def claim(self, info):
        try:
            self._validate_first_promise(info)
            # 建立双方第一次合作的合约
            msc_addr = self._deploy_msc(info)
            # 质押10M Token保证金（扣除）
            # 走TASK合约
            self._take_task(info)
            self._transfer_token_to_msc(msc_addr, info)
            work = self._fresh_work_state(info)
            # 数据库中建立双方第一次合作的关系
            msc = self._store_msc(info, msc_addr)
            self._persistence([msc, work])
        except Exception:
            raise
        return msc

    def _validate_first_promise(self, info):
        validators = self.plugins.hook.metis_proposal_gather_first_claim_promise_validators()
        failures = []

        for validator in chain.from_iterable(validators):
            try:
                validator(info)
            except ValidationError as e:
                failures.append(e.reason)

        if failures:
            raise StopValidation(failures)

    def _deploy_msc(self, info):
        msc = MSC()
        msc_addr = msc.deploy_msc([info.current_user_eth, info.publisher_eth], 10)  # eth addr
        return msc_addr

    def _transfer_token_to_msc(self, msc_addr, info):
        token = MToken()
        tx = token.transfer(msc_addr, 10, info.current_user_eth, value=1)
        token.web3.eth.waitForTransactionReceipt(tx)
        Operation.create_operation(current_user.uid, '质押', '质押 10M Token与发布方建立第一次合作关系', 'First time to work with publisher, stake 10 M Token')

    def _take_task(self, info):
        print("第一次查询TASTLIST")
        task = TaskList()
        work = self.work_orm.get_work_by_work_id(info.work_id)
        task_index = task.get_task_index(info.publisher_eth, work.work_describe)
        task.take_task(info.publisher_eth, task_index, info.current_user_eth)

    def _fresh_work_state(self, info):
        work = self.work_orm.get_work_by_work_id(info.work_id)
        work.work_status = 1
        work.utime = datetime.datetime.now()
        work.participants = info.current_user_uid
        return work

    def _store_msc(self, info, msc_addr):
        msc = self.msc_orm(
            msc_type="PROMISE",
            party_a=info.current_user_uid,
            work_id=info.work_id,   # uid
            msc_addr=msc_addr,
            party_b=info.publisher_uid  # uid
        )
        return msc

    def _persistence(self, iterable):
        for item in iterable:
            try:
                self.db.session.add(item)
            except Exception:
                logger.error("Persistence Error")
                self.db.session.rollback()
                raise PersistenceError
        self.db.session.commit()



