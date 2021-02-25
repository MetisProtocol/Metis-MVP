# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: view.py
@time: 2020/5/26 3:59 下午
@desc:
"""
import os
import json
from . import impl
from flask import Blueprint, request
from flask.views import MethodView
from metis.utils.helpers import register_view, render, stand_response
from .model import Eth
from .contracts import MToken


class GenerateEthRecord(MethodView):

    def __init__(self, service_factory):
        self.service_factory = service_factory

    def get(self):
        source = list()
        file_path = os.path.join(
            os.path.dirname(__file__), 'keys.text'
        )
        with open(file_path, 'r') as fd:
            for line in fd.readlines():
                source.append(tuple(line.strip('\n').split(',')))
            print(source)
        res = self._gen(source)
        self._store(res)
        return json.dumps(self._gen(source))
        # token = MToken()
        # eths = Eth.query.all()
        # a = []
        # i = 1
        # for eth in eths:
        #     balance = token.get_balance(eth.public_key)
        #     a.append((i, balance))
        #     i += 1
        # return json.dumps(a)



    @staticmethod
    def _gen(args):
        res = []
        for item in args:
            public_key, private_key = item
            res.append(
                {
                    "public_key": public_key,
                    "private_key": private_key
                }
            )
        return res

    @staticmethod
    def _store(args):
        for item in args:
            public_key = item['public_key']
            private_key = item['private_key']
            if not Eth.is_exists(public_key):
                eth = Eth(public_key, private_key)
                eth.save()



@impl
def load_blueprints(app):
    eth = Blueprint("eth", __name__)

    register_view(
        eth,
        routes=['/gen'],
        view_func=GenerateEthRecord.as_view(
            "gen",
            service_factory=""
        )
    )
    app.register_blueprint(eth, url_prefix="/eth")



