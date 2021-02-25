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
from metis.SmartContract.contracts import TaskList
from metis.Proposal.model import Operation


@attr.s(repr=True, hash=True, cmp=False, frozen=True)
class ReviewProposalInfo:
    work_id = attr.ib()
    publisher_eth = attr.ib()


class ReviewService:
    def __init__(self, plugins, work_orm, db):
        self.plugins = plugins
        self.work_orm = work_orm
        self.db = db

    def review(self, info):
        try:
            self._validate_promise_claim(info)
            self._review_push_task_list_chain(info)
            work = self._fresh_work_state(info)
            self._store([work])
        except Exception:
            raise
        return work
        # 告诉TASK_LIST 审核工作结果
        # 告诉MSC合约 解除双方合作关系 检查双方是否还有合作 如果没有则解除双方用作质押的首次建立的合约并返回M TOKEN
        # 转账将任务的激励发放到接任务方
        # 如果解除则上方返还用作建立合作关系的质押Token
        # 修改msc表中is_effective 为无效 如解除关系则PROMISE设置为无效
        # 修改work表中标记状态已完成

    def _validate_promise_claim(self, info):
        validators = self.plugins.hook.metis_proposal_gather_review_work_validators()
        failures = []

        for validator in chain.from_iterable(validators):
            try:
                validator(info)
            except ValidationError as e:
                failures.append(e.reason)

        if failures:
            raise StopValidation(failures)

    def _review_push_task_list_chain(self, info):
        task = TaskList()
        work = self.work_orm.get_work_by_work_id(info.work_id)
        task_index = task.get_task_index(info.publisher_eth, work.work_describe)
        task.review_task(task_index, True, info.publisher_eth)

    def _fresh_work_state(self, info):
        work = self.work_orm.get_work_by_work_id(info.work_id)
        Operation.create_operation(current_user.uid, '工作审批', '审核通过%s' % work.work_name, 'Approve %s' % work.work_name)
        work.work_status = 3
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
