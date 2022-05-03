from enum import unique
from os import stat
from re import M

from flask_login.utils import login_user, logout_user
from sqlalchemy.sql.elements import Null
from project_main.init import db
from project_main.init import login_manager
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
from project_main.models.media import Media
from project_main.models.goals import Goals

import sys


# User Table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), unique=False, nullable=False)
    last_name = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    media_types = db.Column(db.String(256))


    @staticmethod
    # Facilitates a query of all users.
    def search_all():
        return db.session.query(User).all()

    # Facilitates a query of a specific user by id
    def search_account_by_id(id):
        return db.session.query(User).get(id)

    # Facilitates a query of a specific user by email
    def search_account_by_email(email):
        return db.session.query(User).filter_by(email=email).first()

    # Facilitates the updating of account details
    def update_account(id, password):
        user = User.query.get(id)
        user.password_hash = generate_password_hash(password)
        db.session.commit()    

    # Facilitates the updating of users selected media types
    def update_media_types(self, media_types):
        user = User.query.get(self.id)
        user.media_types = json.dumps(media_types)
        db.session.commit()
    
    # Facilitates the querying of the database to get users seleced media types.
    def get_media_types(self):
        user = User.query.get(self.id)
        return json.loads(user.media_types)

    # Facilitates the checking of a provided password against the databases hash value.
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Facilitates the comparing of two passwords to see that they are the same.
    def check_new_password(new_password, confirm_new):
        return new_password == confirm_new
    
    # Facilitates the creation of a new user account, and its addition to the database.
    def create_account(email, first_name, last_name, password, media_types):
        user = User(email=email.lower(), first_name=first_name, last_name=last_name, password_hash=generate_password_hash(password), media_types=json.dumps(media_types))
        if '@' in email:
            if '.' in email:
                db.session.add(user)
                db.session.commit()
                login_user(user)
                user = db.session.query(User).filter_by(email=email).first()
                Media.new_user_media(user)
                Goals.generate_db(user)

    # Facilitates the deletion of a users account.
    def delete_account(self):
        logout_user()
        db.session.delete(self)
        db.session.commit()

    # Facilitates the checking of the database to identify whether an email has already been used.
    def check_unique_email(email):
        return db.session.query(User).filter_by(email=email).first()
        

# # Loads user using user_id. (Required for flask login to work.)
@login_manager.user_loader
def load_user(id):
   return User.query.get(int(id))
