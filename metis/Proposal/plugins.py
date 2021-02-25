# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: plugins.py
@time: 2020/6/1 1:04 下午
@desc:
"""
from . import impl
from metis.Home.model import DAC
from metis.Proposal.model import Work
from metis.SmartContract.model import MSCTable
from .service.add_proposal import (WorkDACValidator, WorkDescribeUriValidator,  WorkExcitationValidator,
                                   WorkExpiryValidator, WorkUniquenessValidator)
from .service.claim_excitation import (WorkEffectiveValidator, AdminRoleValidator, BalanceValidator)
from .service.claim_promise import ClaimPromiseBalanceValidator, FirstClaimPromiseValidator
from metis.Knowledge.service.add_knowledge import BalanceKnowledgeValidator


@impl
def metis_proposal_gather_add_work_validators():
    return [
        WorkUniquenessValidator(),
        WorkDACValidator(),
        WorkDescribeUriValidator(),
        WorkExpiryValidator(),
        WorkExcitationValidator()
    ]


@impl
def metis_proposal_gather_claim_excitation_validators():
    return [
        # 验证工作是否有效
        WorkEffectiveValidator(Work),
        AdminRoleValidator(DAC),
        BalanceValidator()
    ]


@impl
def metis_proposal_gather_first_claim_promise_validators():
    return [
        ClaimPromiseBalanceValidator()
    ]


@impl
def metis_proposal_gather_claim_promise_validators():
    return [
        # 验证工作是否有效
        WorkEffectiveValidator(Work),
        # 验证账户余额是否充足
        ClaimPromiseBalanceValidator(),
        # 验证双方是否第一次合作
        FirstClaimPromiseValidator(MSCTable)
    ]

@impl
def metis_proposal_gather_publisher_claim_promise_validators():
    return [
        ClaimPromiseBalanceValidator()
    ]


@impl
def metis_proposal_gather_submit_work_validators():
    return [
        WorkEffectiveValidator(Work)
    ]


@impl
def metis_proposal_gather_review_work_validators():
    return [
        WorkEffectiveValidator(Work)
    ]

@impl
def metis_proposal_gather_settlement_validators():
    return [
        WorkEffectiveValidator(Work)
    ]

@impl
def metis_knowledge_gather_add_knowledge_validators():
    """
    用作知识管理界面，将来移走
    :return:
    """
    return [
        BalanceKnowledgeValidator()
    ]
