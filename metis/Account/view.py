# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: view.py
@time: 2020/5/25 10:29 上午
@desc:
"""
import logging
import json
from metis.decorators import activate_required
from flask import Blueprint, request, url_for, redirect
from flask.views import MethodView
from flask_login import login_required, logout_user
from . import impl
from .service.factory import account_registration_service, account_login_service
from .service.Registration import AccountRegisterInfo
from .service.Login import AccountSignInfo
from metis.utils.helpers import register_view, render, stand_response
from metis.Account.form import AccountRegisterForm, AccountSignForm
from metis.MetisExecption.MetisError import StopValidation, PersistenceError

logger = logging.getLogger("metis")


class AccountRegister(MethodView):

    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = AccountRegisterForm()
        form.process(request.form)
        return form

    def get(self):
        return render("account/register.html", form=self.form())

    def post(self):
        form = self.form()
        if form.validate_on_submit():
            account = AccountRegisterInfo(
                email=form.email.data,
                password=form.password.data,
                confirm_password=form.confirm_password.data
            )
            service = self.service_factory()
            try:
                service.register(account, remote_ip=request.remote_addr)
            except StopValidation as e:
                logger.error(e.reasons)
                return stand_response("error", e.reasons)
            except PersistenceError:
                logger.error("Could not persistence")
                return stand_response("error", ["Could not persistence"])
            return stand_response()
        else:
            for key, messages in form.errors.items():
                return stand_response("error", messages[0])


class AccountLogin(MethodView):

    def __init__(self, service_factory):
        self.service_factory = service_factory

    def form(self):
        form = AccountSignForm()
        form.process(request.form)
        return form

    def get(self):
        return render("account/sign.html", form=self.form())

    def post(self):
        form = self.form()
        if form.validate_on_submit():
            account = AccountSignInfo(
                email=form.email.data,
                password=form.password.data
            )
            service = self.service_factory()
            try:
                service.sign(account, request.remote_addr)
            except StopValidation as e:
                logger.error(e.reasons)
                return stand_response("error", e.reasons)
            return stand_response()
        else:
            for key, messages in form.errors.items():
                return stand_response("error", messages[0])


class AccountLogout(MethodView):

    @login_required
    def get(self):
        logout_user()
        return redirect(url_for('account.login'))


class AccountProfile(MethodView):

    @login_required
    def get(self):
        return render("account/profile.html")


@impl(tryfirst=True)
def load_blueprints(app):
    account = Blueprint("account", __name__)

    register_view(
        account,
        routes=['/register'],
        view_func=AccountRegister.as_view(
            "register",
            service_factory=account_registration_service
        )
    )
    register_view(
        account,
        routes=['/login'],
        view_func=AccountLogin.as_view(
            "login",
            service_factory=account_login_service
        )
    )
    register_view(
        account,
        routes=['/logout'],
        view_func=AccountLogout.as_view(
            "logout"
        )
    )

    app.register_blueprint(account, url_prefix="/account")

