# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: api.py
@time: 2020/5/27 2:47 下午
@desc:
"""
from . import impl
from flask import request, Blueprint
from flask.views import MethodView
from metis.utils.helpers import api_stand_response, register_view


class UserProfile(MethodView):

    def get(self):
        skill_set = [
            "str_items"
        ]
        language = ["language_items"]
        content = dict(
            id=str,
            name=str,
            email=str,
            metainfo=str,
            balance=str,
            level=int,
            skillset=skill_set,
            language=language
        )
        return api_stand_response(content=content)


class UserEngagements(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class UserStakes(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class EngagementCommit(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class EngagementFinish(MethodView):
    def get(self):
        pass

    def post(self):
        pass


class EngagementReview(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class EngagementDispute(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class EngagementDismissDispute(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class EngagementArbitrate(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class UserRegister(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class UserExit(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class Engagements(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class Stakes(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class StakeCommit(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class StakeTerminate(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class StakeWithdraw(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class StakeDispute(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class StakeDismissDispute(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class StakeArbitrate(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class Assets(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class UserAssets(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class AssetRequest(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class Asset(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class EngagementClose(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class EngagementRequestArbitration(MethodView):

    def get(self):
        pass

    def post(self):
        pass


class StakeRequestArbitration(MethodView):

    def get(self):
        pass

    def post(self):
        pass


@impl(tryfirst=True)
def load_blueprints(app):
    api = Blueprint("api", __name__)

    register_view(
        api,
        routes=['/userprofile'],
        view_func=UserProfile.as_view("user_profile")
    )
    register_view(
        api,
        routes=['/userengagements'],
        view_func=UserEngagements.as_view("user_engagements")
    )

    app.register_blueprint(api, url_prefix="/api/v1")




