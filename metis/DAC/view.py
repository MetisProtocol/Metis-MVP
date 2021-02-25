# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: view.py
@time: 2020/5/28 12:31 下午
@desc:
"""
import json
import datetime
from . import impl
from flask import Blueprint, request
from flask.views import MethodView
from flask_login import current_user, login_required
from metis.utils.helpers import render, register_view, stand_response
from metis.Home.model import DAC
from .form import ActivityDACForm
from metis.Error import error_handler
from metis.Account.model import Account
from metis.config.Const import ACCOUNT_START
from metis.SmartContract.contracts import MToken, TaskList, MSC
from metis.Proposal.model import Work, Operation

date_dict = [
    {
        "id": 104,
        "year": 2019,
        "day":1,
        "month":6
    },
    {
        "id": 123,
        "year": 2020,
        "day":30,
        "month":9
    },

]
class DACContentIndex(MethodView):

    @login_required
    def get(self, dac_id):
        dac = DAC.get_dac_by_id(dac_id)
        operations = Operation.query.order_by(Operation.ctime.desc()).all()
        operations_main = Operation.get_by_account_uid(current_user.uid)
        account_dict = {operation.account_uid: Account.get_user_by_uid(operation.account_uid) for operation in operations}
        user_info = dict(username=current_user.username, email=current_user.email)
        if not dac:
            return error_handler(404, dac_id=dac_id, user_info=user_info)
        if not dac.dac_is_active:
            return error_handler(403, dac_id=dac_id, user_info=user_info, form=ActivityDACForm())
        dac_members = json.loads(dac.dac_members) if dac.dac_members else []  # [uid, ...]
        dac_members_logo = [Account.get_user_by_uid(dac_member).logo for dac_member in dac_members]
        dac_members = [Account.get_user_by_uid(dac_member).eth_addr for dac_member in dac_members]
        finish_work_count = Work.get_finish_work(current_user.uid, dac_id)
        working_count = Work.get_working(current_user.uid, dac_id)
        token = MToken()
        balance = token.get_balance(current_user.eth_addr)
        dac_admin = Account.get_user_by_uid(dac.dac_admin)
        dac_info = {
            "dac_id": dac.dac_id,
            "dac_name": dac.dac_name,
            "is_active": dac.dac_is_active,
            "dac_members_logo": dac_members_logo,
            "dac_admin": dac_admin.eth_addr,
            "dac_members": dac_members,
            "dac_logo": dac.dac_logo,
            "dac_admin_logo": dac_admin.logo
        }
        is_admin = True if dac.dac_admin == current_user.uid else False
        return render("DAC/index.html", dac_id=dac_id, dac_info=dac_info, user_info=user_info, is_admin=is_admin,
                      balance=balance, finish_work=finish_work_count, on_work=working_count,
                      finish_work_count=len(finish_work_count), on_work_count=len(working_count), operations=operations,
                      operations_main=operations_main, account_dict=account_dict)


class ActiveDAC(MethodView):

    def form(self):
        form = ActivityDACForm()
        form.process(request.form)
        return form

    @login_required
    def post(self, dac_id):
        form = self.form()
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email)
        if form.validate_on_submit():
            if not dac:
                return error_handler(404, dac_id=dac_id, user_info=user_info)
            if dac.dac_admin != current_user.uid:   # 用户不属于这个DAC不允许访问 TODO 所有的关于DAC的视图都需要考虑
                return error_handler(403, dac_id=dac_id, user_info=user_info, form=ActivityDACForm())
            dac.dac_is_active = True
            dac.save()
            task_list = TaskList()
            task_list._add_task_owner(current_user.eth_addr)
            token = MToken()
            # 质押合约
            msc = MSC()
            # deploy ms

            msc_addr = msc.deploy_msc([current_user.eth_addr, ACCOUNT_START], 0)
            print(msc_addr)
            # msc_addr 部署合约的地址
            # transfer excitation to this msc 将质押金从账户中扣出
            token.transfer(msc_addr, int(form.excitation.data), current_user.eth_addr)
            # sys account active this contract 质押第三方
            token.transfer(msc_addr, 0, ACCOUNT_START)
            return stand_response()
        return stand_response('error', ['submit error'])


@impl(tryfirst=True)
def load_blueprints(app):

    dac = Blueprint("dac", __name__)
    register_view(
        dac,
        routes=['/<dac_id>'],
        view_func=DACContentIndex.as_view("index")
    )
    register_view(
        dac,
        routes=['/<dac_id>/active'],
        view_func=ActiveDAC.as_view("active")
    )

    app.register_blueprint(dac, url_prefix="/dac")







