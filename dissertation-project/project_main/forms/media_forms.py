# UN USED. Flask forms for media. After experimentation these were not used
# as the were not deemed flexible enough for the application. 

from flask_wtf import FlaskForm

from wtforms import SubmitField, TextAreaField, StringField, BooleanField, PasswordField, SelectField
from wtforms import validators
from wtforms.validators import DataRequired, ValidationError, Length

class new_media_form(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=150)])
    # creator = StringField('Creator', validators=[DataRequired(), Length(min=5, max=100)])
    length = StringField('Length', validators=[DataRequired(), Length(min=1, max=80)])
    # actor = StringField('Actor', validators=[Length(min=1, max=50)])
    description = StringField('Description', validators=[Length(min=1, max=512)])
    # genre = StringField('Genre')
    # tag = StringField('Tag')
    type = SelectField('Media Type', choices=['Book', 'Film', 'Music'], validators=[DataRequired()])
    completed = BooleanField('Media Finished')
    submit = SubmitField('Add')
