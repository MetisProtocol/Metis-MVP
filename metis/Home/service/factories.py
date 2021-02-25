# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: factories.py
@time: 2020/5/19 3:04 下午
@desc:
"""
from .registration import GenerateDACService
from .join_to_dac import JoinToDAC
from metis.extensions import db
from flask import current_app
from ..model import DAC


def metis_dac_generate_service_factory():
    return GenerateDACService(current_app.pluggy, DAC, db)


def metis_join_to_dac_service_factory():
    return JoinToDAC(current_app.pluggy, DAC, db)

