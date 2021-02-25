# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: view.py
@time: 2020/5/18 12:27 下午
@desc:
"""
import logging
import json
import datetime
from flask import Blueprint, request
from metis.Knowledge import impl
from flask.views import MethodView
from flask_login import login_required, current_user
from metis.utils.helpers import render, register_view, stand_response
from metis.Home.model import DAC
from metis.DAC.form import ActivityDACForm
from metis.Error import error_handler
from metis.Knowledge.model import Knowledge, KnowledgeDetail, KnowledgeInfo
from metis.Knowledge.form import KnowledgeForm, KnowledgeDetailForm, KnowledgeJoinForm, KnowledgeInfoForm,\
    KnowledgeInfoEditForm
from metis.SmartContract.contracts import MToken, Transaction
from metis.Knowledge.service.add_knowledge import AddKnowledgeInfo
from metis.Member.form import TransferForm
from metis.Account.model import Account
from metis.Knowledge.service.add_knowledge_detail import AddKnowledgeDetailInfo
from metis.Knowledge.service.join_knowledge import AddKnowledgeJoinInfo
from metis.Knowledge.service.edit_knowledge import AddKnowledgeEditInfo
from metis.Knowledge.service.info_edit_knowledge import AddKnowledgeInfoEditInfo
from metis.MetisExecption.MetisError import StopValidation
from metis.Knowledge.service.factories import add_knowledge_service_factory, add_knowledge_detail_service_factory,\
    join_knowledge_service_factory, edit_knowledge_service_factory, info_edit_knowledge_service_factory

logger = logging.getLogger("metis")


class KnowledgeIndex(MethodView):

    def __init__(self):
        pass

    def form(self):
        form = KnowledgeForm()
        form.process(request.form)
        return form

    @login_required
    def get(self, dac_id):
        # knowledge = KnowledgeDetail.query.filter_by(id=1).first()
        # knowledge.knowledge_detail_joiner = json.dumps(['MU0000003'])
        # knowledge.save()
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email)
        if not dac:
            return error_handler(404, dac_id=dac_id, user_info=user_info)
        if not dac.dac_is_active:
            return error_handler(403, dac_id=dac_id, user_info=user_info, form=ActivityDACForm())
        knowledge_list = Knowledge.get_knowledge_by_dac(dac_id)
        is_admin = True if dac.dac_admin == current_user.uid else False
        return render("knowledge/index.html", form=self.form(), dac_id=dac_id, is_admin=is_admin, knowledge_list=knowledge_list)


class KnowledgeDetailIndex(MethodView):
    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = KnowledgeDetailForm()
        form.process(request.form)
        return form

    def get(self, knowledge_id, dac_id):
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email)
        if not dac:
            return error_handler(404, dac_id=dac_id, user_info=user_info)
        if not dac.dac_is_active:
            return error_handler(403, dac_id=dac_id, user_info=user_info, form=ActivityDACForm())
        knowledge_list = KnowledgeDetail.get_knowledge_detail_by_knowledge(knowledge_id)
        is_admin = True if dac.dac_admin == current_user.uid else False
        return render("knowledge/detail.html", form=self.form(), dac_id=dac_id, is_admin=is_admin,
                      knowledge_list=knowledge_list, knowledge_id=knowledge_id, json=json,
                      knowledge_join_form=KnowledgeJoinForm())

    def post(self, knowledge_id, dac_id):
        form = self.form()

        if form.validate_on_submit():
            # 工场函数
            service = self.service_factory()
            # 查出账户余额
            balance = MToken().get_balance(current_user.eth_addr)
            # 查出激励
            try:
                info = AddKnowledgeDetailInfo(
                    knowledge_id=knowledge_id,
                    knowledge_name=form.knowledge_detail_name.data,
                    knowledge_describe=form.knowledge_describe.data,
                    knowledge_detail_writer_balance=form.writer_balance.data,
                    knowledge_detail_joiner_balance=form.joiner_balance.data,
                    knowledge_detail_writer_excitation=form.writer_excitation.data,
                    knowledge_detail_joiner_excitation=form.joiner_excitation.data,
                    belongs=current_user.uid,
                    balance=balance,
                    user_eth=current_user.eth_addr
                )
                service.add_knowledge_detail(info, knowledge_id)
            except StopValidation as e:
                logger.error(e.reasons)
                return stand_response('error', e.reasons)
            return stand_response()
        else:
            for key, messages in form.errors.items():
                return stand_response('error', [messages[0]])


class KnowledgeJoin(MethodView):
    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = KnowledgeJoinForm()
        form.process(request.form)
        return form

    def post(self, knowledge_detail_id, join_type):
        form = self.form()

        if form.validate_on_submit():
            # 工场函数
            service = self.service_factory()
            # 查出账户余额
            balance = MToken().get_balance(current_user.eth_addr)
            # 查出激励
            try:
                info = AddKnowledgeJoinInfo(
                    knowledge_detail_id=knowledge_detail_id,
                    balance=balance,
                    user_eth=current_user.eth_addr
                )
                service.join_knowledge(info, join_type)
            except StopValidation as e:
                logger.error(e.reasons)
                return stand_response('error', e.reasons)
            return stand_response()
        else:
            for key, messages in form.errors.items():
                return stand_response('error', [messages[0]])


class KnowledgeInfoIndex(MethodView):
    def __init__(self, service_factory):
        self.service_factory = service_factory
        pass

    def form(self):
        form = KnowledgeInfoEditForm()
        form.process(request.form)
        return form

    def post(self, dac_id, knowledge_detail_id):
        form = self.form()

        if form.validate_on_submit():
            # 工场函数
            service = self.service_factory()
            try:
                info = AddKnowledgeInfoEditInfo(
                    knowledge_detail_name=form.knowledge_detail_name.data,
                    knowledge_describe=form.knowledge_describe.data,
                    knowledge_detail_writer_pledge=form.knowledge_detail_writer_pledge.data,
                    knowledge_detail_joiner_pledge=form.knowledge_detail_joiner_pledge.data,
                    knowledge_detail_writer_excitation=form.knowledge_detail_writer_excitation.data,
                    knowledge_detail_joiner_excitation=form.knowledge_detail_joiner_excitation.data
                )
                service.edit_knowledge_info(info, knowledge_detail_id)
            except StopValidation as e:
                logger.error(e.reasons)
                return stand_response('error', e.reasons)
            return stand_response()
        else:
            for key, messages in form.errors.items():
                return stand_response('error', [messages[0]])

    def get(self, dac_id, knowledge_detail_id):
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email)
        if not dac:
            return error_handler(404, dac_id=dac_id, user_info=user_info)
        if not dac.dac_is_active:
            return error_handler(403, dac_id=dac_id, user_info=user_info, form=ActivityDACForm())
        knowledge = KnowledgeDetail.get_knowledge_detail_by_id(knowledge_detail_id)
        knowledge_info_list = KnowledgeInfo.get_knowledge_info_joiner_by_knowledge(knowledge_detail_id)
        knowledge_info_writer = KnowledgeInfo.get_knowledge_info_writer_by_knowledge(knowledge_detail_id)
        members_logo = {member.uid: member.logo for member in Account.query.all()}

        is_admin = True if dac.dac_admin == current_user.uid else False
        return render("knowledge/info.html", form=self.form(), dac_id=dac_id, is_admin=is_admin,
                      knowledge=knowledge, json=json, knowledge_info_list=knowledge_info_list,
                      knowledge_info_writer=knowledge_info_writer, transfer_form=TransferForm(),
                      get_addr=Account.get_user_by_uid, members_logo=members_logo)


class KnowledgeInfoEdit(MethodView):
    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = KnowledgeInfoForm()
        form.process(request.form)
        return form

    def post(self, dac_id, knowledge_detail_id):
        form = self.form()

        if form.validate_on_submit():
            # 工场函数
            service = self.service_factory()
            try:
                info = AddKnowledgeEditInfo(
                    knowledge_detail_id=knowledge_detail_id,
                    knowledge_info_belongs=current_user.uid,
                    knowledge_info_type=form.knowledge_info_type.data,
                    knowledge_info_memo=form.knowledge_info_memo.data
                )
                service.edit_knowledge(info)
            except StopValidation as e:
                logger.error(e.reasons)
                return stand_response('error', e.reasons)
            return stand_response()
        else:
            for key, messages in form.errors.items():
                return stand_response('error', [messages[0]])

    def get(self, dac_id, knowledge_detail_id):
        knowledge_type = request.args.get('knowledge_type', '')
        knowledge = KnowledgeInfo.query.filter(KnowledgeInfo.knowledge_detail_id == knowledge_detail_id,
                                               KnowledgeInfo.knowledge_info_type == knowledge_type).first() if knowledge_type == 'writer' else ''
        knowledge_memo = ''
        if knowledge:
            knowledge_memo = knowledge.knowledge_info_memo
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email)
        if not dac:
            return error_handler(404, dac_id=dac_id, user_info=user_info)
        if not dac.dac_is_active:
            return error_handler(403, dac_id=dac_id, user_info=user_info, form=ActivityDACForm())
        return render("knowledge/info-edit.html", form=self.form(), dac_id=dac_id,
                      knowledge_detail_id=knowledge_detail_id, knowledge_type=knowledge_type,
                      knowledge_memo=knowledge_memo)


class KnowledgeInfoFabulous(MethodView):
    def __init__(self):
        pass

    def get(self, knowledge_info_id):
        knowledge_detail = KnowledgeInfo.get_knowledge_info_by_id(knowledge_info_id)
        knowledge_detail.knowledge_info_fabulous += 1
        knowledge_detail.save()
        return stand_response()


class KnowledgeReviewPass(MethodView):
    def __init__(self):
        pass

    def get(self, dac_id, knowledge_detail_id):
        knowledge_detail = KnowledgeDetail.query.filter_by(knowledge_detail_id=knowledge_detail_id).first()
        excitation = json.loads(knowledge_detail.knowledge_detail_writer_balance)['excitation'] if knowledge_detail else 0
        transfer = Transaction()
        transfer.pay('0xC7739909e08A9a0F303A010d46658Bdb4d5a6786',
                     Account.get_user_by_uid(knowledge_detail.knowledge_detail_writer).eth_addr, excitation,
                     '0x86117111fcb34df8d0e58505969021b9308513c6e94d16172f0c8789a7130a43')

        knowledge_infos = KnowledgeInfo.query.filter(KnowledgeInfo.knowledge_detail_id == knowledge_detail_id, KnowledgeInfo.knowledge_info_type == 'joiner').all()
        joiner_excitation = json.loads(knowledge_detail.knowledge_detail_joiner_balance)['excitation'] if knowledge_detail else 0
        for knowledge_info in knowledge_infos:
            transfer.pay('0xC7739909e08A9a0F303A010d46658Bdb4d5a6786',
                         Account.get_user_by_uid(knowledge_info.knowledge_info_belongs).eth_addr, joiner_excitation,
                         '0x86117111fcb34df8d0e58505969021b9308513c6e94d16172f0c8789a7130a43')
        knowledge_detail.review_status = 2
        knowledge_detail.utime = datetime.datetime.now()
        knowledge_detail.save()
        return stand_response()


class KnowledgeReviewSubmit(MethodView):
    def __init__(self):
        pass

    def get(self, dac_id, knowledge_detail_id):
        knowledge_detail = KnowledgeDetail.get_knowledge_detail_by_id(knowledge_detail_id)
        knowledge_detail.review_status = 1
        knowledge_detail.save()
        return stand_response()


class KnowledgeReview(MethodView):
    def __init__(self):
        pass

    def form(self):
        pass

    def get(self, dac_id, knowledge_detail_id):
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email)
        if not dac:
            return error_handler(404, dac_id=dac_id, user_info=user_info)
        if not dac.dac_is_active:
            return error_handler(403, dac_id=dac_id, user_info=user_info, form=ActivityDACForm())
        knowledge = KnowledgeDetail.get_knowledge_detail_by_id(knowledge_detail_id)
        knowledge_info = KnowledgeInfo.query.filter_by(knowledge_detail_id=knowledge_detail_id, knowledge_info_type='writer').first()


        is_admin = True if dac.dac_admin == current_user.uid else False
        members_logo = {member.uid: member.logo for member in Account.query.all()}
        return render("knowledge/review.html", form=self.form(), dac_id=dac_id, is_admin=is_admin,
                      knowledge=knowledge, json=json, knowledge_info=knowledge_info,
                      get_addr=Account.get_user_by_uid, members_logo=members_logo)

    def post(self):
        pass


class KnowledgeAdd(MethodView):

    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = KnowledgeForm()
        form.process(request.form)
        return form

    @login_required
    def get(self, dac_id):
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email)
        if not dac:
            return error_handler(404, dac_id=dac_id, user_info=user_info)
        if not dac.dac_is_active:
            return error_handler(403, dac_id=dac_id, user_info=user_info, form=ActivityDACForm())
        is_admin = True if dac.dac_admin == current_user.uid else False
        return render("knowledge/add.html", dac_id=dac_id)

    @login_required
    def post(self, dac_id):
        form = self.form()

        if form.validate_on_submit():
            # 工场函数
            service = self.service_factory()
            # 查出账户余额
            balance = MToken().get_balance(current_user.eth_addr)
            # 查出激励
            try:
                info = AddKnowledgeInfo(
                    dac_id=dac_id,
                    knowledge_name=form.knowledge_name.data,
                    knowledge_describe=form.knowledge_describe.data,
                    belongs=current_user.uid,
                    balance=balance,
                    user_eth=current_user.eth_addr
                )
                service.add_knowledge(info)
            except StopValidation as e:
                logger.error(e.reasons)
                return stand_response('error', e.reasons)
            return stand_response()
        return stand_response('error', ['submit error'])


@impl(tryfirst=True)
def load_blueprints(app):
    knowledge = Blueprint("knowledge", __name__)

    register_view(
        knowledge,
        routes=['/<dac_id>'],
        view_func=KnowledgeIndex.as_view("index")
    )

    register_view(
        knowledge,
        routes=['/<dac_id>/<knowledge_id>'],
        view_func=KnowledgeDetailIndex.as_view(
            "detail",
            service_factory=add_knowledge_detail_service_factory
        )
    )

    register_view(
        knowledge,
        routes=['/<dac_id>/add'],
        view_func=KnowledgeAdd.as_view(
            "add",
            service_factory=add_knowledge_service_factory
        )
    )

    register_view(
        knowledge,
        routes=['/<knowledge_detail_id>/<join_type>/join'],
        view_func=KnowledgeJoin.as_view(
            "join",
            service_factory=join_knowledge_service_factory
        )
    )

    register_view(
        knowledge,
        routes=['/<dac_id>/<knowledge_detail_id>/info'],
        view_func=KnowledgeInfoIndex.as_view(
            "info",
            service_factory=info_edit_knowledge_service_factory
        )
    )

    register_view(
        knowledge,
        routes=['/<dac_id>/<knowledge_detail_id>/info-edit'],
        view_func=KnowledgeInfoEdit.as_view(
            "info-edit",
            service_factory=edit_knowledge_service_factory
        )
    )

    register_view(
        knowledge,
        routes=['/<knowledge_info_id>/fabulous'],
        view_func=KnowledgeInfoFabulous.as_view(
            "fabulous",
        )
    )
    register_view(
        knowledge,
        routes=['/<dac_id>/<knowledge_detail_id>/review'],
        view_func=KnowledgeReview.as_view(
            "review",
        )
    )
    register_view(
        knowledge,
        routes=['/review/<dac_id>/<knowledge_detail_id>'],
        view_func=KnowledgeReviewPass.as_view(
            "review_pass",
        )
    )
    register_view(
        knowledge,
        routes=['/<dac_id>/<knowledge_detail_id>/submit'],
        view_func=KnowledgeReviewSubmit.as_view(
            "submit",
        )
    )

    app.register_blueprint(knowledge, url_prefix="/knowledge")

