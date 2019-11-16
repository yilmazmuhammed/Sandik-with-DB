from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField, BooleanField, \
    SelectMultipleField
from wtforms.validators import InputRequired, Length, Optional, NumberRange
from wtforms.fields.html5 import DateField
from datetime import date

from views import LayoutPageInfo


# Normalde;
#  value='' olarak formu kabul etmiyor, fakat şu an ediyor.
class SelectField(SelectField):
    def iter_choices(self):
        for value, label in self.choices:
            if self.coerce is int and not self.data:
                yield (value, label, False)
            else:
                yield (value, label, self.coerce(value) == self.data)


# Normalde seçilen değer, gönderilen değerlerden biri mi? diye kontrol edilir. Ama html kısmında belirlenen/değişen
#  seçeneklerde bu kontrolü yapamadı, select listesindeki değerler js ile belirlendi
class DynamicSelectField(SelectField):
    def pre_validate(self, form):
        pass


class DynamicSelectMultipleField(SelectMultipleField):
    def pre_validate(self, form):
        pass


def form_open(form_name, id=None, enctype=None):
    open = """<form action="" method="post" name="%s" """ % (form_name)

    if id:
        open += """ id="%s" """ % (id)
    if enctype:
        open += """ enctype="%s" """ % (enctype)

    open += """class="sandik-form">"""

    return open


def form_close():
    return """</form>"""


class FormPageInfo(LayoutPageInfo):
    def __init__(self, form, title):
        super().__init__(title)
        self.form = form
        self.errors = []
        for field in form:
            self.errors += field.errors


class WebuserForm(FlaskForm):
    open = form_open(form_name='webuser-form')
    close = form_close()

    username = StringField("Username:",
                           validators=[InputRequired("Please enter your username"),
                                       Length(max=20, message="Username cannot be longer than 20 character")],
                           id='username', render_kw={"placeholder": "Username", "class": "form-control"})
    password = PasswordField("Password:",
                             validators=[InputRequired("Please enter your password"),
                                         Length(max=20, message="Password cannot be longer than 20 character")],
                             id='password', render_kw={"placeholder": "Password", "class": "form-control"})
    password_verify = PasswordField("Password (again):",
                                    validators=[InputRequired("Please enter your password"),
                                                Length(max=20, message="Password cannot be longer than 20 character")],
                                    id='password_verify',
                                    render_kw={"placeholder": "Password (again)", "class": "form-control"})
    name = StringField("Name:", validators=[InputRequired("Please enter your name"),
                                            Length(max=40, message="Name field cannot be longer than 40 character")],
                       id='name', render_kw={"placeholder": "Name", "class": "form-control"})
    surname = StringField("Surname:",
                          validators=[InputRequired("Please enter your name"),
                                      Length(max=40, message="Surname field cannot be longer than 40 character")],
                          id='surname', render_kw={"placeholder": "Surname", "class": "form-control"})
    is_admin = BooleanField(label="Is admin:", id='is_admin',
                            render_kw={"class": "form-control", "data-toggle": "toggle", "data-onstyle": "success"})
    date_of_registration = DateField("Date of registration:", default=date.today(),
                                     validators=[InputRequired("Please enter date of registration")],
                                     id='date_of_registration',
                                     render_kw={"placeholder": "Date of registration", "class": "form-control"})
    submit = SubmitField("Add New Webuser", render_kw={"class": "btn btn-primary sandik-btn-form"})


class SingUpForm(WebuserForm):
    open = form_open(form_name='signup-form')
    is_admin = None
    date_of_registration = None
    submit = SubmitField("Sign Up", render_kw={"class": "btn btn-primary sandik-btn-form"})


