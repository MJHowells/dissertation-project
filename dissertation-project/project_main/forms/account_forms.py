# Account forms using Flask Forms. Flask forms were used over normal forms for the validation 
# features they provide. 

from flask_wtf import FlaskForm

from wtforms import SubmitField, TextAreaField, StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired, ValidationError, Length, Email, EqualTo
from project_main.models.account import User
from flask_login import current_user
import sys


class create_account_form(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password: (8+ Characters, 1 Symbol, Uppercase and Number)', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email).first()
        if user:
            raise ValidationError('Email is already in use.')
        else:
            return True

    def validate_password(self, password):
        special_char = "'!@#$%^&*()-+?_=,<>/'"
        upper = False
        symbol = False
        number = False
        for letter in password.data:
            if letter.isupper():
                upper = True
            elif letter.isdigit():
                number = True
            elif letter in special_char:
                symbol = True
        if upper and symbol and number == True:
            return True
        else:
            raise ValidationError("Password must include 1 symbol" + " (" + special_char + ") "+ ", number and uppercase character. ")

class login_form(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            return True
        else:
            raise ValidationError('Email Not Recognised.')

class change_password_form(FlaskForm):
    password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

    def validate_password(self, password):
        user = User.check_password(current_user, password.data)
        if user:
            return True
        else:
            raise ValidationError("Incorrect Password.")

    def validate_new_password(self, new_password):
        special_char = "'!@#$%^&*()-+?_=,<>/'"
        upper = False
        symbol = False
        number = False
        for letter in new_password.data:
            if letter.isupper():
                upper = True
            elif letter.isdigit():
                number = True
            elif letter in special_char:
                symbol = True
        if upper and symbol and number == True:
            return True
        else:
            raise ValidationError("Password must include 1 symbol" + " (" + special_char + ") "+ ", number and uppercase character. ")


class delete_account_form(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo("password")])
    confirm_deletion = BooleanField('Are you sure?', validators=[DataRequired()])
    submit = SubmitField('Delete Account')

    def validate_email(self, email):
        user = User.query.filter_by(id=current_user.id).first()
        if user.email == email.data:
            return True
        else:
            return ValidationError("Incorrect Email.")
        
    def validate_password(self, password):
        user = User.check_password(current_user, password.data)
        if user:
            return True
        else:
            raise ValidationError("Incorrect Password.")

    def validate_check(self, confirm_deletion):
        raise ValidationError("Check must be selected to delete account!")


    
    
