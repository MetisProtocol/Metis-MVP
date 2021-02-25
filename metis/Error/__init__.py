# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: __init__.py.py
@time: 2020/5/30 10:43 上午
@desc:
"""
from metis.utils.helpers import render
from metis.Home.model import DAC

__all__ = ["error_handler", "dac_authentication"]


class ErrorHandler:

    mapping = {
        404: "error/404.html",
        403: "error/activity_forbidden.html"
    }

    def abort(self, status_code, **content):
        return render(self.mapping[status_code], **content)

    def __call__(self, code, **kwargs):
        return self.abort(code, **kwargs)


class DACAuthentication:

    def authentication(self, dac_id, user, form=None):
        dac = DAC.get_dac_by_id(dac_id)
        user_info = dict(username=user.username, email=user.email)
        if not dac:
            return error_handler(404, dac_id=dac_id, user_info=user_info)
        if not dac.dac_is_active:
            return error_handler(403, dac_id=dac_id, user_info=user_info, form=form)

    def __call__(self, dac_id, user, form=None):
        return self.authentication(dac_id, user, form)


def error_handler(code, **content):
    abort = ErrorHandler()
    return abort(code, **content)


def dac_authentication(dac_id, user, form=None):
    auth = DACAuthentication()
    return auth(dac_id, user, form)

