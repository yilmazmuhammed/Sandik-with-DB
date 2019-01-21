from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import InputRequired, Length, Optional
from wtforms.fields.html5 import DateField
from datetime import date

from views import PageInfo


class FormPageInfo(PageInfo):
    def __init__(self, form, title):
        super().__init__(title)
        self.form = form
        self.errors = []
        for field in form:
            self.errors += field.errors


class SingUpForm(FlaskForm):
    form_name = 'signup-form'
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
    name = StringField("Name:", validators=[InputRequired("Please enter your name"),
                                            Length(max=40, message="Name field cannot be longer than 40 character")],
                       id='name')
    surname = StringField("Surname:",
                          validators=[InputRequired("Please enter your name"),
                                      Length(max=40, message="Surname field cannot be longer than 40 character")],
                          id='surname')

    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    form_name = 'login-form'
    username = StringField("Username:", validators=[InputRequired("Please enter your username")], id='username')
    password = PasswordField("Password:", validators=[InputRequired("Please enter your password")], id='password')
    submit = SubmitField("Login")


class SandikForm(FlaskForm):
    form_name = 'new-sandik-form'
    name = StringField("Sandik name:",
                       validators=[InputRequired("Please enter name of new sandik"),
                                   Length(max=40, message="Sandik name cannot be longer than 40 character")],
                       id='name')
    explanation = TextAreaField("Explanation:",
                                validators=[Optional(),
                                            Length(max=200, message="Explanation cannot be longer than 200 character")],
                                id='explanation')
    submit = SubmitField("Create New Sandik")


class MemberForm(FlaskForm):
    form_name = 'member-form'
    username = StringField("Username:",
                           validators=[InputRequired("Please enter username of new member"),
                                       Length(max=20, message="Username cannot be longer than 20 character")],
                           id='username')
    authority = SelectField(label='Member type:', validators=[InputRequired("Please select a member type in list")],
                            coerce=int, choices=[], id='authority')
    date_of_membership = DateField("Date of membership:", default=date.today(),
                                   validators=[InputRequired("Please enter date of membership")],
                                   id='date_of_membership')
    submit = SubmitField("Add Member")


class TransactionForm(FlaskForm):
    form_name = 'transaction-form'
    share = SelectField("Share:", validators=[InputRequired("Please select your share for transactionin list")],
                        coerce=int, choices=[], id='share')
    transaction_date = DateField("Transaction date:", default=date.today(),
                                 validators=[InputRequired("Please enter transaction date")],
                                 id='transaction_date')
    # TODO max amount borç tipine, içerdeki parasına ve diğer kurallara göre belirlenecek, burada da olabilir,
    #  formu aldıktan sonra da
    amount = IntegerField("Amount:", validators=[InputRequired("Please enter amount of transaction")], id='amount')
    explanation = TextAreaField("Explanation:",
                                validators=[Optional(),
                                            Length(max=200, message="Explanation cannot be longer than 200 character")],
                                id='explanation')
    submit = SubmitField("Add Transaction")


# Normalde seçilen değer, gönderilen değerlerden biri mi? diye kontrol edilit. Ama html kısmında belirlenen/değişen
# seçeneklerde bu kontrolü yapamadı
class DynamicSelectField(SelectField):
    def pre_validate(self, form):
        pass


class ContributionForm(TransactionForm):
    # TODO Çoklu aidat ödemelerinde getir
    amount = None
    # TODO çoklu aidat ödemelerinde multiple yap
    # value format: yyyy-mm
    contribution_period = DynamicSelectField(label="Contribution period:",
                                             validators=[InputRequired("Please select contribution period in list")],
                                             coerce=str, choices=[], id='contribution_period')
    # TODO use super()
    explanation = TextAreaField("Explanation:",
                                validators=[Optional(),
                                            Length(max=200, message="Explanation cannot be longer than 200 character")],
                                id='explanation')
    submit = SubmitField("Add Contribution")


class DebtForm(TransactionForm):
    debt_type = SelectField("Debt type:", validators=[InputRequired("Please select debt type from the list")],
                            coerce=int, choices=[], id='debt_type')

    number_of_installment = SelectField("Number of installment:",
                                        validators=[InputRequired("Please select number of installment from the list")],
                                        coerce=int, choices=[], id='number_of_installment')
    # TODO use super()
    explanation = TextAreaField("Explanation:",
                                validators=[Optional(),
                                            Length(max=200, message="Explanation cannot be longer than 200 character")],
                                id='explanation')
    submit = SubmitField("Take Debt")


class PaymentForm(TransactionForm):
    share = None
    debt = SelectField("Debt:", validators=[InputRequired("Please select the debt from list")], coerce=int, id='debt')

    # TODO use super()
    explanation = TextAreaField("Explanation:",
                                validators=[Optional(),
                                            Length(max=200, message="Explanation cannot be longer than 200 character")],
                                id='explanation')
    submit = SubmitField("Pay Debt")
