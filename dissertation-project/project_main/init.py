import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='views', static_url_path='/', static_folder='resources')
# UPDATE SECRET KEY LATER TO BE MORE SECURE.
app.config['SECRET_KEY'] = 'f059cb01f09a4e2af642dfc0d5d64589f7ee87714659abc466ba397f549aef88'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://c2106366:KEy39JWC9Ze4TYZH@csmysql.cs.cf.ac.uk:3306/c2106366_dissertation"
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

