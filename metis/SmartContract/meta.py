# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: meta.py
@time: 2020/5/14 9:43 上午
@desc: Base Class
"""
import json
import os
from web3 import Web3
from metis.config.Const import (DEBUG_WEB3_PROVIDER_SCHEME, DEBUG_WEB3_PROVIDER_HOST, DEBUG_WEB3_PROVIDER_PORT)
from metis.config.Const import (PRODUCTION_WEB3_PROVIDER_SCHEME, PRODUCTION_WEB3_PROVIDER_HOST,
                                PRODUCTION_WEB3_PROVIDER_PORT, PRIVATE_KEYS)


class SmartContractMeta:

    ABI_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'abi/')

    # DEBUG ENV
    DEBUG_SCHEME = DEBUG_WEB3_PROVIDER_SCHEME
    DEBUG_HOST = DEBUG_WEB3_PROVIDER_HOST
    DEBUG_PORT = DEBUG_WEB3_PROVIDER_PORT

    # PRODUCTION ENV
    PRODUCTION_SCHEME = PRODUCTION_WEB3_PROVIDER_SCHEME
    PRODUCTION_HOST = PRODUCTION_WEB3_PROVIDER_HOST
    PRODUCTION_PORT = PRODUCTION_WEB3_PROVIDER_PORT

    def __init__(self):
        self.web3 = None
        self.abi = None
        self.contract = None
        self.contract_addr = None
        self.private_keys = PRIVATE_KEYS

    def _load_abi_as_json(self, abi_file):
        with open(self.ABI_DIR + abi_file, 'r') as fd:
            return json.load(fd)

    def initialize(self, abi_file, contract_addr, env="DEBUG"):
        if env == "PRODUCTION":
            self.web3 = Web3(
                # Web3.HTTPProvider(f"{self.PRODUCTION_SCHEME}://{self.PRODUCTION_HOST}")
                Web3.HTTPProvider(f"{self.PRODUCTION_SCHEME}://{self.PRODUCTION_HOST}:{self.PRODUCTION_PORT}")
            )
        else:
            self.web3 = Web3(Web3.HTTPProvider(f"{self.DEBUG_SCHEME}://{self.DEBUG_HOST}:{self.DEBUG_PORT}"))
            # self.web3 = Web3(Web3.HTTPProvider(f"{self.PRODUCTION_SCHEME}://{self.DEBUG_HOST}"))
        self.abi = self._load_abi_as_json(abi_file)
        self.contract_addr = self.web3.toChecksumAddress(contract_addr)
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.contract_addr)

    @classmethod
    def _convert_accuracy(cls, number, accuracy=18):
        return number * 10 ** accuracy

    @classmethod
    def _convert_to_hum_accuracy(cls, number, accuracy=18):
        print(number)
        print("11111111111111111111")
        return number / (10 ** accuracy)
    
    def get_signed_txn(self, account, value=0):
        return dict(
            nonce=self.web3.eth.getTransactionCount(account) + value,
            gasPrice=31000,
            gas=5000000,
            value=0,
            private_key=self.private_keys.get(account, '')
        )


if __name__ == '__main__':
    ts = SmartContractMeta()
    ts.initialize("task_list_abi.json", "0x9ED1a06357db2Af77af0B25e0e38C3C0Bba1AE48")








