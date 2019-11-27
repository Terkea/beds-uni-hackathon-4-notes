from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email


class registerForm(FlaskForm):
    email = StringField('E-mail address', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    password_check = StringField('Password check', validators=[DataRequired()])
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])