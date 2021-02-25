# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: plugin.py
@time: 2020/5/19 2:59 下午
@desc:
"""
from metis.Home import impl
from .service.registration import DACNameUniquenessValidator


@impl
def metis_generate_dac_validators():
    return [
        DACNameUniquenessValidator()
    ]







