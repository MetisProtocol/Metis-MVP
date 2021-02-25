# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: view.py
@time: 2020/5/18 12:07 下午
@desc:
"""
from metis.Activity import impl
from flask import Blueprint, abort
from flask.views import MethodView
from metis.utils.helpers import render, register_view
from flask_login import login_required, current_user
from metis.Home.model import DAC
from metis.DAC.form import ActivityDACForm


class Index(MethodView):

    @login_required
    def get(self, dac_id):
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=current_user.username, email=current_user.email)
        if not dac:
            return render("error/404.html", dac_id=dac_id, user_info=user_info)
        if not dac.dac_is_active:
            return render("error/activity_forbidden.html", dac_id=dac_id, user_info=user_info, form=ActivityDACForm())
        is_admin = True if dac.dac_admin == current_user.uid else False
        return render('activity/index.html', dac_id=dac_id, is_admin=is_admin)


@impl(tryfirst=True)
def load_blueprints(app):
    activity = Blueprint("activity", __name__)

    register_view(
        activity,
        routes=['/<dac_id>'],
        view_func=Index.as_view("index")
    )

    app.register_blueprint(activity, url_prefix="/activity")






