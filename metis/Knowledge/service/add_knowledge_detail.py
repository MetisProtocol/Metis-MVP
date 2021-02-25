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
import json
from flask_login import current_user
from metis.CommonService import ValidatorsMeta
from metis.MetisExecption.MetisError import ValidationError, PersistenceError, StopValidation, EthError
from itertools import chain
from metis.SmartContract.contracts import MToken, MSC
from metis.Proposal.model import Operation
from metis.config.Const import ACCOUNT_START

logger = logging.getLogger("metis")


@attr.s(repr=True, cmp=False, frozen=True, hash=True)
class AddKnowledgeDetailInfo:
    knowledge_id = attr.ib()
    knowledge_name = attr.ib()
    knowledge_describe = attr.ib()
    belongs = attr.ib()
    user_eth = attr.ib()
    knowledge_detail_writer_balance = attr.ib()
    knowledge_detail_joiner_balance = attr.ib()
    knowledge_detail_writer_excitation = attr.ib()
    knowledge_detail_joiner_excitation = attr.ib()
    balance = attr.ib()


class BalanceKnowledgeValidator(ValidatorsMeta):
    """
    验证该用户余额是否足够激活该工作
    """

    def validate(self, info):
        if int(info.balance) - 100 < 0:
            raise StopValidation('账户余额不足')


class AddKnowledgeDetailService:
    def __init__(self, plugins, orm, db):
        self.plugins = plugins
        self.orm = orm
        self.db = db

    def add_knowledge_detail(self, knowledge_info, knowledge_id):
        try:
            self._validate_info(knowledge_info)
            self._deploy_tmp_msc(knowledge_info)
            pass
        except StopValidation:
            raise
        knowledge = self._store_knowledge(knowledge_info, knowledge_id)  # 存储该任务到mysql
        Operation.create_operation(current_user.uid, '增加知识条目', '增加新的知识分类，质押100 M Token', 'Create new knowledge category, stake 100 M Token')
        return knowledge

    def _validate_info(self, knowledge_info):
        validators = self.plugins.hook.metis_knowledge_gather_add_knowledge_validators()
        failures = list()

        for validator in chain.from_iterable(validators):
            try:
                validator(knowledge_info)
            except ValidationError as e:
                failures.append(e.reason)

        if failures:
            raise StopValidation(failures)

    def _store_knowledge(self, knowledge_info, knowledge_id):
        knowledge = self.orm(
            knowledge_id,
            knowledge_info.knowledge_name,
            knowledge_info.belongs,
            json.dumps({'excitation': knowledge_info.knowledge_detail_writer_excitation,
                        'pledge': knowledge_info.knowledge_detail_writer_balance}),
            json.dumps({'excitation': knowledge_info.knowledge_detail_joiner_excitation,
                        'pledge': knowledge_info.knowledge_detail_joiner_balance})
        )
        knowledge.knowledge_describe = knowledge_info.knowledge_describe
        knowledge.save()
        return knowledge

    def _deploy_tmp_msc(self, knowledge_info):
        # M Token合约 关于货币合约
        token = MToken()
        # 质押合约
        msc = MSC()
        # deploy msc
        msc_addr = msc.deploy_msc([knowledge_info.user_eth, ACCOUNT_START], 0)
        # msc_addr 部署合约的地址
        # transfer excitation to this msc 将质押金从账户中扣出
        token.transfer(msc_addr, 100, knowledge_info.user_eth)
        # sys account active this contract 质押第三方
        token.transfer(msc_addr, 0, ACCOUNT_START)
        return msc_addr
