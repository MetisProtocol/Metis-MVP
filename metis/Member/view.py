# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: view.py
@time: 2020/5/8 12:45 下午
@desc:
"""
import json
import datetime

from flask import Blueprint, request
from flask.views import MethodView
from metis.Member import impl
from metis.Member.form import DACMemberRegisterForm, TransferForm
from metis.Account.model import Account
from metis.utils.helpers import register_view, render, stand_response
from metis.SmartContract.contracts import MToken, Transaction, MSC
from flask_login import login_required, current_user
from metis.SmartContract.model import MSCTable
from metis.Proposal.model import Operation, TransferInfo
from metis.Home.model import DAC


class Register(MethodView):
    def __init__(self, registration_service_factory):
        self.registration_service_factory = registration_service_factory

    def form(self):
        form = DACMemberRegisterForm()
        form.process(request.form)
        return form

    def get(self):
        return render("member/register_dac_member.html", form=self.form())

    def post(self):
        form = self.form()
        return json.dumps({"code": "ok"})


class MemberOperation(MethodView):
    def __init__(self):
        pass

    @login_required
    def get(self, dac_id):
        operations = Operation.get_by_account_uid(current_user.uid)
        return render("member/operation.html", operations=operations, dac_id=dac_id)


class MemberWallet(MethodView):
    def __init__(self):
        pass

    @login_required
    def get(self, dac_id):
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email, eth=current_user.eth_addr)
        token = MToken()
        balance = token.get_balance(current_user.eth_addr)
        eth_balance = token.web3.eth.getBalance(current_user.eth_addr)
        eth_balance = eth_balance / (10 ** 18) if eth_balance else eth_balance
        msc = MSCTable.get_first_claim_promise(current_user.uid)
        transfer_info = TransferInfo.get_transfer_info(current_user.eth_addr)
        is_admin = True if dac.dac_admin == current_user.uid else False
        print(len(transfer_info))
        return render("member/wallet.html", transfer_info=transfer_info, dac_id=dac_id, user_info=user_info,
                      msc=msc, balance=balance, transfer_form=TransferForm(), is_admin=is_admin,
                      eth_balance=eth_balance)


class Info(MethodView):

    def __init__(self):
        pass

    def form(self):
        form = TransferForm()
        form.process(request.form)
        return form

    @login_required
    def get(self, dac_id):
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email, eth=current_user.eth_addr)
        token = MToken()
        balance = token.get_balance(current_user.eth_addr)
        eth_balance = token.web3.eth.getBalance(current_user.eth_addr)
        eth_balance = eth_balance / (10 ** 18) if eth_balance else eth_balance
        msc = MSCTable.get_all_first_claim_promise(current_user.uid)
        is_admin = True if dac.dac_admin == current_user.uid else False
        return render("member/info.html", balance=balance, dac_id=dac_id, user_info=user_info,
                      transfer_form=TransferForm(), msc_info=msc, is_admin=is_admin, eth_balance=eth_balance)

    @login_required
    def post(self, dac_id):
        form = self.form()
        if form.validate_on_submit():
            transfer = Transaction()
            try:
                transfer.pay(current_user.eth_addr, form.receiver_eth.data, form.amount.data, form.private_key.data)
            except Exception:
                return stand_response("error", ['账户余额不足, 请充值'])
            Operation.create_operation(current_user.uid, "转账", "向%s转账%dM Token" % (form.receiver_eth.data, form.amount.data), "Transfer %d M Token to %s" % (form.amount.data, form.receiver_eth.data))
            return stand_response()
        for key, messages in form.errors.items():
            print(messages[0])
        return stand_response('error', [messages[0]])


class Withdraw(MethodView):
    def __init__(self):
        pass

    def form(self):
        pass

    @login_required
    def get(self, dac_id, msc_id):
        msc = MSCTable.query.filter_by(msc_id=msc_id).first()
        if request.args.get("zhongcai", ""):
            msc.withdraw = "000000000"
            msc.utime = datetime.datetime.now()
        else:
            if msc and not msc.withdraw:
                msc.withdraw = current_user.uid
                msc.utime = datetime.datetime.now()
            elif msc and msc.withdraw:
                try:
                    self._out_promise_from_chain(msc)
                except Exception:
                    return stand_response('error', '解除合作失败')
                msc.is_effective = 0
                msc.utime = datetime.datetime.now()
        msc.save()
        return stand_response()

    def _out_promise_from_chain(self, msc_record):
        msc = MSC()
        party_a = Account.get_user_by_uid(msc_record.party_a).eth_addr
        party_b = Account.get_user_by_uid(msc_record.party_b).eth_addr
        msc.i_want_out(party_a, msc_record.msc_addr)
        msc.i_want_out(party_b, msc_record.msc_addr)
        msc.withdraw(party_a, msc_record.msc_addr)
        msc.withdraw(party_b, msc_record.msc_addr)



@impl(tryfirst=True)
def load_blueprints(app):
    member = Blueprint("member", __name__)

    register_view(
        member,
        routes=['/register'],
        view_func=Register.as_view(
            "register",
            registration_service_factory=""
        )
    )
    register_view(
        member,
        routes=['/<dac_id>/info'],
        view_func=Info.as_view(
            "info"
        )
    )
    register_view(
        member,
        routes=['/<dac_id>/operation'],
        view_func=MemberOperation.as_view(
            "operation"
        )
    )
    register_view(
        member,
        routes=['/<dac_id>/wallet'],
        view_func=MemberWallet.as_view(
            "wallet"
        )
    )
    register_view(
        member,
        routes=['/<dac_id>/<msc_id>'],
        view_func=Withdraw.as_view(
            "withdraw"
        )
    )

    app.register_blueprint(member, url_prefix="/member")



