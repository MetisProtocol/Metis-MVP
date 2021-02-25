# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: factories.py
@time: 2020/6/1 12:23 下午
@desc:
"""
from ..service.add_knowledge import AddKnowledgeService
from ..service.add_knowledge_detail import AddKnowledgeDetailService
from ..service.join_knowledge import AddKnowledgeJoinService
from ..service.edit_knowledge import AddKnowledgeEditService
from ..service.info_edit_knowledge import KnowledgeInfoEditService
from ..model import Knowledge, KnowledgeDetail, KnowledgeInfo
from flask import current_app
from metis.extensions import db
from metis.SmartContract.model import MSCTable


def add_knowledge_service_factory():
    return AddKnowledgeService(current_app.pluggy, Knowledge, db)


def add_knowledge_detail_service_factory():
    return AddKnowledgeDetailService(current_app.pluggy, KnowledgeDetail, db)


def join_knowledge_service_factory():
    return AddKnowledgeJoinService(current_app.pluggy, KnowledgeDetail, db)


def edit_knowledge_service_factory():
    return AddKnowledgeEditService(current_app.pluggy, KnowledgeInfo, db)


def info_edit_knowledge_service_factory():
    return KnowledgeInfoEditService(current_app.pluggy, KnowledgeDetail, db)


# def claim_excitation_service_factory():
#     return ClaimExcitationService(current_app.pluggy, Work, MSCTable, db)
#
#
# def claim_promise_service_factory():
#     return ClaimPromiseService(current_app.pluggy, MSCTable, Work, db)
#
#
# def first_promise_service_factory():
#     return FirstPromiseClaimService(current_app.pluggy, MSCTable, Work, db)
#
#
# def publisher_claim_promise_service_factory():
#     return PublisherClaimPromiseService(current_app.pluggy, MSCTable, db)
#
#
# def submit_service_factory():
#     return SubmitService(current_app.pluggy, Work, db)
#
#
# def review_service_factory():
#     return ReviewService(current_app.pluggy, Work, db)
#
#
# def settlement_service_factory():
#     return SettlementService(current_app.pluggy, Work, MSCTable, db)
