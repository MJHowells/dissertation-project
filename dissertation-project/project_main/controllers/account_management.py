from flask import Blueprint, render_template, redirect, url_for
from flask.helpers import flash
from flask_login import current_user, login_user, logout_user
from werkzeug.security import generate_password_hash
from project_main.init import db
from flask.globals import request
import json
import sys

from project_main.forms.account_forms import create_account_form, login_form, change_password_form, delete_account_form
from project_main.models.account import User


# This file contains functions which control account functions. 

account_management = Blueprint('account_management', __name__, template_folder='../views/account_management/')

# Renders the account managment page.
@account_management.route('/account_management')
def acc_management():
    if current_user.is_authenticated:
        return render_template('account_management.html')
    else:
        return redirect('home.home_login')

# Renders the create account page, and facilitates account creation upon successful POST request.
@account_management.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if current_user.is_authenticated:
        return redirect('home.home_login')
    form = create_account_form()
    if form.validate_on_submit():
        media_types = request.form.getlist("media_type")
        if User.check_new_password(form.password.data, form.confirm_password.data):
            if form.validate_email(form.email.data):
                User.create_account(form.email.data, form.first_name.data, form.last_name.data, form.password.data, media_types)
                flash("Account Created!")
                return redirect(url_for('home.home_page'))   
    return render_template('create_account.html', form=form)

# Renders the login page, and facilitates user login upon successful POST request.
@account_management.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.home_page')) 
    form = login_form()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not User.check_password(user, form.password.data):
            flash("Incorrect Email + Password Combo.", "login_error")
            return redirect(url_for('account_management.login'))
        login_user(user, remember=form.remember_me.data)
        flash("You have been logged in!")
        return redirect(url_for('home.home_page')) 
    return render_template('login.html', title='Log In', form=form)

# Facilitates user logout, redirecting to home page.
@account_management.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You have been logged out!")
        return redirect(url_for('home.index'))
    else:
        return redirect(url_for('home.index'))

# Renders change password page, and facilitates the changing of passwords upon successful POST request.
@account_management.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if current_user.is_authenticated:
        form = change_password_form()
        if form.validate_on_submit():
            password = request.form.get("password")
            if User.check_password(current_user, password):
                new_password = request.form.get("new_password")
                confirm_new_password = request.form.get("confirm_new_password")
                if User.check_new_password(new_password, confirm_new_password):
                    User.update_account(current_user.id, new_password)
                    flash("Password changed!")
                    return redirect(url_for('account_management.acc_management'))
            else:
                flash("Incorrect Password.")
                return redirect(url_for('account_management.change_password'))
        return render_template('change_password.html', form=form)
    else:
        return redirect(url_for('home.index'))

# Renders delete account page and faciliates the deletion of accounts upon successful POST request.
@account_management.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if current_user.is_authenticated:
        form = delete_account_form()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None or not User.check_password(user, form.password.data):
                return redirect(url_for('account_management.delete_account')) 
            if User.check_new_password(form.password.data, form.confirm_password.data):
                User.delete_account(user)
                flash("Account Deleted.")
                return redirect(url_for('home.index'))
        return render_template('delete_account.html', form=form)
    else:
        return redirect(url_for('home.index'))

# Renders update media types page and facilitates the changing of selected media types upon successful POST request.
@account_management.route('/update_media_types', methods=["GET", "POST"])
def update_media_types():
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        current_media_types = json.loads(user.media_types)
        if request.method == "POST":
            media_types = request.form.getlist("media_type")
            User.update_media_types(current_user, media_types)
            flash("Media Types Updated")
            return redirect(url_for("account_management.acc_management"))
        return render_template('update_media_types.html', current_media_types=current_media_types)
    else:
        return redirect(url_for('home.index'))




