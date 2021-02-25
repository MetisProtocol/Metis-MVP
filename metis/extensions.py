# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: extensions.py
@time: 2020/5/8 10:33 上午
@desc:
"""
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_cors import CORS
from flask_migrate import Migrate


# mail
mail = Mail()

# CORS
cors = CORS()

# db
db = SQLAlchemy()

# Migrate
migrate = Migrate()

# CSRF Project
csrf = CSRFProtect()

# login manager
login_manager = LoginManager()



