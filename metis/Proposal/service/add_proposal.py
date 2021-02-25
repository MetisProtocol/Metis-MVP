# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: addProposal.py
@time: 2020/6/1 12:23 下午
@desc:
"""
import re
import logging
import attr
from flask_login import current_user
from metis.CommonService import ValidatorsMeta
from metis.MetisExecption.MetisError import ValidationError, PersistenceError, StopValidation, EthError
from itertools import chain
from metis.Home.model import DAC
from metis.SmartContract.contracts import TaskList
from metis.Wiki import Wiki
from metis.Proposal.model import Work, Operation, WorkInfo

logger = logging.getLogger("metis")


@attr.s(repr=True, cmp=False, frozen=True, hash=True)
class AddProposalInfo:
    dac_id = attr.ib()
    work_name = attr.ib()
    work_describe = attr.ib()
    work_deadline = attr.ib()
    work_expiry = attr.ib()
    work_excitation = attr.ib()
    publisher_uid = attr.ib()


class WorkDACValidator(ValidatorsMeta):

    def validate(self, info):
        dac = DAC.get_dac_by_id(dac_id=info.dac_id)
        if not dac:
            raise ValidationError("DAC", "DAC不存在")


class WorkUniquenessValidator(ValidatorsMeta):

    def validate(self, info):
        if Work.is_exists(info.dac_id, info.work_name):
            raise ValidationError("Work", "该工作名已存在")


class WorkDescribeUriValidator(ValidatorsMeta):
    PATTERN = re.compile(r"^((https|http|ftp|rtsp|mms)?:\/\/)[^\s]+")

    def validate(self, info):
        if not re.match(self.PATTERN, info.work_describe):
            raise ValidationError("work_desc_uri", "描述wiki url格式错误")


class WorkExcitationValidator(ValidatorsMeta):

    def validate(self, info):
        if info.work_excitation < 0:
            raise ValidationError("excitation", "激励数量不能小于0")


class WorkExpiryValidator(ValidatorsMeta):

    def validate(self, info):
        if info.work_expiry < 0:
            raise ValidationError("expiry", "预计天数不能小于0")


class AddProposalService:

    def __init__(self, plugins, orm, db):
        self.plugins = plugins
        self.orm = orm
        self.db = db

    def add(self, work_info, account):
        try:
            self._validate_add_info(work_info)  # 验证提交的信息
            # self._publish_work_to_block_chain(account, work_info)
            Operation.create_operation(current_user.uid, "发布任务", "发布%s, 质押%dM Token作为激励" % (work_info.work_name, work_info.work_excitation), "Create %s, stake %dM Token as incentives" % (work_info.work_name, work_info.work_excitation))
        except StopValidation:
            raise
        self._create_wiki(work_info)    # 生成wiki模板
        work = self._store_work(work_info)  # 存储该任务到mysql
        return work

    def _validate_add_info(self, work_info):
        validators = self.plugins.hook.metis_proposal_gather_add_work_validators()
        failures = list()

        for validator in chain.from_iterable(validators):
            try:
                validator(work_info)
            except ValidationError as e:
                failures.append(e.reason)
        if failures:
            raise StopValidation(failures)

    def _create_wiki(self, work_info):
        wiki = Wiki()
        wiki.create(work_info.work_name)

    def _publish_work_to_block_chain(self, account, work_info):
        task = TaskList()
        task.web3.eth.defaultAccount = account.eth_addr
        task.add_task(
            work_info.work_describe,
            work_info.work_expiry,
            work_info.work_excitation,
            "0x0000000000000000000000000000000000000000",
            account.eth_addr,
        )
        print("添加到TASTLIST中")

    def _store_work(self, work_info):
        print("---------------------------")
        print(work_info.work_name)
        print(work_info.work_describe)
        print(work_info.work_expiry)
        print(work_info.work_excitation)
        print(work_info.dac_id)
        print(work_info.publisher_uid)
        print("---------------------------")
        print("将数据存储到WORK库中")
        work = self.orm(
            work_info.work_name,
            work_info.work_describe,
            work_info.work_expiry,
            work_info.work_deadline,
            work_info.work_excitation,
            work_info.dac_id,
            work_info.publisher_uid
        )
        work_info = WorkInfo(work.work_id)
        work.save()
        work_info.save()
        return work



