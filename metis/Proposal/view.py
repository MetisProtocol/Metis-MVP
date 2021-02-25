# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: view.py
@time: 2020/5/11 11:23 上午
@desc:
"""
import logging
import json
import datetime
from flask import Blueprint, request
from flask.views import MethodView
from flask_login import login_required, current_user
from . import impl
from .form import (AddProposalForm, ExcitationClaimProposalForm, ClaimPromiseForm, PublisherClaimPromiseForm,
                   ProposalSubmitForm, WorkInfoForm)
from .model import Work, WorkInfo
from .service.add_proposal import AddProposalInfo
from .service.claim_excitation import ClaimExcitationInfo
from .service.claim_promise import ClaimPromiseInfo
from .service.first_promise import FirstPromiseInfo
from .service.settlement import SettlementInfo
from .service.submit import SubmitProposalInfo
from .service.publisher_claim_promise import PublisherClaimPromiseInfo
from .service.review import ReviewProposalInfo
from .service.factories import (add_work_service_factory, claim_excitation_service_factory,
                                claim_promise_service_factory, first_promise_service_factory,
                                publisher_claim_promise_service_factory, submit_service_factory,
                                review_service_factory, settlement_service_factory)
from metis.utils.helpers import register_view, render, stand_response
from metis.Home.model import DAC
from metis.SmartContract.model import MSCTable
from metis.Account.model import Account
from metis.DAC.form import ActivityDACForm
from metis.Error import error_handler
from metis.MetisExecption.MetisError import StopValidation, PersistenceError, EthError, FirstClaimPromiseError
from metis.SmartContract.contracts import MToken

logger = logging.getLogger("metis")


class ProposalIndex(MethodView):
    def __init__(self):
        pass

    @login_required
    def get(self, dac_id):
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email)
        if not dac:
            return error_handler(404, dac_id=dac_id, user_info=user_info)
        if not dac.dac_is_active:
            return error_handler(403, dac_id=dac_id, user_info=user_info, form=ActivityDACForm())
        is_admin = True if dac.dac_admin == current_user.uid else False
        status = request.args.get('status')
        if status == '0':
            all_work_list, state_statistics = self.build_work_list(dac_id, int(status))
            return render('proposal/index.html', dac_id=dac_id, user_info=user_info, is_admin=is_admin,
                          all_work_list=all_work_list, state_statistics=state_statistics, claim_form=ClaimPromiseForm())
        elif status == '1':
            all_work_list, state_statistics = self.build_work_list(dac_id, int(status))
            return render('proposal/index.html', dac_id=dac_id, user_info=user_info, is_admin=is_admin,
                          all_work_list=all_work_list, state_statistics=state_statistics, claim_form=ClaimPromiseForm())
        elif status == '2':
            all_work_list, state_statistics = self.build_work_list(dac_id, int(status))
            return render('proposal/index.html', dac_id=dac_id, user_info=user_info, is_admin=is_admin,
                          all_work_list=all_work_list, state_statistics=state_statistics, claim_form=ClaimPromiseForm())
        elif status == '3':
            all_work_list, state_statistics = self.build_work_list(dac_id, int(status))
            return render('proposal/index.html', dac_id=dac_id, user_info=user_info, is_admin=is_admin,
                          all_work_list=all_work_list, state_statistics=state_statistics, claim_form=ClaimPromiseForm())
        elif status == '6':
            all_work_list, state_statistics = self.build_work_list(dac_id, int(status))
            return render('proposal/index.html', dac_id=dac_id, user_info=user_info, is_admin=is_admin,
                          all_work_list=all_work_list, state_statistics=state_statistics, claim_form=ClaimPromiseForm())
        else:
            all_work_list, state_statistics = self.build_work_list(dac_id)
            return render('proposal/index.html', dac_id=dac_id, user_info=user_info, is_admin=is_admin,
                          all_work_list=all_work_list, state_statistics=state_statistics, claim_form=ClaimPromiseForm())

    def build_work_list(self, dac_id, status=None):
        works = Work.get_all_available_works(dac_id)
        state_statistics = self.build_state_statistics(works)
        if status is None:
            all_work_list = []
            for work in works:
                all_work_list.append(
                    self.build_work_content(work)
                )
            return all_work_list, state_statistics
        else:
            all_work_list = []
            for work in works:
                if work.work_status == status:
                    all_work_list.append(
                       self.build_work_content(work)
                    )
        return all_work_list, state_statistics

    @staticmethod
    def build_work_content(work):
        publisher_promise = False
        if work.participants:   # participants party_a publisher party_b
            msc_record = MSCTable.query.filter(
                MSCTable.msc_type == 'PROMISE',
                MSCTable.is_effective == 1,
                MSCTable.msc_status == 1,
                MSCTable.party_a == work.participants,
                MSCTable.party_b == work.publisher
            ).first()
            if msc_record:
                if msc_record.msc_status == 1:  # 0 申领方激活 1 双方都激活，并且有效 2 之后都属于无效状态
                    publisher_promise = True
        return {
            'work_id': work.work_id,
            'work_ctime': work.ctime,
            'work_name': work.work_name,
            'work_status': work.work_status,
            'work_excitation': work.work_excitation,
            'work_deadline': work.work_deadline,
            'work_participants': work.participants,
            "work_describe": work.work_describe,
            'work_publisher': work.publisher,
            'publisher_promise': publisher_promise
        }
    # 查找所有已经被申领的任务，查找申领方和admin的promise合约状态是否是msc_status=1，如果不是，提示admin质押

    @staticmethod
    def build_state_statistics(works):
        undo = 0
        exc = 0
        review = 0
        finish = 0
        for work in works:
            if work.work_status == 0:
                undo += 1
            elif work.work_status == 1:
                exc += 1
            elif work.work_status == 2:
                review += 1
            elif work.work_status == 6:
                finish += 1
        return {
            "undo": undo,
            "exec": exc,
            "review": review,
            "finish": finish
        }


class ProposalAdd(MethodView):
    WIKI_BASE_URI = "http://wiki.metis.apple-store-signature.com/index.php/"

    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = AddProposalForm()
        form.process(request.form)
        return form

    @login_required
    def post(self, dac_id):
        form = self.form()
        if form.validate_on_submit():
            days = (datetime.datetime.strptime(form.work_expiry.data, '%Y-%m-%d') - datetime.datetime.now()).days
            if days <= 0:
                return stand_response("error", ['请输入正确的截止日期'])
            service = self.service_factory()
            work_info = AddProposalInfo(
                dac_id=dac_id,
                work_name=form.work_name.data,
                work_describe=self.WIKI_BASE_URI + form.work_name.data,
                work_excitation=form.work_excitation.data,
                work_deadline=form.work_expiry.data,
                work_expiry=days,
                publisher_uid=current_user.uid
            )
            try:
                service.add(work_info, current_user)
            except StopValidation as e:
                logger.error(e.reasons)
                return stand_response("error", e.reasons)
            except EthError as e:
                logger.error(e.reason)
                return stand_response('error', [e.reason])
            except PersistenceError:
                logger.error("Could not persistence work")
                return stand_response("error", ["Could not persistence work"])
            return stand_response()
        for key, messages in form.errors.items():
            print(messages[0])
            print("=====================")
        print("==================")
        return stand_response("error", [messages[0]])

    @login_required
    def get(self, dac_id):
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email)
        if not dac:
            return error_handler(404, dac_id=dac_id, user_info=user_info)
        if not dac.dac_is_active:
            return error_handler(403, dac_id=dac_id, user_info=user_info, form=ActivityDACForm())
        is_admin = True if dac.dac_admin == current_user.uid else False
        return render("proposal/add.html", dac_id=dac_id, is_admin=is_admin, user_info=user_info, form=self.form())


class ProposalPublished(MethodView):

    def __init__(self):
        pass

    @login_required
    def get(self, dac_id):
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email)
        if not dac:
            return error_handler(404, dac_id=dac_id, user_info=user_info)
        if not dac.dac_is_active:
            return error_handler(403, dac_id=dac_id, user_info=user_info, form=ActivityDACForm())
        is_admin = True if dac.dac_admin == current_user.uid else False
        published_works = Work.get_published_works(current_user.uid, dac_id)
        work_status_badge = {
            0: "badge-info",
            1: "badge-danger",
            2: "badge-warning",
            3: "badge-warning",
            4: "badge-warning",
            5: "badge-warning",
            6: "badge-success"
        }
        work_status_describe = {
            0: "未开始",
            1: "进行中",
            2: "待审核",
            3: "待结算",
            4: "待发布方结算",
            5: "待申领方结算",
            6: "已完成"
        }
        works = [
            {
                "work_id": work.work_id,
                "work_name": work.work_name,
                "work_ctime": work.ctime,
                "work_status": work.work_status,
                "status_cls": work_status_badge[work.work_status],
                "work_excitation": work.work_excitation,
                "work_describe": work.work_describe,
                "is_active": work.is_active,
                "review": 1 if work.work_status == 2 else 0,
                "status_describe": work_status_describe[work.work_status],
                'is_promise': self._is_promised(work),
                'work_publisher': work.publisher,
                'work_participants': work.participants,
            }
            for work in published_works
        ]
        return render("proposal/published.html", dac_id=dac_id, is_admin=is_admin, user_info=user_info, works=works,
                      excitation_form=ExcitationClaimProposalForm(),
                      publisher_claim_promise_form=PublisherClaimPromiseForm())

    def _is_promised(self, work):
        if work.participants:  # participants party_a publisher party_b
            msc_record = MSCTable.query.filter(
                MSCTable.msc_type == 'PROMISE',
                MSCTable.is_effective == 1,
                MSCTable.party_a == work.participants,
                MSCTable.party_b == work.publisher
            ).first()
            if msc_record:
                if msc_record.msc_status == 1:  # 0 申领方激活 1 双方都激活，并且有效 2 之后都属于无效状态
                    return True
        return False


class ExcitationClaim(MethodView):

    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = ExcitationClaimProposalForm()
        form.process(request.form)
        return form

    @login_required
    def post(self):
        form = self.form()
        if form.validate_on_submit():
            # 工场函数
            service = self.service_factory()
            # 查出账户余额
            balance = MToken().get_balance(current_user.eth_addr)
            # 查出激励
            excitation = Work.get_excitation_by_work_id(form.active_work_id.data)
            work = Work.get_work_by_work_id(form.active_work_id.data)
            try:
                info = ClaimExcitationInfo(
                    # dac id
                    dac_id=form.active_dac_id.data,
                    # work _id
                    work_id=form.active_work_id.data,
                    current_user=current_user.uid,
                    excitation=excitation,
                    balance=balance,
                    user_eth=current_user.eth_addr,
                    work_describe=work.work_describe

                )
                service.claim(info)
            except StopValidation as e:
                logger.error(e.reasons)
                return stand_response('error', e.reasons)
            except EthError as e:
                logger.error(e.reason)
                return stand_response('error', [e.reason])
            except PersistenceError:
                logger.error("Could not persistence claim excitation info")
                return stand_response('error', ['Could not persistence claim excitation info'])
            return stand_response()
        return stand_response('error', ['submit error'])


class ProposalGet(MethodView):
    """
    显示接收方已经获取到的所有的任务信息，任务提交是否需要在这里设置为一个弹窗？或者直接使用之前的提交页面
    """

    def __init__(self):
        pass

    def form(self):
        form = ""
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
        received_works = Work.get_received_works(current_user.uid, dac_id)
        works = [
            {
                "work_id": received_work.work_id,
                "work_name": received_work.work_name,
                "work_ctime": received_work.ctime,
                "work_status": received_work.work_status,
                "work_describe": received_work.work_describe,
                "publisher_promise": self._publisher_promise(received_work)
            }
            for received_work in received_works
        ]
        return render("proposal/get.html", dac_id=dac_id, is_admin=is_admin, user_info=user_info, works=works,
                      excitation_form=ExcitationClaimProposalForm())

    @staticmethod
    def _publisher_promise(work):
        publisher_promise = False
        if work.participants:
            msc_record = MSCTable.query.filter(
                MSCTable.msc_type == 'PROMISE',
                MSCTable.is_effective == 1,
                MSCTable.msc_status == 1,
                MSCTable.party_a == work.participants,
                MSCTable.party_b == work.publisher
            ).first()
            if msc_record:
                if msc_record.msc_status == 1:  # 0 申领方激活 1 双方都激活，并且有效 2 之后都属于无效状态
                    publisher_promise = True
        return publisher_promise


class FirstClaimPromise(MethodView):
    """
    任务接收方首次进行保证金的质押操作
    """

    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = ClaimPromiseForm()
        form.process(request.form)
        return form

    @login_required
    def post(self):
        form = self.form()
        token = MToken()
        if form.validate_on_submit():
            publisher = Account.get_user_by_uid(form.publisher.data)
            info = FirstPromiseInfo(
                current_user_uid=current_user.uid,
                publisher_uid=form.publisher.data,
                balance=token.get_balance(current_user.eth_addr),
                work_id=form.work_id.data,
                current_user_eth=current_user.eth_addr,
                publisher_eth=publisher.eth_addr if publisher else ""
            )
            service = self.service_factory()
            try:
                service.claim(info)
            except StopValidation as e:
                logger.error(e.reasons)
                return stand_response('error', ['账户余额不足，请充值'])
            except PersistenceError:
                logger.error("Persistence Error")
                return stand_response('error', ['Persistence error'])
            except EthError as e:
                logger.error(e)
                logger.error("Eth Error")
                return stand_response('error', ['ETH error'])
            return stand_response()
        else:
            for key, messages in form.errors.items():
                print(messages[0])
        return stand_response('error', ['submit error'])


class ClaimPromise(MethodView):
    """
    需要修改类名，这个是takeTask 进行任务接收的 TODO
    """

    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = ClaimPromiseForm()
        form.process(request.form)
        return form

    def post(self):
        form = self.form()
        token = MToken()
        if form.validate_on_submit():
            publisher = Account.get_user_by_uid(form.publisher.data)
            work = Work.get_work_by_work_id(form.work_id.data)
            info = ClaimPromiseInfo(
                current_user_uid=current_user.uid,
                current_user_eth=current_user.eth_addr,
                work_id=form.work_id.data,
                publisher_uid=form.publisher.data,
                balance=token.get_balance(current_user.eth_addr),
                publisher_eth=publisher.eth_addr,
                excitation=work.work_excitation
            )
            service = self.service_factory()
            try:
                service.claim(info)
            except StopValidation as e:
                logger.error(e.reasons)
                return stand_response('error', e.reasons)
            except PersistenceError:
                logger.error('persistence error')
                return stand_response('error', ['persistence error'])
            except EthError as e:
                logger.error('eth error', e.reason)
                return stand_response('error', ['账户余额不足，请充值'])
            except FirstClaimPromiseError:
                return stand_response(content={'is_first': True})
            return stand_response()
        return stand_response('error', ['submit error'])


class PublisherClaimPromise(MethodView):
    """
    任务发布方进行首次保证金的质押操作
    """

    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = PublisherClaimPromiseForm()
        form.process(request.form)
        return form

    @login_required
    def post(self):
        token = MToken()
        form = self.form()
        if form.validate_on_submit():
            publisher = Account.get_user_by_uid(form.publisher.data)
            info = PublisherClaimPromiseInfo(
                current_user_uid=current_user.uid,
                current_user_eth=current_user.eth_addr,
                publisher_uid=form.publisher.data,
                publisher_eth=publisher.eth_addr,
                balance=token.get_balance(current_user.eth_addr),
                participants=form.participants.data
            )
            service = self.service_factory()
            try:
                service.claim(info)
            except StopValidation as e:
                return stand_response('error', e.reasons)
            except PersistenceError:
                return stand_response('error', ['persistence error'])
            return stand_response()
        return stand_response('error', ['submit error'])


class ProposalSubmit(MethodView):

    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = ProposalSubmitForm()
        form.process(request.form)
        return form

    @login_required
    def get(self, dac_id, work_id):
        work = Work.get_work_by_work_id(work_id)
        if not work:
            pass    # 404
        wiki_uri = work.work_describe
        return render("proposal/submit.html", dac_id=dac_id, work_id=work_id, wiki_uri=wiki_uri, form=self.form())

    @login_required
    def post(self, dac_id, work_id):
        form = self.form()
        if form.validate_on_submit():
            # content = form.content.data.replace("content=", "")
            # content = self._parser_submit_content(content)
            info = SubmitProposalInfo(
                # content=content,
                work_id=work_id,
                current_eth=current_user.eth_addr
            )
            service = self.service_factory()
            try:
                service.submit(info)
            except PersistenceError as e:
                return stand_response('error', ['persistence error'])
            # print(self._parser_submit_content(content))
            return stand_response()
        return stand_response('error', ['submit error'])

    @staticmethod
    def _parser_submit_content(content):
        line = ''
        next_text = ''
        for word in content + "\n":
            if word == '\n':
                next_text += line + '\r\n\r\n'
                line = ''
            else:
                line += word
        return next_text


class ProposalReview(MethodView):
    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = ExcitationClaimProposalForm()
        form.process(request.form)
        return form

    @login_required
    def post(self):
        form = self.form()
        if form.validate_on_submit():
            print("11111111111111")
            print(form.active_work_id.data)
            print("11111111111111")
            info = ReviewProposalInfo(
                work_id=form.active_work_id.data,
                publisher_eth=current_user.eth_addr
            )
            service = self.service_factory()
            try:
                service.review(info)
            except StopValidation as e:
                logger.error(e.reasons)
                return stand_response('error', e.reasons)
            except PersistenceError:
                logger.error('persistence error')
                return stand_response('error', ['persistence error'])
            except EthError as e:
                logger.error('eth error', e.reason)
                return stand_response('error', ['账户余额不足，请充值'])
            return stand_response()
        return stand_response('error', ['submit error'])


class ProposalSettlement(MethodView):
    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = ExcitationClaimProposalForm()
        form.process(request.form)
        return form

    @login_required
    def post(self):
        form = self.form()
        if form.validate_on_submit():
            work = Work.get_work_by_work_id(form.active_work_id.data)
            party_a = Account.get_user_by_uid(work.publisher)
            party_b = Account.get_user_by_uid(work.participants)
            info = SettlementInfo(
                work_id=form.active_work_id.data,
                current_eth=current_user.eth_addr,
                publisher_eth=party_a.eth_addr,
                participants_eth=party_b.eth_addr
            )
            service = self.service_factory()
            try:
                service.settlement(info)
            except StopValidation as e:
                logger.error(e.reasons)
                return stand_response('error', e.reasons)
            except PersistenceError:
                logger.error('persistence error')
                return stand_response('error', ['persistence error'])
            except EthError as e:
                logger.error('eth error', e.reason)
                return stand_response('error', ['账户余额不足， 请充值'])
            return stand_response()
        return stand_response('error', ['submit error'])


class ProposalWork(MethodView):
    def __init__(self):
        pass

    def form(self):
        form = WorkInfoForm()
        form.process(request.form)
        return form

    def get(self, dac_id, work_id):
        work = Work.get_work_by_work_id(work_id)
        work_info = WorkInfo.get_work_info_by_work_id(work_id)
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email)
        if not dac:
            return error_handler(404, dac_id=dac_id, user_info=user_info)
        if not dac.dac_is_active:
            return error_handler(403, dac_id=dac_id, user_info=user_info, form=ActivityDACForm())
        is_admin = True if dac.dac_admin == current_user.uid else False
        links = json.loads(work_info.enclosure)['links'] if work_info.enclosure else ''
        names = json.loads(work_info.enclosure)['names'] if work_info.enclosure else ''
        sizes = json.loads(work_info.enclosure)['sizes'] if work_info.enclosure else ''
        members_logo = {member.uid: member.logo for member in Account.query.all()}
        return render("proposal/work.html", dac_id=dac_id, is_admin=is_admin, user_info=user_info, work=work,
                      work_info=work_info, form=ProposalSubmitForm(), links=links, names=names, sizes=sizes,
                      members_logo=members_logo)


class ProposalWorkEdit(MethodView):
    def __init__(self):
        pass

    def form(self):
        form = WorkInfoForm()
        form.process(request.form)
        return form

    def post(self, dac_id, work_id):
        form = self.form()
        if form.validate_on_submit():
            work_info = WorkInfo.get_work_info_by_work_id(work_id)
            if form.work_type.data == 'describe':
                work_info.work_describe = form.work_memo.data
                work_info.utime = datetime.datetime.now()
                work_info.save()
            elif form.work_type.data == 'memo':
                work_info.work_memo = form.work_memo.data
                work_info.enclosure = form.enclosure.data
                work_info.utime = datetime.datetime.now()
                work_info.save()
            return stand_response()
        return stand_response('error', ['submit error'])

    def get(self, dac_id, work_id):
        work_type = request.args.get("work_type", '')
        work_info = WorkInfo.get_work_info_by_work_id(work_id)
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email)
        if not dac:
            return error_handler(404, dac_id=dac_id, user_info=user_info)
        if not dac.dac_is_active:
            return error_handler(403, dac_id=dac_id, user_info=user_info, form=ActivityDACForm())
        is_admin = True if dac.dac_admin == current_user.uid else False
        links = json.loads(work_info.enclosure)['links'] if work_info.enclosure else ''
        names = json.loads(work_info.enclosure)['names'] if work_info.enclosure else ''
        sizes = json.loads(work_info.enclosure)['sizes'] if work_info.enclosure else ''

        return render("proposal/work_edit.html", dac_id=dac_id, is_admin=is_admin, user_info=user_info,
                      work_type=work_type, work_info=work_info, form=self.form(), links=links, names=names, sizes=sizes)



@impl(tryfirst=True)
def load_blueprints(app):
    proposal = Blueprint("proposal", __name__)

    register_view(
        proposal,
        routes=['/<dac_id>'],
        view_func=ProposalIndex.as_view(
            "index"
        )
    )
    register_view(
        proposal,
        routes=['/<dac_id>/add'],
        view_func=ProposalAdd.as_view(
            "add",
            service_factory=add_work_service_factory
        )
    )
    register_view(
        proposal,
        routes=['/<dac_id>/published'],
        view_func=ProposalPublished.as_view("published")
    )
    register_view(
        proposal,
        routes=['/<dac_id>/get'],
        view_func=ProposalGet.as_view("get")
    )
    register_view(
        proposal,
        routes=['/claim_excitation'],
        view_func=ExcitationClaim.as_view(
            "claim_excitation",
            service_factory=claim_excitation_service_factory
        )
    )
    register_view(
        proposal,
        routes=['/first_promise'],
        view_func=FirstClaimPromise.as_view(
            "first_promise",
            service_factory=first_promise_service_factory
        )
    )
    register_view(
        proposal,
        routes=['/promise'],
        view_func=ClaimPromise.as_view(
            "promise",
            service_factory=claim_promise_service_factory
        )
    )
    register_view(
        proposal,
        routes=['/publisher_promise'],
        view_func=PublisherClaimPromise.as_view(
            "publisher_promise",
            service_factory=publisher_claim_promise_service_factory
        )
    )
    register_view(
        proposal,
        routes=['/<dac_id>/<work_id>/submit'],
        view_func=ProposalSubmit.as_view(
            "submit",
            service_factory=submit_service_factory
        )
    )
    register_view(
        proposal,
        routes=['/review'],
        view_func=ProposalReview.as_view(
            "review",
            service_factory=review_service_factory
        )
    )
    register_view(
        proposal,
        routes=['/settlement'],
        view_func=ProposalSettlement.as_view(
            "settlement",
            service_factory=settlement_service_factory
        )
    )
    register_view(
        proposal,
        routes=['/<dac_id>/<work_id>/info'],
        view_func=ProposalWork.as_view(
            "work_info",
            # service_factory=settlement_service_factory
        )
    )
    register_view(
        proposal,
        routes=['/<dac_id>/<work_id>/edit'],
        view_func=ProposalWorkEdit.as_view(
            "work_edit",
            # service_factory=settlement_service_factory
        )
    )

    app.register_blueprint(proposal, url_prefix="/proposal")

