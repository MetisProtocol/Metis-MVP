# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: Debug.py
@time: 2020/5/8 10:32 上午
@desc:
"""
from metis.config.Default import DefaultConfig
from metis.config.Const import (DATABASE_SCHEME, DEBUG_DATABASE_HOST, DEBUG_DATABASE_NAME, DEBUG_DATABASE_PASSWORD,
                                DEBUG_DATABASE_PORT, DEBUG_DATABASE_USERNAME)


class DebugConfig(DefaultConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_SCHEME}://{DEBUG_DATABASE_USERNAME}:{DEBUG_DATABASE_PASSWORD}@" \
                              f"{DEBUG_DATABASE_HOST}:{DEBUG_DATABASE_PORT}/{DEBUG_DATABASE_NAME}"

