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
from metis.config.Const import ACCOUNT_START
from metis.CommonService import ValidatorsMeta
from metis.MetisExecption.MetisError import ValidationError, PersistenceError, StopValidation, EthError
from itertools import chain
from metis.SmartContract.contracts import MToken, MSC
from metis.Proposal.model import Operation

logger = logging.getLogger("metis")


@attr.s(repr=True, cmp=False, frozen=True, hash=True)
class AddKnowledgeJoinInfo:
    knowledge_detail_id = attr.ib()
    balance = attr.ib()
    user_eth = attr.ib()


class BalanceKnowledgeValidator(ValidatorsMeta):
    """
    验证该用户余额是否足够激活该工作
    """

    def validate(self, info):
        if int(info.balance) - 100 < 0:
            raise StopValidation('账户余额不足')


class AddKnowledgeJoinService:
    def __init__(self, plugins, orm, db):
        self.plugins = plugins
        self.orm = orm
        self.db = db

    def join_knowledge(self, knowledge_info, join_type):
        knowledge = self.orm.get_knowledge_detail_by_id(knowledge_info.knowledge_detail_id)
        try:
            self._validate_info(knowledge_info)
            self._deploy_tmp_msc(knowledge_info, knowledge, join_type)
            pass
        except StopValidation:
            raise
        knowledge = self._store_knowledge(knowledge, join_type)  # 存储该任务到mysql
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

    def _store_knowledge(self, knowledge, join_type):
        if join_type == 'join':
            joiner = json.loads(knowledge.knowledge_detail_joiner)
            joiner.append(current_user.uid)
            knowledge.knowledge_detail_joiner = json.dumps(joiner)
            Operation.create_operation(current_user.uid, '参与讨论', '参与%s的知识条目讨论，质押100 M Token' % knowledge.knowledge_detail_name, 'Participate in the discussion， stake 100 M Token')
        else:
            knowledge.knowledge_detail_writer = current_user.uid
            Operation.create_operation(current_user.uid, '参与记录', '参与%s的知识条目记录，质押100 M Token' % knowledge.knowledge_detail_name, 'Participate in the consolidate， stake 100 M Token')
        knowledge.save()
        return knowledge

    def _deploy_tmp_msc(self, knowledge_info, knowledge, join_type):
        balance = json.loads(knowledge.knowledge_detail_writer_balance)['pledge'] if join_type == 'writer' \
            else json.loads(knowledge.knowledge_detail_joiner_balance)['pledge']
        # M Token合约 关于货币合约
        token = MToken()
        # 质押合约
        msc = MSC()
        # deploy msc
        msc_addr = msc.deploy_msc([knowledge_info.user_eth, ACCOUNT_START], 0)
        # msc_addr 部署合约的地址
        # transfer excitation to this msc 将质押金从账户中扣出
        token.transfer(msc_addr, balance, knowledge_info.user_eth)
        # sys account active this contract 质押第三方
        token.transfer(msc_addr, 0, ACCOUNT_START)
        return msc_addr
