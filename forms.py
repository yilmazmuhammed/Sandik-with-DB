from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from wtforms.fields.html5 import DateField


class FormPageInfo:
    def __init__(self, form, title, errors):
        self.form = form
        self.title = title
        self.errors = errors


class SingUpForm(FlaskForm):
    username = StringField("Username:",
                           validators=[InputRequired("Please enter your username"),
                                       Length(max=20, message="Username cannot be longer than 20 character")],
                           id='username')
    password = PasswordField("Password:",
                             validators=[InputRequired("Please enter your password"),
                                         Length(max=20, message="Password cannot be longer than 20 character")],
                             id='password')
    password_verify = PasswordField("Password:",
                                    validators=[InputRequired("Please enter your password"),
                                                Length(max=20, message="Password cannot be longer than 20 character")],
                                    id='password')
    date_of_registration = DateField("Date of registration",
                                     validators=[InputRequired("Please enter date of registration")],
                                     id='date_of_registration')

    name = StringField("Name:", validators=[InputRequired("Please enter your name"),
                                            Length(max=40, message="Name field cannot be longer than 40 character")],
                       id='name')
    surname = StringField("Surname:",
                          validators=[InputRequired("Please enter your name"),
                                      Length(max=40, message="Surname field cannot be longer than 40 character")],
                          id='surname')

    submit = SubmitField("Sign Up")
