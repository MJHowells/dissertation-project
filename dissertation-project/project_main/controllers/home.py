from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_user, logout_user
from project_main.init import db
import json
from flask.helpers import flash

import sys


from project_main.forms.account_forms import create_account_form, login_form
from project_main.models.account import User
from project_main.models.media import Media
from project_main.models.goals import Goals


home = Blueprint('home', __name__, template_folder='../views')

# This file contains functions which render and control the home pages.


# Renders pre-login Home page, and facilitates user login upon succesful POST request. 
@home.route('/', methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home.home_page'))
    else:
        form = login_form()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None or not User.check_password(user, form.password.data):
                flash("Incorrect Email + Password Combo.", "login_error")
                return redirect(url_for('account_management.login'))
            login_user(user, remember=form.remember_me.data)
            flash("You have been logged in!")
            return redirect(url_for('home.home_page')) 

        return render_template('login_or_create_account.html', form=form)

# Renders logged in home page.
@home.route('/home')
def home_page():
    if current_user.is_authenticated:
        media = Media.getFirstConsuming(current_user)
        goal = Goals.getFirstCurrGoal(current_user)
        if goal != None:
            temp_media = Media.get_media(current_user)
            consumed = json.loads(temp_media.consumed)
        else:
            consumed = None
        return render_template('home.html', media=media, goal=goal, consumed=consumed)
    else:
        return redirect(url_for("home.index"))

# Renders help page.
@home.route('/help')
def help_page():
    return render_template('help.html')

# Renders about page.
@home.route('/about')
def about_page():
    return render_template('about.html')
