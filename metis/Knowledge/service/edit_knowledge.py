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
class AddKnowledgeEditInfo:
    knowledge_detail_id = attr.ib()
    knowledge_info_belongs = attr.ib()
    knowledge_info_type = attr.ib()
    knowledge_info_memo = attr.ib()


class AddKnowledgeEditService:
    def __init__(self, plugins, orm, db):
        self.plugins = plugins
        self.orm = orm
        self.db = db

    def edit_knowledge(self, knowledge_info):
        knowledge = self._store_knowledge(knowledge_info)  # 存储该任务到mysql
        return knowledge

    def _store_knowledge(self, knowledge_info):
        knowledge = self.orm.get_knowledge_info_writer_by_knowledge(knowledge_info.knowledge_detail_id)
        if knowledge_info.knowledge_info_type == 'writer' and knowledge:
            knowledge.knowledge_info_memo = knowledge_info.knowledge_info_memo
            knowledge.ctime = datetime.datetime.now()
        else:
            knowledge = self.orm(
                knowledge_info.knowledge_detail_id,
                knowledge_info.knowledge_info_belongs,
                knowledge_info.knowledge_info_type,
                knowledge_info.knowledge_info_memo
            )
        knowledge.save()
        return knowledge

