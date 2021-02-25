# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: contracts.py
@time: 2020/5/14 9:50 上午
@desc: SmartContract API with Python
"""
import datetime
from web3 import Web3
from metis.SmartContract.meta import SmartContractMeta
from metis.config.Const import DEBUG_TASK_LIST_CONTRACT_ADDR as T_TASK_ADDR
from metis.config.Const import DEBUG_M_TOKEN_CONTRACT_ADDR as T_TOKEN_ADDR
# from metis.config.Const import ACCOUNT_LAST, ACCOUNT_START, PRIVATE_KEYS
from metis.MetisExecption.MetisError import EthError
from metis.Proposal.model import TransferInfo
from metis.utils.helpers import md5


class TaskList(SmartContractMeta):
    ROLE = ["NONE", "TASK_OWNER", "SERVICE", "ADMIN"]
    TASK_STATUS = ["NONE", "OPEN", "EXECUTING", "REVIEW", "REJECT", "DONE"]

    def __init__(self):
        super(TaskList, self).__init__()
        self.initialize('task_list_abi.json', T_TASK_ADDR)
        # self.private_keys = PRIVATE_KEYS


    def add_task(self, info_url, expiry, prize, delegate, sender):
        self.web3.eth.defaultAccount = sender
        try:
            res = self.contract.functions.addTask(info_url, expiry, prize, delegate).transact()
        except Exception:
            raise EthError("提交工作到区块链异常")
        return res

    def take_task(self, task_owner, task_index, sender):
        self.web3.eth.defaultAccount = sender
        try:
            print(task_owner, task_index, sender)
            res = self.contract.functions.takeTask(task_owner, task_index).transact()
        except Exception as e:
            raise EthError("从区块链获取任务异常%s" % e)
        return res

    def finish_task(self, task_owner, task_index, result_url, sender):
        self.web3.eth.defaultAccount = sender
        try:
            res = self.contract.functions.finshTask(task_owner, task_index, result_url).transact()
        except Exception:
            raise EthError("提交工作到区块链异常")
        return res

    def review_task(self, task_index, verdict, sender):
        self.web3.eth.defaultAccount = sender
        try:
            res = self.contract.functions.reviewTask(task_index, verdict).transact()
        except Exception:
            raise EthError("审核工作结果提交异常")
        return res

    def get_task_length_by_address(self, task_owner):
        try:
            res = self.contract.functions.getNumTaskByAddress(task_owner).call()
        except Exception:
            raise EthError("获取工作列表异常")
        return res

    def get_task(self, owner, index):
        try:
            res = self.contract.functions.tasklist(owner, index).call()
        except Exception:
            raise EthError("获取任务失败")
        return res

    def get_task_index(self, owner, info_uri):
        try:
            for index in range(self.get_task_length_by_address(owner)):
                task_content = self.get_task(owner, index)
                if task_content[0] == info_uri:
                    return index
        except Exception:
            raise EthError('获取任务索引失败')


    def _add_task_owner(self, account):
        # self.web3.eth.defaultAccount = ACCOUNT_START
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        try:
            res = self.contract.functions.addTaskOwner(self.web3.toChecksumAddress(account)).transact()
        except Exception:
            raise EthError("授权task owner异常")
        return res

    def _add_service(self, account):
        # self.web3.eth.defaultAccount = ACCOUNT_START
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        try:
            res = self.contract.functions.addService(self.web3.toChecksumAddress(account)).transact()
        except Exception:
            raise EthError("授权task service异常")
        return res


class MSC(SmartContractMeta):

    CONTRACT_STATUS = ["Pending", "Effective", "Completed", "Dispute", "Requested", "Closed"]
    PARTICIPANT_STATUS = ["Pending", "Committed", "WantOut", "Completed", "Dispute", "Closed"]
    # ACCOUNT_START = ACCOUNT_START
    # ACCOUNT_LAST = ACCOUNT_LAST

    def __init__(self):
        super(MSC, self).__init__()
        # self.web3 = Web3(Web3.HTTPProvider(f"{self.DEBUG_SCHEME}://{self.DEBUG_HOST}"))
        self.web3 = Web3(Web3.HTTPProvider("http://123.57.141.229:8080"))
        self.abi = self._load_abi_as_json('msc_abi.json')
        with open(self.ABI_DIR + "msc_bytecode.txt", 'r') as fd:
            self.bytecode = fd.read().strip("\n").strip(" ")

    def deploy_msc(self, parties: list, amount):
        """
        :param parties: 发布方和原始用户的eth
        :param amount:
        :return:
        """
        # system account 并入到主网之后可能需要重新指定
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        parties = [self.web3.toChecksumAddress(user.strip(" ")) for user in parties]
        self.contract = self.web3.eth.contract(abi=self.abi, bytecode=self.bytecode)

        # convert accuracy
        amount = self._convert_accuracy(amount)

        # default account
        # self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        self.web3.eth.defaultAccount = self.web3.eth.accounts[7]

        # deploy 在此部署MSC合约 constructor
        print("1111")
        tx_hash = self.contract.constructor(
            parties,
            self.web3.toChecksumAddress(self.web3.eth.defaultAccount),
            1,
            self.web3.toChecksumAddress(T_TOKEN_ADDR),
            amount
        ).transact()
        # ).transact(self.get_signed_txn(self.ACCOUNT_LAST))
        print(tx_hash)
        print("=========")
        # tx_hash = self.web3.toHex(self.web3.keccak(tx_hash))
        # print(tx_hash)
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        print(tx_receipt)
        # 获取到此合约地址 并返回
        print("=======================")
        print("tx_receipt.contractAddress")
        print("=======================")
        return tx_receipt.contractAddress


    def send(self, to, amount, sender, msc_addr, value=0):
        # set sender
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.web3.toChecksumAddress(msc_addr))
        self.web3.eth.defaultAccount = sender

        # convert accuracy
        amount = self._convert_accuracy(amount)
        # return self.contract.functions.send(to, amount).transact(self.get_signed_txn(sender, value))
        return self.contract.functions.send(to, amount).transact()

    def i_want_out(self, sender, msc_addr, value=0):
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.web3.toChecksumAddress(msc_addr))
        self.web3.eth.defaultAccount = sender
        # return self.contract.functions.iwantout().transact(self.get_signed_txn(sender, value))
        return self.contract.functions.iwantout().transact()

    def withdraw(self, sender, msc_addr, value=0):
        self.web3.eth.defaultAccount = sender
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.web3.toChecksumAddress(msc_addr))
        return self.contract.functions.withdraw().transact()
        # return self.contract.functions.withdraw().transact(self.get_signed_txn(sender, value))

    def contract_status(self, msc_addr):
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.web3.toChecksumAddress(msc_addr))
        status_code = self.contract.functions.contractStatus().call()
        return self.CONTRACT_STATUS[status_code]


class MToken(SmartContractMeta):
    # ACCOUNT_START = ACCOUNT_START

    def __init__(self):
        super(MToken, self).__init__()
        self.initialize('m_token_abi.json', T_TOKEN_ADDR)

        # test env spec default account accounts[0]
        # self.web3.eth.accounts.create()
        # self.web3.eth.accounts[0] = "0xc27E363E8865c58992C808C020d258B319A4c8e8"
        print(type(self.web3.eth.accounts))
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]

    def get_balance(self, user):
        return self._convert_to_hum_accuracy(self.contract.functions.balanceOf(user).call())

    def transfer(self, to, amount, sender=None, private_key="0xb0057716d5917badaf911b193b12b910811c1497b5bada8d7711f758981c3773", value=0):
        amount = self._convert_accuracy(amount)
        if sender:
            self.web3.eth.defaultAccount = sender
        # tx_hash = self.contract.functions.transfer(to, amount).transact(self.get_signed_txn(sender))
        return self.contract.functions.transfer(to, amount).transact()
        # return self.contract.functions.transfer(to, amount).transact(self.get_signed_txn(sender, value))
        # amount = self._convert_accuracy(amount)
        # # if sender:
        # #     self.web3.eth.defaultAccount = sender
        # # tx = self.contract.functions.transfer(to, amount).transact()
        # # print(tx)
        # # print("-------------")
        # # return tx
        # # convert accuracy
        # # amount = self._convert_accuracy(amount)
        # if sender:
        #     self.web3.eth.defaultAccount = sender
        #     nonce = self.web3.eth.getTransactionCount(sender)
        #     # print("22222222222")
        #     # print(nonce)
        #     # print("22222222222")
        #     txn = self.contract.functions.transfer(to, amount).buildTransaction(
        #     {
        #         # "chainId": 1,
        #         "gas": 70000,
        #         "gasPrice": self.web3.toWei('1', 'gwei'),
        #         'nonce': nonce
        #     }
        # )
        #     print(txn)
        #     tx_hash = self._signature(txn, private_key)
        #     amount = self._convert_to_hum_accuracy(amount)
        #     self._persistence(sender, to, amount, tx_hash, gas="")
        # #
        # return

    def _signature(self, txn, private_key):
        signed_txn = self.web3.eth.account.signTransaction(txn, private_key=private_key)
        print("99999999999999")
        print(signed_txn)
        print(signed_txn.rawTransaction)
        print("99999999999999")
        self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        tx_hash = self.web3.toHex(self.web3.sha3(signed_txn.rawTransaction))
        return tx_hash

    def _persistence(self, frm, to, amount, tx_hash, gas):
        transfer_info = TransferInfo(tx_hash, frm, to, amount)
        transfer_info.save()


class Transaction(SmartContractMeta):

    def __init__(self):
        super(Transaction, self).__init__()
        # self.web3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/618f13ebe46048c796836d11ed87be09"))
        self.web3 = Web3(Web3.HTTPProvider("http://123.57.141.229:8080"))
        print("111")

    def claim(self, sender, amount):
        """
        对于一个任务，进行质押之后才能激活（接收方才能进行接收任务，但是目前msc必须有两方才能够部署生效）
        质押之后生成一个msc合约，然后系统调用私钥，对这次转账事务进行一次签名
        质押就是部署msc合约
        """
        self.web3.eth.defaultAccount = sender
        msc = MSC()
        msc_contract_addr = msc.deploy_msc("", 10)

    def pay(self, frm, to, amount, private_key="a06ff3f94c4b49596e69f0e0397735eea7c6dd6637d87ca0f0dff44cc6697232"):
        """
        转账，系统调用私钥对事务进行签名，存储事务
        """
        print("222")
        amount = self._convert_accuracy(amount)
        token = MToken()
        print("333")
        nonce = self.web3.eth.getTransactionCount(frm)
        print("444")
        self.web3.eth.defaultAccount = frm
        print("555")
        txn = token.contract.functions.transfer(to, amount).buildTransaction(
            {
                # "chainId": 1,
                "gas": 70000,
                "gasPrice": self.web3.toWei('1', 'gwei'),
                'nonce': nonce
            }
        )
        print(txn)
        tx_hash = self._signature(txn, private_key)
        print(tx_hash)
        amount = self._convert_to_hum_accuracy(amount)
        print("222222222222222222")
        print(nonce)
        print("222222222222222222")
        self._persistence(frm, to, amount, tx_hash, gas="")

    def _signature(self, txn, private_key):
        signed_txn = self.web3.eth.account.signTransaction(txn, private_key=private_key)
        self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        tx_hash = self.web3.toHex(self.web3.sha3(signed_txn.rawTransaction))
        return tx_hash

    def _persistence(self, frm, to, amount, tx_hash, gas):
        print("===========")
        print("===========")
        print(tx_hash)
        print(frm)
        print(to)
        print(amount)
        print("===========")
        print("===========")
        transfer_info = TransferInfo(tx_hash, frm, to, amount)
        transfer_info.save()


if __name__ == '__main__':
    msc = MSC()
    print(msc.web3.eth.getBalance('0xCDC1E53Bdc74bBf5b5F715D6327Dca5785e228B4'))
    # print(msc.web3.eth.getTransactionReceipt(b'as\x10\xc5\x94?\xa6\x873\x1b\xdbz\xc8y X\xfcb\x95O\xc2\x94 \x1d\x86\xed\xe3\xabkX\x19x'))
    # print(msc.web3.eth.getTransactionCount('0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598'))
    # msc_addr = msc.deploy_msc(['0x64E078A8Aa15A41B85890265648e965De686bAE6', "0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0"], 0)
    # transe = Transaction()
    # transe.pay("0x64E078A8Aa15A41B85890265648e965De686bAE6", "0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598", 2000, "0x0874049f95d55fb76916262dc70571701b5c4cc5900c0691af75f1a8a52c8268")
    # dict01 = {'to': '0x518A9A528395E85317136265d520789aBEE477E7', 'from': '0x64E078A8Aa15A41B85890265648e965De686bAE6', 'data': '0xa919057c0000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000000b00000000000000000000000000000000000000000000000000000000000000c800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000041687474703a2f2f77696b692e6d657469732e6170706c652d73746f72652d7369676e61747572652e636f6d2f696e6465782e7068702f746573745f776f726b373800000000000000000000000000000000000000000000000000000000000000'}
    # task = TaskList()
    # print(task.web3.toChecksumAddress("0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598"))
    # print(task.contract.functions.addTaskOwner("0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598").call())
    # print(task.contract.functions.getNumTaskLists().call())
    # print(task.contract.functions.getNumTaskByAddress('0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598').call())
    # print(task.web3.eth.getTransactionReceipt(b'\x89>\xd5\x05\xe9\xc0\xd2\xde\xb4\x83M\xa5\x90r\x08\xb3\x0eB@\xb8\x91<:`\xca\x96D+\x8b\xc64\x8b'))
    # task.web3.eth.defaultAccount = "0x64E078A8Aa15A41B85890265648e965De686bAE6"
    # signed_txn = dict(
    #     nonce=task.web3.eth.getTransactionCount(task.web3.eth.defaultAccount),
    #     gasPrice=task.web3.eth.gasPrice,
    #     gas=2000000,
    #     value=0,
        # data=b'',
    # )
        # "0x0874049f95d55fb76916262dc70571701b5c4cc5900c0691af75f1a8a52c8268",
    # )
    # print(task._add_task_owner("0x64E078A8Aa15A41B85890265648e965De686bAE6"))
    # task.review_task(2, True, "0x64E078A8Aa15A41B85890265648e965De686bAE6")
    # tx = task._add_task_owner("0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598")
    # task.web3.eth.waitForTransactionReceipt(tx)
    # print(task.web3.eth.waitForTransactionReceipt(tx))
    # task._add_service("0x8C4cE7a10A4e38EE96feD47C628Be1FfA57Ab96e")
    # tx = task.add_task('http://wiki.metis.apple-store-signature.com/index.php/test_work312343u', 40, 100, "0x0000000000000000000000000000000000000000", '0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598')
    # print(task.web3.eth.waitForTransactionReceipt(tx))
    # print(tx)
    # print(task.take_task('0x64E078A8Aa15A41B85890265648e965De686bAE6', 2, '0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598'))
    # print(task.web3.eth.getTransactionCount("0x64E078A8Aa15A41B85890265648e965De686bAE6"))
    # print(task.get_task("0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598", 0))
    # print(task.get_task("0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598", 1))
    # print(task.get_task("0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598", 2))
    # print(task.get_task("0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598", 3))
    # print(task.get_task("0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598", 3))
    # task.review_task(2, True, '0x8C4cE7a10A4e38EE96feD47C628Be1FfA57Ab96e')
    # print(task.contract.functions.taskownerlist.call())
    # print(task.take_task('0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598', 2, '0x8C4cE7a10A4e38EE96feD47C628Be1FfA57Ab96e'))
    # print(task.get_task_index("0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598", 'http://wiki.metis.apple-store-signature.com/index.php/test_worktasd'))
    # task.review_task(2, True, "0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598")
    # print(task.get_task_length_by_address("0x2F560290FEF1B3Ada194b6aA9c40aa71f8e95598"))
    # task.review_task(2, True, "0x64E078A8Aa15A41B85890265648e965De686bAE6")
    # print(task.get_task_length_by_address("0x64E078A8Aa15A41B85890265648e965De686bAE6"))
    # transaction = {
    # 'to': '0x64E078A8Aa15A41B85890265648e965De686bAE6',
    # 'value': 1000,
    # 'gas': 100000,
    # 'gasPrice': task.web3.eth.gasPrice,
    # 'nonce': 0,
    # 'chainId': 3
    # }
    # key = 'a06ff3f94c4b49596e69f0e0397735eea7c6dd6637d87ca0f0dff44cc6697232'
    # signed = task.web3.eth.account.sign_transaction(transaction, key)
    # print(signed.rawTransaction)
    # print(task.web3.eth.sendTransaction({'to': '0xd3CdA913deB6f67967B99D67aCDFa1712C293601', 'from': "0xc27E363E8865c58992C808C020d258B319A4c8e8", 'value': 100}))
    # print(datetime.datetime.strptime('2020-07-30', '%Y-%m-%d'))
    # msc = MSC()
    # token = MToken()
    # print(msc.contract_status('0x5AC90ac3619ED2F320bAed5700B312e4ea3C276e'))
    # print(msc.contract_status('0x2044765102a14F39C0ADbd3e52d5A31a3B5A4429'))
    # print("===")
    # print(token.web3.eth.getTransactionCount("0xc27E363E8865c58992C808C020d258B319A4c8e8"))
    # print(token.get_balance("0xBF5de68e91a6116E95be42b856Faea6c9B2735a9"))
    # print(msc.web3.toChecksumAddress(msc.web3.eth.accounts[8]))
    # task = TaskList()
    # task._add_task_owner('0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e')
    # task._add_service('0x610Bb1573d1046FCb8A70Bbbd395754cD57C2b60')
    # a = task.add_task(
    #     'https://www.baidu.com',
    #     30,
    #     50,
    #     "0x0000000000000000000000000000000000000000",
    #     '0x43e26aB9733E5E99B60E9f475049261d05e8C81F'
    # )
    # print(task.get_task_length_by_address("0x43e26aB9733E5E99B60E9f475049261d05e8C81F"))
    # print(task_list.get_task_index("0x385c4caDE07D0FA1e58a36fb9a7e9AeE958D7914", "http://wiki.metis.apple-store-signature.com/index.php/test_work7"))
    # print(task_list.get_task("0xB41c18B85e122d9aa448954B409aa3ab4A69C1bc", 0))
    # print(msc.contract_status("0x6657ffb6BCc1cbf46Ff600C93F77160D6c1526da"))
    # print((datetime.datetime.now() - datetime.datetime.strptime('2020-07-20', '%Y-%m-%d')).days)