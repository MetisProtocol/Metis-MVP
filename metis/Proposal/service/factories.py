# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: factories.py
@time: 2020/6/1 12:23 下午
@desc:
"""
from ..service.add_proposal import AddProposalService
from ..service.claim_excitation import ClaimExcitationService
from ..service.claim_promise import ClaimPromiseService
from ..service.first_promise import FirstPromiseClaimService
from ..service.publisher_claim_promise import PublisherClaimPromiseService
from ..service.review import ReviewService
from ..service.submit import SubmitService
from ..service.settlement import SettlementService
from ..model import Work
from metis.SmartContract.model import MSCTable
from flask import current_app
from metis.extensions import db
from metis.SmartContract.model import MSCTable


def add_work_service_factory():
    return AddProposalService(current_app.pluggy, Work, db)


def claim_excitation_service_factory():
    return ClaimExcitationService(current_app.pluggy, Work, MSCTable, db)


def claim_promise_service_factory():
    return ClaimPromiseService(current_app.pluggy, MSCTable, Work, db)


def first_promise_service_factory():
    return FirstPromiseClaimService(current_app.pluggy, MSCTable, Work, db)


def publisher_claim_promise_service_factory():
    return PublisherClaimPromiseService(current_app.pluggy, MSCTable, db)


def submit_service_factory():
    return SubmitService(current_app.pluggy, Work, db)


def review_service_factory():
    return ReviewService(current_app.pluggy, Work, db)


def settlement_service_factory():
    return SettlementService(current_app.pluggy, Work, MSCTable, db)