class EditWebUserForm(FlaskForm):
    open = form_open(form_name='edit-webuser-form')
    close = form_close()

    username = StringField("Username:",
                           validators=[Length(max=20, message="Username cannot be longer than 20 character")],
                           id='username', render_kw={"class": "form-control", "readonly": ""})
    old_password = PasswordField("Old password:",
                                 validators=[InputRequired("Please enter your password"),
                                             Length(max=20, message="Password cannot be longer than 20 character")],
                                 id='old_password', render_kw={"class": "form-control"})
    new_password = PasswordField("New password:",
                                 validators=[Length(max=20, message="Password cannot be longer than 20 character")],
                                 id='new_password', render_kw={"class": "form-control"})
    new_password_verify = PasswordField("New password (again):",
                                        validators=[
                                            Length(max=20, message="Password cannot be longer than 20 character")],
                                        id='new_password_verify',
                                        render_kw={"class": "form-control"})
    name = StringField("Name:", validators=[Length(max=40, message="Name field cannot be longer than 40 character")],
                       id='name', render_kw={"class": "form-control"})
    surname = StringField("Surname:",
                          validators=[Length(max=40, message="Surname field cannot be longer than 40 character")],
                          id='surname', render_kw={"class": "form-control"})
    submit = SubmitField("Submit", render_kw={"class": "btn btn-primary sandik-btn-form"})


class LoginForm(FlaskForm):
    open = form_open(form_name='login-form')
    close = form_close()

    username = StringField("Username:", validators=[InputRequired("Please enter your username")], id='username',
                           render_kw={"placeholder": "Username", "class": "form-control"})
    password = PasswordField("Password:", validators=[InputRequired("Please enter your password")], id='password',
                             render_kw={"placeholder": "Password", "class": "form-control"})
    submit = SubmitField("Login", render_kw={"class": "btn btn-primary sandik-btn-form"})


class SandikForm(FlaskForm):
    open = form_open(form_name='new-sandik-form')
    close = form_close()

    name = StringField("Sandik name:",
                       validators=[InputRequired("Please enter name of new sandik"),
                                   Length(max=40, message="Sandik name cannot be longer than 40 character")],
                       id='name', render_kw={"placeholder": "Sandik name", "class": "form-control"})
    date_of_opening = DateField("Date of opening:", default=date.today(),
                                validators=[InputRequired("Please enter opening date of sandik ")],
                                id='date_of_opening',
                                render_kw={"placeholder": "Date of opening", "class": "form-control"})
    contribution_amount = IntegerField("Contribution Amount:",
                                       validators=[InputRequired("Please enter contribution amount of sandik")],
                                       id='contribution_amount',
                                       render_kw={"placeholder": "Contribution Amount", "class": "form-control"})
    explanation = TextAreaField("Explanation:",
                                validators=[Optional(),
                                            Length(max=200, message="Explanation cannot be longer than 200 character")],
                                id='explanation', render_kw={"placeholder": "Explanation", "class": "form-control"})
    submit = SubmitField("Create New Sandik", render_kw={"class": "btn btn-primary sandik-btn-form"})


class MemberForm(FlaskForm):
    open = form_open(form_name='member-form')
    close = form_close()

    username = StringField("Username:",
                           validators=[InputRequired("Please enter username of new member"),
                                       Length(max=20, message="Username cannot be longer than 20 character")],
                           id='username', render_kw={"placeholder": "Username", "class": "form-control"})
    authority = SelectField(label='Member type:', validators=[InputRequired("Please select a member type in list")],
                            coerce=int, choices=[], id='authority',
                            render_kw={"placeholder": "Member type", "class": "form-control"})
    date_of_membership = DateField("Date of membership:", default=date.today(),
                                   validators=[InputRequired("Please enter date of membership")],
                                   id='date_of_membership',
                                   render_kw={"placeholder": "Date of membership", "class": "form-control"})
    submit = SubmitField("Add Member", render_kw={"class": "btn btn-primary sandik-btn-form"})


class MemberAuthorityTypeForm(FlaskForm):
    open = form_open(form_name='member-authority-type-form')
    close = form_close()

    name = StringField("Name:",
                       validators=[InputRequired("Please enter name of Member Authority Type"),
                                   Length(max=20, message="Name cannot be longer than 20 character")],
                       id='name', render_kw={"placeholder": "Name", "class": "form-control"})
    capacity = IntegerField("Capacity:",
                            validators=[InputRequired("Sayı sınırı belirlemek istemiyorsanız 0 giriniz.\n"
                                                      "Değilse 0'dan büyük bir tamsayı giriniz."),
                                        NumberRange(min=0, message="Lütfen geçerli bir kapasite giriniz.")],
                            id='amount', render_kw={"placeholder": "Capacity", "class": "form-control"})
    is_admin = BooleanField(label="Is admin:", id='is_admin',
                            render_kw={"class": "form-control", "data-toggle": "toggle", "data-onstyle": "success"})
    reading_transaction = BooleanField(label="Reading transaction:", id='reading_transaction',
                                       render_kw={"class": "form-control",
                                                  "data-toggle": "toggle", "data-onstyle": "success"})
    writing_transaction = BooleanField(label="Writing transaction:", id='writing_transaction',
                                       render_kw={"class": "form-control",
                                                  "data-toggle": "toggle", "data-onstyle": "success"})
    adding_member = BooleanField(label="Adding Member:", id='adding_member',
                                 render_kw={"class": "form-control",
                                            "data-toggle": "toggle", "data-onstyle": "success"})
    throwing_member = BooleanField(label="Throwing Member:", id='throwing_member',
                                   render_kw={"class": "form-control",
                                              "data-toggle": "toggle", "data-onstyle": "success"})

    submit = SubmitField("Add Member Authority Type", render_kw={"class": "btn btn-primary sandik-btn-form"})


