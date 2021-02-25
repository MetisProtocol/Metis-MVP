# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: __init__.py.py
@time: 2020/5/19 2:58 下午
@desc:
"""
from abc import ABC, abstractmethod


class ValidatorBase(ABC):

    @abstractmethod
    def validate(self, dac_info):
        """

        :param dac_info:
        :return:
        """

    def __call__(self, dac_info):
        return self.validate(dac_info)


class PostProcessorBase(ABC):

    @abstractmethod
    def post_process(self, info):
        """
        :param info:
        :return:
        """

    def __call__(self, info):
        return self.post_process(info)

