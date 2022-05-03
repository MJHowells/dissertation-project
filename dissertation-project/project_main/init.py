import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='views', static_url_path='/', static_folder='resources')
app.config['SECRET_KEY'] = None #Removed for public commit (No longer active)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] = None #Removed for public commit (No longer active)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

from project_main.controllers.home import home
from project_main.controllers.account_management import account_management
from project_main.controllers.consumption_interaction import consumption_interaction

app.register_blueprint(home)
app.register_blueprint(account_management)
app.register_blueprint(consumption_interaction)

