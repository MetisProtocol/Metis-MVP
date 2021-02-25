# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: __init__.py.py
@time: 2020/5/26 9:45 上午
@desc:
"""
from abc import ABC, abstractmethod


class ValidatorsMeta(ABC):
    """
    common validator abstract cls
    """

    @abstractmethod
    def validate(self, info):
        """
        validate info
        :param info:
        :return:
        """

    def __call__(self, info):
        return self.validate(info)


class ProcessorMeta(ABC):
    """
    common processor abstract cls
    """
    @abstractmethod
    def post_process(self, user):
        pass

    def __call__(self, user):
        return self.post_process(user)



