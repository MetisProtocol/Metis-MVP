# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: spec.py
@time: 2020/5/8 12:34 下午
@desc:
"""
from pluggy import HookspecMarker

spec = HookspecMarker("metis")


@spec
def load_blueprints(app):
    """Hook for registering blueprints"""


@spec
def metis_generate_dac_validators():
    """ Hook for gathering user registration validators """


@spec
def metis_generate_dac_post_processor(dac_info):
    """Hook for registration post process"""


@spec
def metis_dac_gather_sign_validators():
    """
        Hook for gathering user sign validators
    """


@spec
def metis_account_gather_registration_validators():
    """

    :return:
    """


@spec
def metis_account_registration_post_processor(info):
    """

    :param info:
    :return:
    """


@spec
def metis_proposal_gather_add_work_validators():
    """

    :return:
    """


@spec
def metis_proposal_gather_claim_excitation_validators():
    """

    :return:
    """


@spec
def metis_proposal_gather_first_claim_promise_validators():
    """

    :return:
    """


@spec
def metis_proposal_gather_claim_promise_validators():
    """

    :return:
    """


@spec
def metis_proposal_gather_publisher_claim_promise_validators():
    """

    :return:
    """

