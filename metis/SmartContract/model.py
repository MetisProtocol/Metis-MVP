# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: model.py
@time: 2020/5/26 3:06 下午
@desc:
"""
import logging
import datetime
from sqlalchemy import or_
from metis.extensions import db
from metis.MetisExecption.MetisError import StopValidation, PersistenceError

logger = logging.getLogger("metis")


class Eth(db.Model):
    __tablename__ = "metis_eth"

    id = db.Column(db.Integer, primary_key=True)
    public_key = db.Column(db.String(255), nullable=False)
    private_key = db.Column(db.String(255), nullable=False)
    is_assigned = db.Column(db.SmallInteger, nullable=False, default=0)     # 0 未分配 1 已分配
    ctime = db.Column(db.DateTime, nullable=False)
    utime = db.Column(db.DateTime, nullable=False)

    account_uid = db.Column(db.String(255))     # 同用户对应

    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key
        self.ctime = datetime.datetime.now()
        self.utime = datetime.datetime.now()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()

    @staticmethod
    def generate_eth():
        eth_instance = Eth.query.filter(Eth.is_assigned != 1).order_by(Eth.id).first()
        if not eth_instance:
            raise StopValidation("Eth地址不足")
        return eth_instance

    @staticmethod
    def is_exists(public_key):
        res = Eth.query.filter(Eth.public_key == public_key).first()
        return False if not res else True


class MSCTable(db.Model):

    __tablename__ = "metis_msc"

    id = db.Column(db.Integer, primary_key=True)
    msc_id = db.Column(db.String(255), nullable=False)
    msc_type = db.Column(db.String(20), nullable=False)     # 质押激励(EXCITATION)，质押保证金(PROMISE)，双方置换合约(TEMP)
    party_a = db.Column(db.String(255), nullable=False)     # 甲方
    party_b = db.Column(db.String(255))     # 乙方 目前的msc是一对一的，必定有一个甲方一个乙方
    msc_addr = db.Column(db.String(255), nullable=False)
    msc_status = db.Column(db.SmallInteger, nullable=False, default=0)  # 当前msc合约状态 pending effective completed ...
    is_effective = db.Column(db.Boolean, nullable=False, default=True)  # 该条记录是否有效

    work_id = db.Column(db.String(255), nullable=False)   # 哪个工作产生的合约，合约必是由工作合作产生的
    withdraw = db.Column(db.String(20), default=None)

    ctime = db.Column(db.DateTime, nullable=False)
    utime = db.Column(db.DateTime, nullable=False)

    def __init__(self, msc_type, party_a, work_id, msc_addr, party_b=""):
        self.msc_id = self._gen_msc_id()
        self.msc_type = msc_type
        self.party_a = party_a
        self.party_b = party_b
        self.work_id = work_id
        self.msc_addr = msc_addr
        self.ctime = datetime.datetime.now()
        self.utime = datetime.datetime.now()

    def _gen_msc_id(self):
        last = MSCTable.query.order_by(MSCTable.msc_id.desc()).first()
        if not last:
            return "MC0000001"
        else:
            last_id = int(last.msc_id.replace("MC", "")) + 1
            return f"MC{last_id:0>7d}"

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            logger.error("MSC Persistence Error")
            db.session.rollback()
            raise PersistenceError

    @staticmethod
    def get_party_b_relationship(account_uid):
        return MSCTable.query.filter(MSCTable.is_effective == 1,
                                     MSCTable.msc_type == "PROMISE",
                                     MSCTable.party_a == account_uid
                                     ).all()

    @staticmethod
    def get_party_a_relationship(account_uid):
        return MSCTable.query.filter(MSCTable.is_effective == 1,
                                     MSCTable.msc_type == 'PROMISE',
                                     MSCTable.party_b == account_uid
                                     ).all()

    @staticmethod
    def is_first_claim_promise(party_a):
        res = MSCTable.query.filter(MSCTable.party_a == party_a,
                                    MSCTable.msc_type == 'PROMISE',
                                    MSCTable.is_effective == 1,
                                    ).first()
        return False if res else True

    @staticmethod
    def get_first_claim_promise(uid):
        res = MSCTable.query.filter(or_(MSCTable.party_a == uid, MSCTable.party_b == uid),
                                    MSCTable.msc_type == 'PROMISE',
                                    MSCTable.is_effective == 1,
                                    ).first()
        return res

    @staticmethod
    def get_all_first_claim_promise(uid):
        res = MSCTable.query.filter(or_(MSCTable.party_a == uid, MSCTable.party_b == uid),
                                    MSCTable.msc_type == 'PROMISE',
                                    MSCTable.is_effective == 1,
                                    ).all()
        return res

    @staticmethod
    def get_temporary_by_work_id(work_id):
        return MSCTable.query.filter(MSCTable.work_id == work_id,
                                     MSCTable.is_effective == 1,
                                     MSCTable.msc_type == 'TEMPORARY').first()

    @staticmethod
    def get_formal_by_work_id(work_id):
        return MSCTable.query.filter(MSCTable.work_id == work_id,
                                     MSCTable.is_effective == 1,
                                     MSCTable.msc_type == 'FORMAL').first()

    @staticmethod
    def get_effective_promise(party_a, party_b):
        return MSCTable.query.filter(
            MSCTable.party_a == party_a,
            MSCTable.party_b == party_b,
            MSCTable.is_effective == 1,
            MSCTable.msc_type == "PROMISE"
        ).order_by(MSCTable.msc_id.desc()).first()

    @staticmethod
    def get_formal_effective_promise(party_a, party_b):
        return MSCTable.query.filter(
            MSCTable.party_a == party_a,
            MSCTable.party_b == party_b,
            MSCTable.is_effective == 1,
            MSCTable.msc_type == "FORMAL"
        ).order_by(MSCTable.msc_id.desc()).first()
    # 激励质押合约，需要介入一个第三方，等到有用户接受任务时，第三方退出，重新建立一个双方的合约
    #  保证金质押合约，总是由任务接收方发起，等待任务发布方质押之后，保证金合约生效，双方由此建立合作关系

    #  用户中间遍历关系表 type 为 保证金质押，已激活的，未失效的，用户遍历party_a == uid
    # admin 遍历 party_b = admin_uid 找出所有关系
    # 解除协作需要遍历工作表，只要双方目前没有正在进行的工作，没有未完成的工作即可解除协作



