# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: model.py
@time: 2020/5/11 11:23 上午
@desc:
"""
import logging
import datetime
from sqlalchemy import or_
from metis.extensions import db
from metis.MetisExecption.MetisError import PersistenceError

logger = logging.getLogger("metis")


class Work(db.Model):
    __tablename__ = "metis_work"

    id = db.Column(db.Integer, primary_key=True)
    work_id = db.Column(db.String(255), nullable=False)
    work_name = db.Column(db.String(255), nullable=False)
    work_describe = db.Column(db.String(255), nullable=False)
    work_excitation = db.Column(db.Integer, nullable=False)
    work_expiry = db.Column(db.Integer, nullable=False)
    work_deadline = db.Column(db.DateTime)
    work_status = db.Column(db.SmallInteger, nullable=False, default=0)
    publisher = db.Column(db.String(255), nullable=False)  # 发布方
    participants = db.Column(db.String(255))  # 接收方
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    ctime = db.Column(db.DateTime, nullable=False)
    utime = db.Column(db.DateTime, nullable=False)

    dac_id = db.Column(db.String(255), nullable=False)

    def __init__(self, work_name, work_describe, work_expiry, work_deadline, work_excitation, dac_id, publisher):
        self.work_id = self._gen_work_id()
        self.work_name = work_name
        self.work_describe = work_describe
        self.work_deadline = work_deadline
        self.work_expiry = work_expiry
        self.work_excitation = work_excitation
        self.dac_id = dac_id
        self.publisher = publisher
        self.ctime = datetime.datetime.now()
        self.utime = datetime.datetime.now()

    @staticmethod
    def _gen_work_id():
        last_work_id = Work.query.order_by(Work.work_id.desc()).first()
        if not last_work_id:
            return "MW0000001"
        else:
            suffix = last_work_id.work_id.replace("MW", "")
            return f"MW{int(suffix) + 1:0>7d}"

    @staticmethod
    def get_published_works(publisher, dac_id):
        return Work.query.filter(Work.publisher == publisher, Work.dac_id == dac_id).order_by(Work.work_id).all()

    @staticmethod
    def get_received_works(recipient, dac_id):
        return Work.query.filter(Work.participants == recipient, Work.dac_id == dac_id).order_by(Work.work_id).all()

    @staticmethod
    def get_all_available_works(dac_id):
        return Work.query.filter(Work.dac_id == dac_id, Work.is_active).order_by(Work.ctime.desc()).all()

    @staticmethod
    def is_exists(dac_id, work_name):
        return True if Work.query.filter(Work.dac_id == dac_id, Work.work_name == work_name).first() else False

    @staticmethod
    def is_exists_by_work_id(dac_id, work_id):
        return True if Work.query.filter(Work.dac_id == dac_id, Work.work_id == work_id).first() else False

    @staticmethod
    def is_effective(work_id):
        return True if Work.query.filter(Work.work_id == work_id).first() else False

    @staticmethod
    def get_excitation_by_work_id(work_id):
        return Work.query.filter(Work.work_id == work_id).first().work_excitation

    @staticmethod
    def get_work_by_work_id(work_id):
        return Work.query.filter(Work.work_id == work_id).first()

    @staticmethod
    def get_publisher_by_work_id(work_id):
        return Work.query.filter(Work.work_id == work_id).first()

    @staticmethod
    def get_finish_work(account_id, dac_id):
        return Work.query.filter(or_(Work.publisher == account_id, Work.participants == account_id),
                                 Work.work_status == 6, Work.dac_id == dac_id).all()

    @staticmethod
    def get_working(account_id, dac_id):
        return Work.query.filter(or_(Work.publisher == account_id, Work.participants == account_id),
                                 or_(Work.work_status == 1, Work.work_status == 2, Work.work_status == 3,
                                     Work.work_status == 4, Work.work_status == 5), Work.dac_id == dac_id).all()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            raise PersistenceError("Could not persistence work info")


class WorkInfo(db.Model):
    __tablename__="metis_work_info"

    id = db.Column(db.Integer, primary_key=True)
    work_id = db.Column(db.String(20), nullable=False)
    work_describe = db.Column(db.String(300))
    work_memo = db.Column(db.Text)
    enclosure = db.Column(db.Text)
    status = db.Column(db.Boolean, nullable=False, default=1)
    ctime = db.Column(db.DateTime, nullable=False)
    utime = db.Column(db.DateTime, nullable=False)

    def __init__(self, work_id):
        self.work_id = work_id
        self.ctime = datetime.datetime.now()
        self.utime = datetime.datetime.now()

    @staticmethod
    def get_work_info_by_work_id(work_id):
        return WorkInfo.query.filter_by(work_id=work_id).first()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            raise PersistenceError("Could not persistence work info")


class Operation(db.Model):
    __tablename__ = "metis_operation"

    id = db.Column(db.Integer, primary_key=True)
    account_uid = db.Column(db.String(20), nullable=False)
    operation_type = db.Column(db.String(100), nullable=False)
    operation_memo = db.Column(db.String(300), nullable=False)
    operation_memo_en = db.Column(db.String(300))
    status = db.Column(db.Boolean, nullable=False, default=1)
    ctime = db.Column(db.DateTime, nullable=False)
    utime = db.Column(db.DateTime, nullable=False)

    # dac_id = db.Column(db.String(255), nullable=False)

    def __init__(self, account_uid, operation_type, operation_memo, operation_memo_en):
        self.account_uid = account_uid
        self.operation_type = operation_type
        self.operation_memo = operation_memo
        self.operation_memo_en = operation_memo_en
        self.ctime = datetime.datetime.now()
        self.utime = datetime.datetime.now()

    @staticmethod
    def create_operation(account_uid, operation_type, operation_memo, operation_memo_en):
        operation = Operation(account_uid, operation_type, operation_memo, operation_memo_en)
        operation.save()

    @staticmethod
    def get_by_account_uid(uid):
        return Operation.query.filter_by(account_uid=uid).order_by(Operation.ctime.desc()).all()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            raise PersistenceError("Could not persistence work info")


class TransferInfo(db.Model):
    __tablename__ = "metis_transfer_info"
    id = db.Column(db.Integer, primary_key=True)
    transfer_from = db.Column(db.String(100), nullable=False)
    transfer_to = db.Column(db.String(100), nullable=False)
    transfer_hash = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=1)
    amount = db.Column(db.String(20), nullable=False)
    ctime = db.Column(db.DateTime, nullable=False)
    utime = db.Column(db.DateTime, nullable=False)

    def __init__(self, transfer_hash, transfer_from, transfer_to, amount):
        self.transfer_hash = transfer_hash
        self.transfer_from = transfer_from
        self.transfer_to = transfer_to
        self.amount = amount
        self.ctime = datetime.datetime.now()
        self.utime = datetime.datetime.now()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            raise PersistenceError("Could not persistence work info")

    @staticmethod
    def get_transfer_info(eth_addr):
        return TransferInfo.query.filter(or_(TransferInfo.transfer_from == eth_addr,
                                             TransferInfo.transfer_to == eth_addr)). \
            order_by(TransferInfo.ctime.desc()).all()

