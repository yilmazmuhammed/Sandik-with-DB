from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional
from wtforms.fields.html5 import DateField


class FormPageInfo:
    def __init__(self, form, title, form_name):
        self.form = form
        self.title = title
        self.errors = ()
        self.form_name = form_name
        for field in form:
            self.errors += field.errors


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


class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[InputRequired("Please enter your username")], id='username')
    password = PasswordField("Password:", validators=[InputRequired("Please enter your password")], id='password')
    submit = SubmitField("Login")


class SandikForm(FlaskForm):
    name = StringField("Sandik name:",
                       validators=[InputRequired("Please enter name of new sandik"),
                                   Length(max=40, message="Sandik name cannot be longer than 40 character")],
                       id='name')
    explanation = TextAreaField("Explanation:",
                                validators=[Optional(),
                                            Length(max=200, message="Explanation cannot be longer than 200 character")],
                                id='explanation')
    submit = SubmitField("Create New Sandik")