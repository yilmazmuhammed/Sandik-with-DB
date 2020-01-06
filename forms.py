from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField, BooleanField, \
    SelectMultipleField
from wtforms.validators import InputRequired, Length, Optional, NumberRange
from wtforms.fields.html5 import DateField
from datetime import date

from views import LayoutPageInfo, get_translation


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
    t = get_translation()['forms']['webuser']

    open = form_open(form_name='webuser-form')
    close = form_close()

    username = StringField("%s:" % t['username']['label'],
                           validators=[InputRequired(t['username']['required']),
                                       Length(max=20, message=t['username']['length'])],
                           id='username', render_kw={"placeholder": t['username']['label'], "class": "form-control"})
    password = PasswordField("%s:" % t['password']['label'],
                             validators=[InputRequired(t['password']['required']),
                                         Length(max=20, message=t['password']['length'])],
                             id='password', render_kw={"placeholder": t['password']['label'], "class": "form-control"})
    password_verify = PasswordField("%s:" % t['password_verify']['label'],
                                    validators=[InputRequired(t['password_verify']['required']),
                                                Length(max=20, message=t['password_verify']['length'])],
                                    id='password_verify',
                                    render_kw={"placeholder": t['password_verify']['label'], "class": "form-control"})
    name = StringField("%s:" % t['name']['label'], validators=[InputRequired(t['name']['required']),
                                                               Length(max=40, message=t['name']['length'])],
                       id='name', render_kw={"placeholder": t['name']['label'], "class": "form-control"})
    surname = StringField("%s:" % t['surname']['label'],
                          validators=[InputRequired(t['surname']['required']),
                                      Length(max=40, message=t['surname']['length'])],
                          id='surname', render_kw={"placeholder": t['surname']['label'], "class": "form-control"})
    is_admin = BooleanField(label="%s:" % t['is_admin']['label'], id='is_admin',
                            render_kw={"class": "form-control", "data-toggle": "toggle", "data-onstyle": "success"})
    date_of_registration = DateField("%s:" % t['date_of_registration']['label'], default=date.today(),
                                     validators=[InputRequired(t['date_of_registration']['required'])],
                                     id='date_of_registration',
                                     render_kw={"placeholder": t['date_of_registration']['label'],
                                                "class": "form-control"})
    submit = SubmitField("%s:" % t['submit']['label'], render_kw={"class": "btn btn-primary sandik-btn-form"})


class SingUpForm(WebuserForm):
    t = get_translation()['forms']['signup']

    open = form_open(form_name='signup-form')
    is_admin = None
    date_of_registration = None
    submit = SubmitField("%s:" % t['submit']['label'], render_kw={"class": "btn btn-primary sandik-btn-form"})


class EditWebUserForm(FlaskForm):
    t = get_translation()['forms']['edit_webuser']

    open = form_open(form_name='edit-webuser-form')
    close = form_close()

    username = StringField("%s:" % t['username']['label'],
                           validators=[Length(max=20, message=t['username']['length'])],
                           id='username', render_kw={"class": "form-control", "readonly": ""})
    old_password = PasswordField("%s:" % t['old_password']['label'],
                                 validators=[InputRequired(t['old_password']['required']),
                                             Length(max=20, message=t['old_password']['length'])],
                                 id='old_password', render_kw={"class": "form-control"})
    new_password = PasswordField("%s:" % t['new_password']['label'],
                                 validators=[Length(max=20, message=t['new_password']['length'])],
                                 id='new_password', render_kw={"class": "form-control"})
    new_password_verify = PasswordField("%s:" % t['new_password_verify']['label'],
                                        validators=[
                                            Length(max=20, message=t['new_password_verify']['length'])],
                                        id='new_password_verify',
                                        render_kw={"class": "form-control"})
    name = StringField("%s:" % t['name']['label'], validators=[Length(max=40, message=t['name']['length'])],
                       id='name', render_kw={"class": "form-control"})
    surname = StringField("%s:" % t['surname']['label'],
                          validators=[Length(max=40, message=t['surname']['length'])],
                          id='surname', render_kw={"class": "form-control"})
    submit = SubmitField("%s:" % t['submit']['label'], render_kw={"class": "btn btn-primary sandik-btn-form"})


