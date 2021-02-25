# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: helpers.py
@time: 2020/5/8 12:47 下午
@desc:
"""
import os
import json
import hashlib
# from flask import render_template
from metis.config.Const import ENCODE_METHOD
from metis.config.Debug import DebugConfig
from string import ascii_letters
from random import randint


# def render(template, **kwargs):
#     return render_template(template, **kwargs)


def md5(*args):
    m = hashlib.md5()
    for item in args:
        if isinstance(item, (list, tuple, dict, set)):
            raise TypeError("Must be Str Object")
        m.update(str(item).encode(ENCODE_METHOD))
    return m.hexdigest()


def _gen_salt():
    words = ascii_letters + "0123456789"
    return ''.join(
        [words[randint(0, 61)] for _ in range(4)]
    )


def register_view(bp_or_app, routes, view_func, *args, **kwargs):
    for route in routes:
        bp_or_app.add_url_rule(route, view_func=view_func, *args, **kwargs)


def get_metis_config(app, config):
    if config is not None:
        # 如果给的不是一个文件名，那就是一个对象
        if not isinstance(config, str):
            return config
        if os.path.exists(config):
            return config
    else:  # 如果没有给定配置文件，使用默认的配置
        project_dir = os.path.abspath(os.path.dirname(
            os.path.dirname(__file__)))
        # 先找flask.cfg 这个文件，如果有使用这个文件
        # 如果没有就使用flask自己的配置就好
        project_default_cfg = os.path.join(project_dir, 'metis.cfg')
        if os.path.exists(project_default_cfg):
            return project_default_cfg
        else:
            return DebugConfig  # 返回默认的配置对象
    return


def stand_response(tpe='normal', message=["error"], content=None):
    if tpe == 'normal':
        return json.dumps(
            {
                'code': "ok",
                'message': "ok",
                "content": content
            }
        )
    else:
        return json.dumps(
            {
                'code': "error",
                'message': message,
                "content": content
            }
        )


def api_stand_response(tpe="normal", description="ok", content=None):
    if tpe == 'normal':
        return json.dumps(
            {
                'status_code': 200,
                "description": description,
                "content": content
            }
        )
    else:
        return json.dumps(
            {
                'status_code': 400,
                'description': description
            }
        )

if __name__ == '__main__':
    print(md5('LoNl', '000000'))
    # 1bfc2bccef984975e6f0257b174dc4f1