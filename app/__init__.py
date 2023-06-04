from flask import Flask
#import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY']= 'd46779c015167125cc6c76194f2c5a38'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'


# def db_init(app):
#     db.init_app(app)

#     with app.app_context():
#         db.create_all()

from app import routes