class LoginForm(FlaskForm):
    t = get_translation()['forms']['login']

    open = form_open(form_name='login-form')
    close = form_close()

    username = StringField("%s:" % t['username']['label'], validators=[InputRequired(t['username']['required'])],
                           id='username',
                           render_kw={"placeholder": "%s:" % t['username']['label'], "class": "form-control"})
    password = PasswordField("%s:" % t['password']['label'], validators=[InputRequired(t['password']['required'])],
                             id='password',
                             render_kw={"placeholder": "%s:" % t['password']['label'], "class": "form-control"})
    submit = SubmitField("%s:" % t['submit']['label'], render_kw={"class": "btn btn-primary sandik-btn-form"})


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
    t = get_translation()['forms']['transaction']

    open = form_open(form_name='transaction-form')
    close = form_close()

    share = DynamicSelectField("%s:" % t['share']['label'], validators=[InputRequired(t['share']['required'])],
                               coerce=int, choices=[], id='share', render_kw={"class": "form-control"})
    transaction_date = DateField("%s:" % t['date']['label'], default=date.today(),
                                 validators=[InputRequired("%s" % t['date']['required'])],
                                 id='transaction_date', render_kw={"class": "form-control"})
    amount = IntegerField("%s:" % t['amount']['label'], validators=[InputRequired(t['amount']['required'])],
                          id='amount',
                          render_kw={"placeholder": t['amount']['label'], "class": "form-control"})
    explanation = TextAreaField("%s:" % t['explanation']['label'],
                                validators=[Optional(),
                                            Length(max=200, message=t['explanation']['length'])],
                                id='explanation',
                                render_kw={"placeholder": t['explanation']['label'], "class": "form-control"})
    # TODO use super()
    submit = SubmitField(t['submit']['label'], render_kw={"class": "btn btn-primary sandik-btn-form"})


class ContributionForm(TransactionForm):
    t = get_translation()['forms']['contribution']

    open = form_open(form_name='contribution-form')
    close = form_close()
    amount = IntegerField("%s:" % t['amount']['label'], validators=[InputRequired(t['amount']['required'])],
                          id='amount',
                          render_kw={"placeholder": t['amount']['label'], "class": "form-control", "readonly": ""})

    # value format: yyyy-mm
    contribution_period = DynamicSelectMultipleField(label="%s:" % t['contribution_period']['label'],
                                                     validators=[InputRequired(t['contribution_period']['required'])],
                                                     coerce=str, choices=[], id='contribution_period',
                                                     render_kw={"class": "form-control"})
    # TODO use super()
    explanation = TextAreaField("%s:" % t['explanation']['label'],
                                validators=[Optional(),
                                            Length(max=200, message=t['explanation']['length'])],
                                id='explanation',
                                render_kw={"placeholder": t['explanation']['label'], "class": "form-control"})
    # TODO use super()
    submit = SubmitField(t['submit']['label'], render_kw={"class": "btn btn-primary sandik-btn-form"})


class DebtForm(TransactionForm):
    t = get_translation()['forms']['debt']

    open = form_open(form_name='debt-form', id="debt-form")
    close = form_close()

    debt_type = SelectField("%s:" % t['debt_type']['label'], validators=[InputRequired(t['debt_type']['required'])],
                            coerce=int, choices=[], id='debt_type', render_kw={"class": "form-control"})

    number_of_installment = SelectField("%s:" % t['number_of_installment']['label'],
                                        validators=[InputRequired(t['number_of_installment']['required'])],
                                        coerce=int, choices=[], id='number_of_installment',
                                        render_kw={"class": "form-control"})
    # TODO use super()
    explanation = TextAreaField("%s:" % t['explanation']['label'],
                                validators=[Optional(),
                                            Length(max=200, message=t['explanation']['length'])],
                                id='explanation',
                                render_kw={"placeholder": t['explanation']['label'], "class": "form-control"})
    # TODO use super()
    submit = SubmitField(t['submit']['label'], render_kw={"class": "btn btn-primary sandik-btn-form"})


class PaymentForm(TransactionForm):
    t = get_translation()['forms']['payment']

    open = form_open(form_name='payment-form')
    close = form_close()

    share = None
    debt = DynamicSelectField("%s:" % t['debt']['label'], validators=[InputRequired(t['debt']['required'])], coerce=int,
                              choices=[], id='debt', render_kw={"class": "form-control"})

    # TODO use super()
    explanation = TextAreaField("%s:" % t['explanation']['label'],
                                validators=[Optional(),
                                            Length(max=200, message=t['explanation']['length'])],
                                id='explanation',
                                render_kw={"placeholder": t['explanation']['label'], "class": "form-control"})
    # TODO use super()
    submit = SubmitField(t['submit']['label'], render_kw={"class": "btn btn-primary sandik-btn-form"})


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

        member = SelectField("%s:" % tag, validators=[InputRequired("Please select from the list")], choices=choices,
                             id=id, coerce=coerce, render_kw={"class": "form-control"})
        submit = SubmitField(submit_tag, render_kw={"class": "btn btn-primary sandik-btn-form"})

    return SelectForm()
