# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: model.py
@time: 2020/5/20 2:36 下午
@desc:
"""
import datetime
from metis.extensions import db


class DAC(db.Model):
    __tablename__ = "metis_dac"

    id = db.Column(db.Integer, primary_key=True)
    dac_id = db.Column(db.String(255), nullable=False)
    dac_name = db.Column(db.String(255), nullable=False)
    dac_description = db.Column(db.String(255), nullable=False)
    dac_admin = db.Column(db.String(20), nullable=False)    # dac 拥有者
    dac_members = db.Column(db.Text)    # dac加入的成员
    dac_logo = db.Column(db.String(100))
    dac_ctime = db.Column(db.DateTime, nullable=False)
    dac_utime = db.Column(db.DateTime, nullable=False)
    dac_is_active = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, dac_name, dac_description, dac_admin):
        self.dac_name = dac_name
        self.dac_description = dac_description
        self.dac_admin = dac_admin
        self.dac_id = self._gen_did()
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
        last = DAC.query.order_by(DAC.dac_id.desc()).first()
        if not last:
            return "MD0000001"
        last_uid = last.dac_id.replace("MD", "")
        new_id = int(last_uid) + 1
        return f"MD{new_id:0>7d}"

    @staticmethod
    def is_exists(dac_name):
        return True if DAC.query.filter(DAC.dac_name == dac_name.strip(" ")).first() else False

    @staticmethod
    def is_admin(dac_id, uid):
        return True if DAC.query.filter(DAC.dac_admin == uid, DAC.dac_id == dac_id).first() else False

    @staticmethod
    def get_all_effective_dac():
        return DAC.query.filter(DAC.dac_is_active != 0).all()

    @staticmethod
    def get_all_dac_by_admin(uid):
        return DAC.query.filter(DAC.dac_admin == uid).all()

    @staticmethod
    def get_dac_by_id(dac_id):
        return DAC.query.filter(DAC.dac_id == dac_id).first()







