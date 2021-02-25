# _*_ coding: utf-8 _*_

"""
@author: Liu
@file: test.py
@time: 2020/11/15 下午11:39
@desc:
"""
import os
import json
from web3 import Web3


class SmartContractMeta:

    ABI_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'abi/')

    def __init__(self):
        self.web3 = None
        self.abi = None
        self.contract = None
        self.contract_addr = None
        # self.private_keys = PRIVATE_KEYS

    def _load_abi_as_json(self, abi_file):
        with open(self.ABI_DIR + abi_file, 'r') as fd:
            return json.load(fd)

    def initialize(self, abi_file, contract_addr, env="DEBUG"):
        self.web3 = Web3(Web3.HTTPProvider("http://123.57.141.229:8080"))
        self.abi = self._load_abi_as_json(abi_file)
        self.contract_addr = self.web3.toChecksumAddress(contract_addr)
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.contract_addr)


class TaskList(SmartContractMeta):
    ROLE = ["NONE", "TASK_OWNER", "SERVICE", "ADMIN"]
    TASK_STATUS = ["NONE", "OPEN", "EXECUTING", "REVIEW", "REJECT", "DONE"]

    def __init__(self):
        super(TaskList, self).__init__()
        self.initialize('task_list_abi.json', "0xC89Ce4735882C9F0f0FE26686c53074E09B0D550")
        # self.private_keys = PRIVATE_KEYS

    def add_task(self, info_url, expiry, prize, delegate, sender):
        self.web3.eth.defaultAccount = sender
        try:
            res = self.contract.functions.addTask(info_url, expiry, prize, delegate).transact()
        except Exception:
            print("提交工作到区块链异常")
            raise
        return res

    def take_task(self, task_owner, task_index, sender):
        self.web3.eth.defaultAccount = sender
        try:
            print(task_owner, task_index, sender)
            res = self.contract.functions.takeTask(task_owner, task_index).transact()
        except Exception as e:
            print("从区块链获取任务异常%s" % e)
            raise
        return res

    def finish_task(self, task_owner, task_index, result_url, sender):
        self.web3.eth.defaultAccount = sender
        try:
            res = self.contract.functions.finshTask(task_owner, task_index, result_url).transact()
        except Exception:
            print("提交工作到区块链异常")
            raise
        return res

    def review_task(self, task_index, verdict, sender):
        self.web3.eth.defaultAccount = sender
        try:
            res = self.contract.functions.reviewTask(task_index, verdict).transact()
        except Exception:
            print("审核工作结果提交异常")
            raise
        return res

    def get_task_length_by_address(self, task_owner):
        # try:
        res = self.contract.functions.getNumTaskByAddress(task_owner).call()
        # except Exception:
        #     print("获取工作列表异常")
        #     raise
        return res

    def get_task(self, owner, index):
        try:
            res = self.contract.functions.tasklist(owner, index).call()
        except Exception:
            print("获取任务失败")
            raise
        return res

    def get_task_index(self, owner, info_uri):
        try:
            for index in range(self.get_task_length_by_address(owner)):
                task_content = self.get_task(owner, index)
                print(task_content)
                if task_content[0] == info_uri:
                    return index
        except Exception:
            print('获取任务索引失败')

    def _add_task_owner(self, account):
        # self.web3.eth.defaultAccount = ACCOUNT_START
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        try:
            res = self.contract.functions.addTaskOwner(self.web3.toChecksumAddress(account)).transact()
        except Exception:
            print("授权task owner异常")
            raise
        return res

    def get_signed_txn(self, account, value=0):
        return dict(
            nonce=self.web3.eth.getTransactionCount(account) + value,
            gasPrice=31000,
            gas=5000000,
            value=0,
            private_key="0xb0057716d5917badaf911b193b12b910811c1497b5bada8d7711f758981c3773"
        )

    def _add_service(self, account):
        # self.web3.eth.defaultAccount = ACCOUNT_START
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        try:
            res = self.contract.functions.addService(self.web3.toChecksumAddress(account)).transact()
        except Exception:
            print("授权task service异常")
            raise
        return res

class MToken(SmartContractMeta):
    # ACCOUNT_START = ACCOUNT_START

    def __init__(self):
        super(MToken, self).__init__()
        self.initialize('m_token_abi.json', '0xD833215cBcc3f914bD1C9ece3EE7BF8B14f841bb')

        # test env spec default account accounts[0]
        # self.web3.eth.accounts.create()
        # self.web3.eth.accounts[0] = "0xc27E363E8865c58992C808C020d258B319A4c8e8"
        print(type(self.web3.eth.accounts))
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]

    def transfer(self, to, amount, sender=None, private_key="0xb0057716d5917badaf911b193b12b910811c1497b5bada8d7711f758981c3773", value=0):
        amount = self._convert_accuracy(amount)
        if sender:
            self.web3.eth.defaultAccount = sender
        # tx_hash = self.contract.functions.transfer(to, amount).transact(self.get_signed_txn(sender))
        return self.contract.functions.transfer(to, amount).transact()

    @classmethod
    def _convert_accuracy(cls, number, accuracy=18):
        return number * 10 ** accuracy

