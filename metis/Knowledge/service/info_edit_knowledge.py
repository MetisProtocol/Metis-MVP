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
import datetime
import json
from flask_login import current_user
from metis.CommonService import ValidatorsMeta
from metis.MetisExecption.MetisError import ValidationError, PersistenceError, StopValidation, EthError
from itertools import chain
from metis.SmartContract.contracts import MToken, MSC

logger = logging.getLogger("metis")


@attr.s(repr=True, cmp=False, frozen=True, hash=True)
class AddKnowledgeInfoEditInfo:
    knowledge_detail_name = attr.ib()
    knowledge_describe = attr.ib()
    knowledge_detail_writer_pledge = attr.ib()
    knowledge_detail_joiner_pledge = attr.ib()
    knowledge_detail_writer_excitation = attr.ib()
    knowledge_detail_joiner_excitation = attr.ib()


class KnowledgeInfoEditService:
    def __init__(self, plugins, orm, db):
        self.plugins = plugins
        self.orm = orm
        self.db = db

    def edit_knowledge_info(self, knowledge_info, knowledge_detail_id):
        knowledge = self._store_knowledge(knowledge_info, knowledge_detail_id)  # 存储该任务到mysql
        return knowledge

    def _store_knowledge(self, knowledge_info, knowledge_detail_id):
        knowledge = self.orm.get_knowledge_detail_by_id(knowledge_detail_id)
        if knowledge:
            knowledge.knowledge_detail_name = knowledge_info.knowledge_detail_name
            knowledge.knowledge_describe = knowledge_info.knowledge_describe
            writer_balance = json.loads(knowledge.knowledge_detail_writer_balance)
            writer_balance['excitation'] = knowledge_info.knowledge_detail_writer_excitation
            writer_balance['pledge'] = knowledge_info.knowledge_detail_writer_pledge
            knowledge.knowledge_detail_writer_balance = json.dumps(writer_balance)
            joiner_balance = json.loads(knowledge.knowledge_detail_joiner_balance)
            joiner_balance['excitation'] = knowledge_info.knowledge_detail_joiner_excitation
            joiner_balance['pledge'] = knowledge_info.knowledge_detail_joiner_pledge
            knowledge.knowledge_detail_joiner_balance = json.dumps(joiner_balance)

        knowledge.save()
        return knowledge