class DebtTypeForm(FlaskForm):
    open = form_open(form_name='debt-type-form')
    close = form_close()

    name = StringField("Name:",
                       validators=[InputRequired("Please enter name of Debt Type"),
                                   Length(max=20, message="Name cannot be longer than 20 character")],
                       id='name', render_kw={"placeholder": "Name", "class": "form-control"})
    explanation = TextAreaField("Explanation:",
                                validators=[Optional(),
                                            Length(max=200, message="Explanation cannot be longer than 200 character")],
                                id='explanation', render_kw={"placeholder": "Explanation", "class": "form-control"})
    max_number_of_installments = IntegerField("Max Number of Installment:",
                                              validators=[InputRequired("Sınır belirlemek istemiyorsanız 0 giriniz.\n"
                                                                        "Değilse 0'dan büyük bir tamsayı giriniz."),
                                                          NumberRange(min=0, message="Lütfen geçerli bir sayı giriniz.")
                                                          ],
                                              id='max_number_of_installments',
                                              render_kw={"placeholder": "Max number of installment",
                                                         "class": "form-control"})
    max_amount = IntegerField("Max Amount:",
                              validators=[InputRequired("Sınır belirlemek istemiyorsanız 0 giriniz.\n"
                                                        "Değilse 0'dan büyük bir tamsayı giriniz."),
                                          NumberRange(min=0, message="Lütfen geçerli bir sayı giriniz.")],
                              id='max_amount', render_kw={"placeholder": "Max amount", "class": "form-control"})
    min_installment_amount = IntegerField("Min Installment Amount:",
                                          validators=[InputRequired("Sınır belirlemek istemiyorsanız 0 giriniz.\n"
                                                                    "Değilse 0'dan büyük bir tamsayı giriniz."),
                                                      NumberRange(min=0, message="Lütfen geçerli bir sayı giriniz.")],
                                          id='min_installment_amount',
                                          render_kw={"placeholder": "Min installment amount", "class": "form-control"})

    submit = SubmitField("Add Debt Type", render_kw={"class": "btn btn-primary sandik-btn-form"})


class TransactionForm(FlaskForm):
    open = form_open(form_name='transaction-form')
    close = form_close()

    share = DynamicSelectField("Share:", validators=[InputRequired("Please select your share for transactionin list")],
                               coerce=int, choices=[], id='share', render_kw={"class": "form-control"})
    transaction_date = DateField("Transaction date:", default=date.today(),
                                 validators=[InputRequired("Please enter transaction date")],
                                 id='transaction_date', render_kw={"class": "form-control"})
    amount = IntegerField("Amount:", validators=[InputRequired("Please enter amount of transaction")], id='amount',
                          render_kw={"placeholder": "Amount", "class": "form-control"})
    explanation = TextAreaField("Explanation:",
                                validators=[Optional(),
                                            Length(max=200, message="Explanation cannot be longer than 200 character")],
                                id='explanation', render_kw={"placeholder": "Explanation", "class": "form-control"})
    submit = SubmitField("Add Transaction", render_kw={"class": "btn btn-primary sandik-btn-form"})


