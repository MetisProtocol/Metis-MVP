# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: join_to_dac.py
@time: 2020/5/28 11:35 上午
@desc:
"""
import json
from flask_login import current_user
from metis.MetisExecption.MetisError import PersistenceError
from metis.SmartContract.contracts import TaskList, MSC, MToken
from metis.config.Const import ACCOUNT_START


class JoinToDAC:

    def __init__(self, plugins, orm, db):
        self.plugins = plugins
        self.dac_orm = orm
        self.db = db

    def join(self, dac_id, account):
        try:
            dac = self._store_info(dac_id, account)
        except Exception:
            raise
        return dac

    def _store_info(self, dac_id, account):
        dac = self.dac_orm.get_dac_by_id(dac_id)
        dac_members = json.loads(dac.dac_members) if dac.dac_members else []
        if account.uid not in dac_members:
            dac_members.append(account.uid)
        dac.dac_members = json.dumps(dac_members)
        account_dac = json.loads(account.dac) if account.dac else []
        account_dac.append(dac_id)
        account.dac = json.dumps(account_dac)
        task_list = TaskList()
        task_list._add_service(current_user.eth_addr)
        token = MToken()
        # 质押合约
        msc = MSC()
        # deploy msc
        msc_addr = msc.deploy_msc([current_user.eth_addr, ACCOUNT_START], 0)
        # msc_addr 部署合约的地址
        # transfer excitation to this msc 将质押金从账户中扣出
        token.transfer(msc_addr, 10, current_user.eth_addr)
        # sys account active this contract 质押第三方
        token.transfer(msc_addr, 0, ACCOUNT_START, value=1)
        self.db.session.add(dac)
        self.db.session.add(account)
        self.db.session.commit()
        # except Exception:
        #     self.db.session.rollback()
        #     raise PersistenceError("Could not persistence to db")
        return dac

