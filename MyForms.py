from wsgiref import validate
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from flask_wtf.file import *


class Command(FlaskForm):
    command = StringField('command',validators=[DataRequired()])
    submit = SubmitField('submit')

class Login(FlaskForm):
    username = StringField('username',validators=[DataRequired(),Length(min=1,max=20)])
    #email = StringField('username',validators=[DataRequired(),Length(min=1,max=50)])
    password = PasswordField('password',validators=[DataRequired(),Length(min=8,max=30)])
    submit = SubmitField('submit')

class Register(FlaskForm):
    username = StringField('username',validators=[DataRequired(),Length(min=1,max=20)])
    email = EmailField('email',validators=[DataRequired(),Length(min=1,max=50)])
    password = PasswordField('password',validators=[DataRequired(),Length(min=8,max=30),EqualTo("confirm_password",message="Passwords do not match")])
    confirm_password = PasswordField('confirm_password',validators=[DataRequired(),Length(min=8,max=30)])
    submit = SubmitField('submit')

class filefield1(FlaskForm):
    exelist = ["exe"]
    fileselector = FileField(validators=[FileAllowed(exelist,"exe's only")])
    submit = SubmitField('submit')