class ContributionForm(TransactionForm):
    open = form_open(form_name='contribution-form')
    close = form_close()

    amount = IntegerField("Amount:", validators=[InputRequired("Please enter amount of transaction")], id='amount',
                          render_kw={"placeholder": "Amount", "class": "form-control", "readonly": ""})

    # value format: yyyy-mm
    contribution_period = \
        DynamicSelectMultipleField(label="Contribution period:",
                                   validators=[InputRequired("Please select contribution period in list")],
                                   coerce=str, choices=[], id='contribution_period',
                                   render_kw={"class": "form-control"})
    # TODO use super()
    explanation = TextAreaField("Explanation:",
                                validators=[Optional(),
                                            Length(max=200, message="Explanation cannot be longer than 200 character")],
                                id='explanation', render_kw={"placeholder": "Explanation", "class": "form-control"})
    # TODO use super()
    submit = SubmitField("Add Contribution", render_kw={"class": "btn btn-primary sandik-btn-form"})


class DebtForm(TransactionForm):
    open = form_open(form_name='debt-form', id="debt-form")
    close = form_close()

    debt_type = SelectField("Debt type:", validators=[InputRequired("Please select debt type from the list")],
                            coerce=int, choices=[], id='debt_type', render_kw={"class": "form-control"})

    number_of_installment = SelectField("Number of installment:",
                                        validators=[InputRequired("Please select number of installment from the list")],
                                        coerce=int, choices=[], id='number_of_installment',
                                        render_kw={"class": "form-control"})
    # TODO use super()
    explanation = TextAreaField("Explanation:",
                                validators=[Optional(),
                                            Length(max=200, message="Explanation cannot be longer than 200 character")],
                                id='explanation', render_kw={"placeholder": "Explanation", "class": "form-control"})
    # TODO use super()
    submit = SubmitField("Take Debt", render_kw={"class": "btn btn-primary sandik-btn-form"})


class PaymentForm(TransactionForm):
    open = form_open(form_name='payment-form')
    close = form_close()

    share = None
    debt = DynamicSelectField("Debt:", validators=[InputRequired("Please select the debt from list")], coerce=int,
                              choices=[], id='debt', render_kw={"class": "form-control"})

    # TODO use super()
    explanation = TextAreaField("Explanation:",
                                validators=[Optional(),
                                            Length(max=200, message="Explanation cannot be longer than 200 character")],
                                id='explanation', render_kw={"placeholder": "Explanation", "class": "form-control"})
    # TODO use super()
    submit = SubmitField("Pay Debt", render_kw={"class": "btn btn-primary sandik-btn-form"})


class CustomTransactionSelectForm(FlaskForm):
    open = form_open(form_name='custom-transaction-select-form')
    close = form_close()

    member = SelectField("Member:", choices=[], id='member', render_kw={"class": "form-control"})
    type_choices = [("contribution", "Contribution"), ("debt", "Debt"), ("payment", "Payment"),
                    ("transaction", "Other")]
    type = SelectField("Type:", choices=type_choices, id='type', render_kw={"class": "form-control"})


class ImportAllDataForm(FlaskForm):
    open = form_open(form_name='import-all-data-form', enctype="multipart/form-data")
    close = form_close()

    # data_url = StringField("Data url:", id='data-url', render_kw={"placeholder": "Data url", "class": "form-control"})
    data_file = FileField("Data file (only csv):", id='data-file', validators=[FileAllowed(['csv'], 'Csv file only!')],
                          render_kw={"class": "form-control"})

    submit = SubmitField("Import data", render_kw={"class": "btn btn-primary sandik-btn-form"})


class AddingShareForm(FlaskForm):
    open = form_open(form_name='adding-share-form')
    close = form_close()

    member = SelectField("Member:", validators=[InputRequired("Please select a member in list")], choices=[],
                         id='member', coerce=int, render_kw={"class": "form-control"})
    date_of_opening = DateField("Date of opening:", default=date.today(),
                                validators=[InputRequired("Please enter date of membership")], id='date_of_opening',
                                render_kw={"placeholder": "Date of opening", "class": "form-control"})
    submit = SubmitField("Add Share", render_kw={"class": "btn btn-primary sandik-btn-form"})


def select_form(form_name, tag, coerce, choices, id, submit_tag):
    class SelectForm(FlaskForm):
        open = form_open(form_name=form_name)
        close = form_close()

        member = SelectField("%s:"%tag, validators=[InputRequired("Please select from the list")], choices=choices,
                             id=id, coerce=coerce, render_kw={"class": "form-control"})
        submit = SubmitField(submit_tag, render_kw={"class": "btn btn-primary sandik-btn-form"})

    return SelectForm()
