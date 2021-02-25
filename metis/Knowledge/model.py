# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: model.py
@time: 2020/5/20 2:36 下午
@desc:
"""
import datetime
import json
from metis.extensions import db


class Knowledge(db.Model):
    __tablename__ = "metis_knowledge"

    id = db.Column(db.Integer, primary_key=True)
    knowledge_id = db.Column(db.String(255), nullable=False)
    knowledge_describe = db.Column(db.String(300), nullable=False)
    knowledge_name = db.Column(db.String(255), nullable=False)
    dac_id = db.Column(db.String(255), nullable=False)
    knowledge_belongs = db.Column(db.String(20), nullable=False)  # dac 拥有者
    knowledge_members = db.Column(db.Text)  # dac加入的成员
    ctime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    utime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    status = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, knowledge_name, dac_id, knowledge_belongs, knowledge_describe):
        self.knowledge_name = knowledge_name
        self.knowledge_belongs = knowledge_belongs
        self.dac_id = dac_id
        self.knowledge_id = self._gen_did()
        self.knowledge_describe = knowledge_describe
        self.dac_ctime = datetime.datetime.now()
        self.dac_utime = datetime.datetime.now()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()

    @staticmethod
    def _gen_did():
        last = Knowledge.query.order_by(Knowledge.knowledge_id.desc()).first()
        if not last:
            return "MK0000001"
        last_uid = last.knowledge_id.replace("MK", "")
        new_id = int(last_uid) + 1
        return f"MK{new_id:0>7d}"

    @staticmethod
    def get_knowledge_by_dac(dac_id):
        return Knowledge.query.filter(Knowledge.dac_id == dac_id, Knowledge.status == 1).all()


class KnowledgeDetail(db.Model):
    __tablename__ = "metis_knowledge_detail"

    id = db.Column(db.Integer, primary_key=True)
    knowledge_describe = db.Column(db.Text)
    knowledge_detail_id = db.Column(db.String(255), nullable=False)
    knowledge_detail_name = db.Column(db.String(255), nullable=False)
    knowledge_id = db.Column(db.String(255), nullable=False)
    knowledge_detail_belongs = db.Column(db.String(20), nullable=False)
    knowledge_detail_writer = db.Column(db.String(20))
    knowledge_detail_joiner = db.Column(db.Text, default=json.dumps([]))
    knowledge_detail_writer_balance = db.Column(db.String(255))
    knowledge_detail_joiner_balance = db.Column(db.String(255))
    review_status = db.Column(db.Integer, default=0)
    ctime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    utime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    status = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, knowledge_id, knowledge_detail_name, knowledge_detail_belongs, knowledge_detail_writer_balance,
                 knowledge_detail_joiner_balance):
        self.knowledge_id = knowledge_id
        self.knowledge_detail_name = knowledge_detail_name
        self.knowledge_detail_belongs = knowledge_detail_belongs
        self.knowledge_detail_joiner_balance = knowledge_detail_joiner_balance
        self.knowledge_detail_writer_balance = knowledge_detail_writer_balance
        self.knowledge_detail_id = self._gen_did()
        self.dac_ctime = datetime.datetime.now()
        self.dac_utime = datetime.datetime.now()

    @staticmethod
    def _gen_did():
        last = KnowledgeDetail.query.order_by(KnowledgeDetail.knowledge_detail_id.desc()).first()
        if not last:
            return "MKD000001"
        last_uid = last.knowledge_detail_id.replace("MKD", "")
        new_id = int(last_uid) + 1
        return f"MKD{new_id:0>6d}"

    @staticmethod
    def get_knowledge_detail_by_knowledge(knowledge_id):
        return KnowledgeDetail.query.filter(KnowledgeDetail.knowledge_id == knowledge_id,
                                            KnowledgeDetail.status == 1).all()

    @staticmethod
    def get_knowledge_detail_by_id(knowledge_detail_id):
        return KnowledgeDetail.query.filter(KnowledgeDetail.knowledge_detail_id == knowledge_detail_id,
                                            KnowledgeDetail.status == 1).first()



    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()


class KnowledgeInfo(db.Model):
    __tablename__ = "metis_knowledge_info"

    id = db.Column(db.Integer, primary_key=True)
    knowledge_detail_id = db.Column(db.String(20), nullable=False)
    knowledge_info_id = db.Column(db.String(20), nullable=False)
    knowledge_info_belongs = db.Column(db.String(20), nullable=False)
    knowledge_info_type = db.Column(db.String(20), nullable=False)
    knowledge_info_memo = db.Column(db.Text, nullable=False)
    knowledge_info_fabulous = db.Column(db.Integer, default=0)
    ctime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    utime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    status = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, knowledge_detail_id, knowledge_info_belongs, knowledge_info_type, knowledge_info_memo):
        self.knowledge_detail_id = knowledge_detail_id
        self.knowledge_info_belongs = knowledge_info_belongs
        self.knowledge_info_type = knowledge_info_type
        self.knowledge_info_memo = knowledge_info_memo
        self.knowledge_info_id = self._gen_did()

    @staticmethod
    def _gen_did():
        last = KnowledgeInfo.query.order_by(KnowledgeInfo.knowledge_info_id.desc()).first()
        if not last:
            return "MKI000001"
        last_uid = last.knowledge_info_id.replace("MKI", "")
        new_id = int(last_uid) + 1
        return f"MKI{new_id:0>6d}"

    @staticmethod
    def get_knowledge_info_joiner_by_knowledge(knowledge_detail_id):
        return KnowledgeInfo.query.filter(KnowledgeInfo.knowledge_detail_id == knowledge_detail_id,
                                          KnowledgeInfo.knowledge_info_type == 'joiner',
                                          KnowledgeInfo.status == 1).all()

    @staticmethod
    def get_knowledge_info_writer_by_knowledge(knowledge_detail_id):
        return KnowledgeInfo.query.filter(KnowledgeInfo.knowledge_detail_id == knowledge_detail_id,
                                          KnowledgeInfo.knowledge_info_type == 'writer',
                                          KnowledgeInfo.status == 1).first()

    @staticmethod
    def get_knowledge_info_by_id(knowledge_info_id):
        return KnowledgeInfo.query.filter(KnowledgeInfo.knowledge_info_id == knowledge_info_id,
                                          KnowledgeInfo.status == 1).first()

    @staticmethod
    def get_no_review_knowledge_detail_by_id(knowledge_detail_id):
        return KnowledgeInfo.query.filter(KnowledgeInfo.knowledge_detail_id == knowledge_detail_id,
                                          KnowledgeInfo.status == 0).all()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
