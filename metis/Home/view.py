# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: view.py
@time: 2020/5/18 2:49 下午
@desc:
"""
import json
import logging
import os
import time
from flask import Blueprint, request, abort, current_app
from flask.views import MethodView
from flask_login import login_required, current_user
from metis.Home import impl
from metis.Home.form import GenerateDACForm, JoinToDACForm
from metis.utils.helpers import render, register_view, stand_response
from metis.Home.service.registration import GenerateDACInfo
from metis.MetisExecption.MetisError import StopValidation, PersistenceError
from metis.SmartContract import MToken, TaskList
from metis.Home.service.factories import metis_dac_generate_service_factory, metis_join_to_dac_service_factory
from .model import DAC
from metis.DAC.form import ActivityDACForm
from metis.Account.model import Account
from metis.extensions import csrf

logger = logging.getLogger(__name__)


class DACIndex(MethodView):

    def __init__(self):
        pass

    @login_required
    def get(self):
        account_dac = json.loads(current_user.dac) if current_user.dac else []
        dac_set = [
            {
                "dac_name": item.dac_name,
                "dac_id": item.dac_id,
                "is_belong": True if item.dac_id in account_dac else False,
                "dac_logo": item.dac_logo
            }
            for item in DAC.get_all_effective_dac()
        ]
        user_info = dict(username=current_user.username, email=current_user.email)
        return render("Home/index.html", dac_set=dac_set, user_info=user_info)


class CreatedDAC(MethodView):

    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = JoinToDACForm()
        form.process(request.form)
        return form

    @login_required
    def get(self):
        dac_set = [
            {
                "dac_name": item.dac_name,
                "dac_id": item.dac_id,
                "is_active": True if item.dac_is_active else False,
                "dac_logo": item.dac_logo
            }
            for item in DAC.get_all_dac_by_admin(current_user.uid)
        ]
        user_info = dict(username=current_user.username, email=current_user.email)
        return render("Home/created.html", dac_set=dac_set, user_info=user_info, form=ActivityDACForm())

    @login_required
    def post(self):
        form = self.form()
        dac = DAC.get_dac_by_id(form.dac_id.data)
        dac.dac_is_active = 1
        dac.save()
        task_list = TaskList()
        task_list._add_task_owner(current_user.eth_addr)
        return stand_response()


class JoinedDAC(MethodView):

    @login_required
    def get(self):
        account_dac = json.loads(current_user.dac) if current_user.dac else []
        dac_set = [
            {
                "dac_name": item.dac_name,
                "dac_id": item.dac_id,
                "is_joined": True if item.dac_id in account_dac and item.dac_admin != current_user.uid else False,
                "dac_logo": item.dac_logo
            }
            for item in DAC.get_all_effective_dac()
        ]
        user_info = dict(username=current_user.username, email=current_user.email)
        return render("Home/joined.html", dac_set=dac_set, user_info=user_info)


class DACProfile(MethodView):

    @login_required
    def get(self):
        token = MToken()
        balance = token.get_balance(current_user.eth_addr)
        eth_balance = token.web3.eth.getBalance(current_user.eth_addr)
        user_info = dict(
            username=current_user.username,
            email=current_user.email,
            eth_addr=current_user.eth_addr,
            eth_balance=eth_balance,
            balance=balance
        )
        return render("Home/profile.html", user_info=user_info)


class GenerateDAC(MethodView):

    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = GenerateDACForm()
        form.process(request.form)
        return form

    @login_required
    def get(self):
        return render('Home/generate.html', form=self.form())

    @login_required
    def post(self):
        form = self.form()
        generate_info = GenerateDACInfo(
            dac_name=form.dac_name.data,
            dac_description=form.dac_describe.data,
            dac_logo=form.file.data
        )
        service = self.service_factory()
        if form.validate_on_submit():
            try:
                dac = service.register(generate_info, current_user)
            except StopValidation as e:
                logger.error(e)
                return stand_response("error", e.reasons)
            except PersistenceError as e:
                logger.error(e)
                return stand_response("error", ['Could not persistence'])
            return stand_response(content={"dac_id": dac.dac_id})
        return stand_response("error", ['Submit Error'])


class JoinToDAC(MethodView):

    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = JoinToDACForm()
        form.process(request.form)
        return form

    @login_required
    def get(self):
        dac_set = [
            {
                "dac_id": item.dac_id,
                "dac_name": item.dac_name,
                "dac_desc": item.dac_description
            }
            for item in DAC.get_all_effective_dac()
        ]
        return render("Home/join_to_dac.html", form=self.form(), dac_set=dac_set)

    @login_required
    def post(self):
        form = self.form()
        if form.validate_on_submit():
            service = self.service_factory()
            try:
                dac = service.join(form.dac_id.data, current_user)
            except PersistenceError as e:
                logger.error(e)
                return stand_response("error", [e])
            return stand_response(content=dict(dac_id=dac.dac_id))
        return stand_response("error", ['submit error'])


class FileDAC(MethodView):
    def __init__(self):
        pass

    # @csrf.exempt
    @login_required
    def post(self):
        try:
            f = request.files['Filedata']
        except KeyError:
            f = request.files['file']
        real_name = f.filename
        print("{}".format(os.path.dirname(current_app.instance_path)))
        # 这个路径是正解
        uploads_directory = os.path.dirname(current_app.instance_path) + '/metis/static/uploads/'
        print("上传文件夹{}".format(uploads_directory))

        filename = f.filename
        name = str(int(round(time.time() * 1000)))
        ext = filename.split('.')[1]
        filename = name + '.' + ext

        local_file = os.path.join(uploads_directory, filename)
        print(local_file)
        f.save(local_file)

        return json.dumps(filename)


class FileAccount(MethodView):
    def __init__(self):
        pass

    # @csrf.exempt
    @login_required
    def post(self):
        try:
            f = request.files['Filedata']
        except KeyError:
            f = request.files['file']
        real_name = f.filename
        print("{}".format(os.path.dirname(current_app.instance_path)))
        # 这个路径是正解
        uploads_directory = os.path.dirname(current_app.instance_path) + '/metis/static/uploads/'
        print("上传文件夹{}".format(uploads_directory))

        filename = f.filename
        name = str(int(round(time.time() * 1000)))
        ext = filename.split('.')[1]
        filename = name + '.' + ext

        local_file = os.path.join(uploads_directory, filename)
        print(local_file)
        f.save(local_file)
        account = Account.get_user_by_uid(current_user.uid)
        account.logo = filename
        account.save()

        return json.dumps(filename)


class AccountBalance(MethodView):
    def __init__(self):
        pass

    @login_required
    def get(self):
        token = MToken()
        balance = token.get_balance(current_user.eth_addr)
        return json.dumps(balance)


@impl(tryfirst=True)
def load_blueprints(app):
    home = Blueprint("home", __name__)

    register_view(
        home,
        routes=['/'],
        view_func=DACIndex.as_view("index")
    )
    register_view(
        home,
        routes=['/joined'],
        view_func=JoinedDAC.as_view(
            "joined"
        )
    )
    register_view(
        home,
        routes=['/created'],
        view_func=CreatedDAC.as_view(
            "created",
            service_factory=''
        )
    )
    register_view(
        home,
        routes=['/profile'],
        view_func=DACProfile.as_view(
            "profile"
        )
    )
    register_view(
        home,
        routes=['/generate'],
        view_func=GenerateDAC.as_view(
            "generate",
            service_factory=metis_dac_generate_service_factory
        )
    )
    register_view(
        home,
        routes=['/register'],
        view_func=JoinToDAC.as_view(
            "register",
            service_factory=metis_join_to_dac_service_factory
        )
    )
    register_view(
        home,
        routes=['/file'],
        view_func=FileDAC.as_view(
            "file"
        )
    )
    register_view(
        home,
        routes=['/file_account'],
        view_func=FileAccount.as_view(
            "file_account"
        )
    )
    register_view(
        home,
        routes=['/balance'],
        view_func=AccountBalance.as_view(
            "balance"
        )
    )

    app.register_blueprint(home, url_prefix="")