if __name__ == '__main__':
    token = MToken()
    task = TaskList()
    # token.transfer('0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0xd03ea8624C8C5987235048901fB614fDcA89b117', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x95cED938F7991cd0dFcb48F0a06a40FA1aF46EBC', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0xACa94ef8bD5ffEE41947b4585a84BdA5a3d3DA6E', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x28a8746e75304c0780E011BEd21C72cD78cd535E', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x610Bb1573d1046FCb8A70Bbbd395754cD57C2b60', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x855FA758c77D68a04990E992aA4dcdeF899F654A', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0xfA2435Eacf10Ca62ae6787ba2fB044f8733Ee843', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x64E078A8Aa15A41B85890265648e965De686bAE6', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0xf408f04F9b7691f7174FA2bb73ad6d45fD5d3CBe', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x61bBB5135b43F03C96570616d6d3f607b7103111', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x89c1D413758F8339Ade263E6e6bC072F1d429f32', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x02233B22860f810E32fB0751f368fE4ef21A1C05', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x4b930E7b3E491e37EaB48eCC8a667c59e307ef20', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x855FA758c77D68a04990E992aA4dcdeF899F654A', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    # token.transfer('0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e', 100000, '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')
    task._add_task_owner('0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e')
    task._add_task_owner('0x610Bb1573d1046FCb8A70Bbbd395754cD57C2b60')
    task._add_task_owner('0x855FA758c77D68a04990E992aA4dcdeF899F654A')
    task._add_task_owner('0xfA2435Eacf10Ca62ae6787ba2fB044f8733Ee843')
    task._add_task_owner('0x64E078A8Aa15A41B85890265648e965De686bAE6')
    task._add_task_owner('0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598')
    task._add_task_owner('0x99cce66d3A39C2c2b83AfCefF04c5EC56E9B2A58')
    task._add_task_owner('0x8C4cE7a10A4e38EE96feD47C628Be1FfA57Ab96e')
    task._add_task_owner('0x61bBB5135b43F03C96570616d6d3f607b7103111')
    task._add_task_owner('0x89c1D413758F8339Ade263E6e6bC072F1d429f32')
    task._add_task_owner('0x02233B22860f810E32fB0751f368fE4ef21A1C05')
    task._add_task_owner('0x4b930E7b3E491e37EaB48eCC8a667c59e307ef20')
    task._add_task_owner('0x855FA758c77D68a04990E992aA4dcdeF899F654A')
    task._add_service('0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e')
    task._add_service('0x610Bb1573d1046FCb8A70Bbbd395754cD57C2b60')
    task._add_service('0x855FA758c77D68a04990E992aA4dcdeF899F654A')
    task._add_service('0x99cce66d3A39C2c2b83AfCefF04c5EC56E9B2A58')
    task._add_service('0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598')
    task._add_service('0x64E078A8Aa15A41B85890265648e965De686bAE6')
    task._add_service('0xfA2435Eacf10Ca62ae6787ba2fB044f8733Ee843')
    task._add_service('0x8C4cE7a10A4e38EE96feD47C628Be1FfA57Ab96e')
    task._add_service('0x61bBB5135b43F03C96570616d6d3f607b7103111')
    task._add_service('0x89c1D413758F8339Ade263E6e6bC072F1d429f32')
    task._add_service('0x02233B22860f810E32fB0751f368fE4ef21A1C05')
    task._add_service('0x4b930E7b3E491e37EaB48eCC8a667c59e307ef20')
    task._add_service('0x855FA758c77D68a04990E992aA4dcdeF899F654A')
    # task.add_task("http://wiki.metis.apple-store-signature.com/index.php/Create the How-to Guide(for Norbert)", 40, 100, "0x0000000000000000000000000000000000000000", "0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e")
    # print(task.get_task_length_by_address("0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e"))
    # print(task.review_task(3,
    #                        True,
    #                        "0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e"))
    # print(task.add_task("http://wiki.metis.apple-store-signature.com/index.php/PC ystem and MSC deployment",
    #                     50, 10000,
    #                     "0x0000000000000000000000000000000000000000", "0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e"
    #                     ))
    # print(task.add_task("http://wiki.metis.apple-store-signature.com/index.php/C ystem and MSC deployment",
    #                     50, 10000,
    #                     "0x0000000000000000000000000000000000000000", "0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e"
    #                     ))
    # print(task.add_task("http://wiki.metis.apple-store-signature.com/index.php/PO2C ystem and MSC deployment",
    #                     50, 10000,
    #                     "0x0000000000000000000000000000000000000000", "0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e"
    #                     ))
    # print(task.add_task("http://wiki.metis.apple-store-signature.com/index.php/P3OC ystem and MSC deployment",
    #                     50, 10000,
    #                     "0x0000000000000000000000000000000000000000", "0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e"
    #                     ))
    # print(task.add_task("http://wiki.metis.apple-store-signature.com/index.php/4123OC ystem and MSC deployment",
    #                     50, 10000,
    #                     "0x0000000000000000000000000000000000000000", "0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e"
    #                     ))
    # print(task.add_task("http://wiki.metis.apple-store-signature.com/index.php/432OC ystem and MSC deployment",
    #                     50, 10000,
    #                     "0x0000000000000000000000000000000000000000", "0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e"
    #                     ))
    # print(task.take_task("0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e", 3, '0x99cce66d3A39C2c2b83AfCefF04c5EC56E9B2A58'))
    # print(task.take_task("0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e", 3, '0xfA2435Eacf10Ca62ae6787ba2fB044f8733Ee843'))
    # print(task.finish_task("0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e", 3,"http://wiki.metis.apple-store-signature.com/index.php/AMA POC System and MSC deployment",
    #                        "0xfA2435Eacf10Ca62ae6787ba2fB044f8733Ee843"))
    # print(task.get_task_length_by_address("0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e"))
    # print(task.get_task_index("0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e", "1"))
    # print(task.get_task_index("0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e", "1"))
