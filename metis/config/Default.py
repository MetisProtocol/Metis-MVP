# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: Default.py
@time: 2020/5/8 10:32 上午
@desc:
"""
import os
import datetime

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


# 定义一个默认的配置


class DefaultConfig:
    DEBUG = False
    PRODUCTION = False

    # The preferred url scheme. In a productive environment it is highly
    # recommended to use 'https'.
    # This only affects the url generation with 'url_for'.
    # PREFERRED_URL_SCHEME = "http"

    # Logging Config Path
    # see https://docs.python.org/library/logging.config.html#logging.config.fileConfig
    # for more details. Should either be None or a path to a file
    # If this is set to a path, consider setting USE_DEFAULT_LOGGING to False
    # otherwise there may be interactions between the log configuration file
    # and the default logging setting.
    #
    # If set to a file path, this should be an absolute file path
    LOG_CONF_FILE = None

    # Path to store the INFO and ERROR logs
    # If None this defaults to temp/logs
    #
    # If set to a file path, this should be an absolute path
    LOG_PATH = os.path.join(base_dir, 'logs')

    # logging 的字典配置
    LOG_DEFAULT_CONF = {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'standard': {
                'format': '%(asctime)s %(levelname)-7s %(name)-25s %(message)s'
            },
            'advanced': {
                'format': '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            }
        },

        'handlers': {
            'console': {
                'level': 'NOTSET',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
            'debug_log': {
                'level': 'DEBUG',
                'formatter': 'advanced',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(LOG_PATH, 'debug.log'),
                'mode': 'a',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
            },

            'info_log': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(LOG_PATH, 'info.log'),
                'mode': 'a',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
            },
            'error_log': {
                'level': 'ERROR',
                'formatter': 'advanced',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(LOG_PATH, 'error.log'),
                'mode': 'a',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
            }
        },

        'loggers': {
            'metis': {
                'handlers': ['console', 'debug_log', 'info_log', 'error_log'],
                'level': 'DEBUG',
                'propagate': True
            },
        }
    }

    # When set to True this will enable the default
    # FlaskBB logging configuration which uses the settings
    # below to determine logging
    USE_DEFAULT_LOGGING = True

    # If SEND_LOGS is set to True, the admins (see the mail configuration) will
    # recieve the error logs per email.
    SEND_LOGS = False

    # SQL Config SQLAlchemy
    SQLALCHEMY_DATABASE_URI = ""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_SIZE = 500
    SQLALCHEMY_POOL_SIZE = 500
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 300
    SQLALCHEMY_MAX_OVERFLOW = 50

    # Flask Email Config
    # MAIL_DEBUG = False
    # MAIL_SERVER = ''
    # MAIL_PORT = 465
    # MAIL_USE_SSL = True
    # MAIL_USERNAME = ''
    # MAIL_PASSWORD = ''
    # MAIL_DEFAULT_SENDER = ''
    # # send attach mime type
    # MIME_TYPE = {
    #     '.xls': 'application/vnd.ms-excel',
    #     '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    #     '.txt': 'text/plain',
    #     '.pdf': 'application/pdf',
    #     '.doc': 'application/msword',
    #     '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    #     '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    #     '.ppt': 'application/vnd.ms-powerpoint',
    #     '.rar': 'application/rar',
    #     '.zip': 'application/zip',
    #     '.tar': 'application/x-tar',
    #     '.gz': 'application/x-gzip'
    # }

    MAIL_DEBUG = True
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'mydesmond@163.com'
    MAIL_PASSWORD = 'Misswang0406'
    MAIL_DEFAULT_SENDER = 'mydesmond@163.com'
    MIME_TYPE = {
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.txt': 'text/plain',
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.rar': 'application/rar',
        '.zip': 'application/zip',
        '.tar': 'application/x-tar',
        '.gz': 'application/x-gzip'
    }

    # SECRET_KEY
    SECRET_KEY = "bXmTa2TPKjJT8h2O4Fifk0qG0JAV8gGB"

    # WTF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = "lyGaIxeA2gs8SE2uftpdsBbpdxMAPVWg"

    # Flask Login
    LOGIN_VIEW = "account.login"

    # The name of the cookie to store the “remember me” information in.
    REMEMBER_COOKIE_NAME = "remember_token"
    # The amount of time before the cookie expires, as a datetime.timedelta object.
    REMEMBER_COOKIE_DURATION = datetime.timedelta(days=365)
    # If the “Remember Me” cookie should cross domains,
    # set the domain value here (i.e. .example.com would allow the cookie
    # to be used on all subdomains of example.com).
    REMEMBER_COOKIE_DOMAIN = None
    # Limits the “Remember Me” cookie to a certain path.
    REMEMBER_COOKIE_PATH = "/"
    # Restricts the “Remember Me” cookie’s scope to secure channels (typically HTTPS).
    REMEMBER_COOKIE_SECURE = None
    # Prevents the “Remember Me” cookie from being accessed by client-side scripts.
    REMEMBER_COOKIE_HTTPONLY = False

    # Redis
    # ------------------------------ #
    # If redis is enabled, it can be used for:
    #   - Sending non blocking emails via Celery (Task Queue)
    #   - Caching
    #   - Rate Limiting
    # REDIS_ENABLED = False
    # REDIS_URL = "redis://localhost:6379"  # or with a password: "redis://:password@localhost:6379"
    # REDIS_DATABASE = 0

    # URL Prefixes

    # FORUM_URL_PREFIX = ""
    # USER_URL_PREFIX = "/user"
    # MESSAGE_URL_PREFIX = "/message"
    # AUTH_URL_PREFIX = "/auth"
    # ADMIN_URL_PREFIX = "/admin"

