from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email


class registerForm(FlaskForm):
    email = StringField('E-mail address', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    password_check = StringField('Password check', validators=[DataRequired()])
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])


class loginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = StringField('password', validators=[DataRequired()])


class createCategory(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired()])


class updateCategory(FlaskForm):
    public_id = StringField('Public ID', validators=[DataRequired()])
    category_name = StringField('Category Name', validators=[DataRequired()])

class deleteCategory(FlaskForm):
    public_id = StringField('Public ID', validators=[DataRequired()])
    notes_action = StringField('Action Name', validators=[DataRequired()])