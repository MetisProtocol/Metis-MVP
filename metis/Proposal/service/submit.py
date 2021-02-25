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
from metis.Account.model import Account
from metis.MetisExecption.MetisError import ValidationError, StopValidation, PersistenceError
from metis.CommonService.common_validators import ValidatorsMeta
from metis.SmartContract.contracts import TaskList
from metis.Proposal.model import Operation
from metis.Wiki import Wiki


@attr.s(repr=True, hash=True, cmp=False, frozen=True)
class SubmitProposalInfo:
    work_id = attr.ib()
    # content = attr.ib()
    current_eth = attr.ib()


class SubmitService:
    def __init__(self, plugins, work_orm, db):
        self.plugins = plugins
        self.work_orm = work_orm
        self.db = db

    def submit(self, info):
        try:
            self._validate_submit_info(info)
            # 将结果提交到链上 TASKLIST合约
            self._finish_work_to_block_chain(info)
            # 将任务结果提交到wiki
            # self._edit_wiki(info)
            # 改变该任务的状态为待审核  修改work表
            work = self._store_work(info)
            self._persistence([work])
        except Exception:
            raise

    def _finish_work_to_block_chain(self, info):
        task = TaskList()
        work = self.work_orm.get_work_by_work_id(info.work_id)
        Operation.create_operation(current_user.uid, '工作提交', '提交%s' % work.work_name, 'Submit %s' % work.work_name)
        publisher = Account.get_user_by_uid(work.publisher)
        task_index = task.get_task_index(publisher.eth_addr, work.work_describe)
        print(publisher.eth_addr, work.work_describe, info.current_eth)
        print("=====================")
        print(task_index)
        task.finish_task(publisher.eth_addr, task_index, work.work_describe, info.current_eth)

    def _validate_submit_info(self, info):
        validators = self.plugins.hook.metis_proposal_gather_submit_work_validators()
        failures = list()

        for validator in chain.from_iterable(validators):
            try:
                validator(info)
            except ValidationError as e:
                failures.append(e.reason)
        if failures:
            raise StopValidation(failures)

    def _edit_wiki(self, info):
        work = self.work_orm.get_work_by_work_id(info.work_id)
        wiki = Wiki()
        wiki.edit(work.work_name, info.content)

    def _store_work(self, info):
        work = self.work_orm.get_work_by_work_id(info.work_id)
        work.work_status = 2
        work.utime = datetime.datetime.now()
        return work

    def _create_wiki(self, info):
        pass

    def _persistence(self, iterable):
        for item in iterable:
            try:
                self.db.session.add(item)
            except Exception:
                self.db.session.rollback()
                raise PersistenceError
        self.db.session.commit()

