# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: app.py
@time: 2020/5/8 10:33 上午
@desc:
"""
import os
import ast
import sys
import time
import logging
import logging.config
from flask import Flask, abort, render_template
from sqlalchemy import event
from sqlalchemy.engine import Engine
from pluggy import PluginManager
from metis.Hooks import spec
from metis.Account.model import Account
from metis.config.Debug import DebugConfig
from metis.config.Production import ProductionConfig
from metis.Member import view
from metis.Proposal import view, plugins
from metis.Activity import view
from metis.Knowledge import view
from metis.Home import view, plugin
from metis.Account import view, plugin
from metis.SmartContract import view
from metis.API import view
from metis.DAC import view, plugins
from metis.utils.helpers import get_metis_config
from metis.extensions import (db, mail, cors, csrf, migrate, login_manager)


logger = logging.getLogger(__name__)


def create_app(config=None, app_name=None):
    app = Flask(app_name) if app_name else Flask(__name__)
    configure_app(app, config)
    configure_extensions(app)
    load_plugins(app)
    configure_blueprints(app)
    return app


def configure_app(app, config=None, env="DEBUG"):
    if env == "PRODUCTION":
        app.config.from_object("metis.config.Production.ProductionConfig")
    else:
        app.config.from_object("metis.config.Default.DefaultConfig")
    config = get_metis_config(app, config)
    if isinstance(config, str):
        app.config.from_pyfile(config)
    else:
        app.config.from_object(config)
    app.config['CONFIG_PATH'] = config

    # load cfg file from env var
    app.config.from_envvar("FLASK_ENV_NAME", silent=True)

    # load custom env var
    app_var_from_env(app, prefix='FLASK_')

    # configure logging
    configure_logging(app)
    app.pluggy = PluginManager("metis")


def configure_logging(app):
    # 如果配置中指定使用默认logging配置，就直接使用
    if app.config.get("USE_DEFAULT_LOGGING"):
        configure_default_logging(app)

    # 指定logging记录日志的文件目录
    # 如果需要自己手动设定，这里需要设定一个绝对路径
    # 默认配置为None，如果需要自己手动设定，可以继承默认设置类，然后设定一个绝对路径即可
    if app.config.get("LOG_CONF_FILE"):
        logging.config.fileConfig(
            app.config["LOG_CONF_FILE"], disable_existing_loggers=False
        )

    # 将每次的数据库操作的时间进行记录，便于做之后的性能分析
    if app.config["SQLALCHEMY_ECHO"]:
        @event.listens_for(Engine, "")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault("query_start_time", []).append(time.time())

        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - conn.info["query_start_time"].pop(-1)
            app.logger.debug("Total Time: %f", total)   # 使用flask自带的logger模块将结果输出到console


def configure_default_logging(app):
    # load default logging config
    logging.config.dictConfig(app.config["LOG_DEFAULT_CONF"])

    if app.config['SEND_LOGS']:     # default False
        pass


def configure_blueprints(app):
    app.pluggy.hook.load_blueprints(app=app)


def app_var_from_env(app, prefix="FLASK"):
    for key, value in os.environ.items():
        if key.startswith(prefix):
            key = key[len(prefix):]     # 去掉prefix
            try:
                # ast 是python的语法分析工具，用python修改python代码
                # 这里使用确保从系统环境变量中载入的变量符合python语法
                value = ast.literal_eval(value)
            except (ValueError, SyntaxError):   # 捕获value，syntax异常
                pass
            app.config[key] = value
    return app


def load_plugins(app):
    app.pluggy.add_hookspecs(spec)
    temp_modules = set(
        module
        for name, module in sys.modules.items()
        if name.startswith('metis')
    )
    for module in temp_modules:
        app.pluggy.register(module)


def configure_extensions(app):
    # db
    db.init_app(app)

    # cors
    cors.init_app(app)

    # mail
    mail.init_app(app)

    # migrate
    migrate.init_app(app, db)

    # csrf
    csrf.init_app(app)

    # flask login manager config
    login_manager.login_view = app.config["LOGIN_VIEW"]
    login_manager.session_protected = "basic"

    @login_manager.user_loader
    def load_user(id):
        instance = Account.query.filter_by(id=id).first()
        if instance:
            return instance
        else:
            abort(403)

    login_manager.init_app(app)



