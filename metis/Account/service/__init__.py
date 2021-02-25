# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: __init__.py.py
@time: 2020/5/25 10:29 上午
@desc:
"""
from abc import ABC, abstractmethod


class ValidatorBase(ABC):
    """
    User info validator abstract cls
    """

    @abstractmethod
    def validate(self, info):
        """

        :param info:
        :return:
        """

    def __call__(self, info):
        return self.validate(info)


