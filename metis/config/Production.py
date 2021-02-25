# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: Production.py
@time: 2020/5/8 10:33 上午
@desc:
"""
from metis.config.Default import DefaultConfig
from metis.config.Const import (DATABASE_SCHEME, PRODUCTION_DATABASE_HOST, PRODUCTION_DATABASE_NAME,
                                PRODUCTION_DATABASE_PASSWORD, PRODUCTION_DATABASE_PORT, PRODUCTION_DATABASE_USERNAME)


class ProductionConfig(DefaultConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_SCHEME}://{PRODUCTION_DATABASE_USERNAME}:{PRODUCTION_DATABASE_PASSWORD}" \
                              f"@{PRODUCTION_DATABASE_HOST}:{PRODUCTION_DATABASE_PORT}/{PRODUCTION_DATABASE_NAME}"

