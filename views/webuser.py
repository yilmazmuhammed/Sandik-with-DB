from datetime import date
from flask import render_template, current_app, redirect, flash, request, url_for, abort
from flask_login import login_user, logout_user, UserMixin, current_user, login_required

from forms import SingUpForm, FormPageInfo, LoginForm, WebuserForm
from database.dbinit import WebUser
from passlib.hash import pbkdf2_sha256 as hasher
from pony.orm import db_session
from pony.orm.core import TransactionIntegrityError, ObjectNotFound


def add_webuser(form: SingUpForm, is_admin=None):
    if form.date_of_registration:
        date_of_registration = form.date_of_registration.data
    else:
        date_of_registration = date.today()

    if is_admin is None:
        if form.is_admin:
            is_admin = form.is_admin.data
        else:
            is_admin = False

    with db_session:
        return WebUser(username=form.data["username"],
                       password_hash=hasher.hash(form.data["password"]),
                       date_of_registration=date_of_registration,
                       name=form.data["name"],
                       surname=form.data["surname"],
                       is_admin=is_admin
                       )


def signup_page():
    if current_user.is_authenticated:
        # TODO üye sayfasına gönder
        return redirect(url_for('home_page'))

    form = SingUpForm()

    if form.validate_on_submit():
        if form.data["password"] != form.data["password_verify"]:
            flash(u"Passwords are not same.", 'danger')
        else:
            try:
                add_webuser(form, is_admin=form.data["username"] in current_app.config["ADMIN_USERS"])
                return redirect(url_for("home_page"))
            except TransactionIntegrityError:  # If username already exists in database
                flash(u"'%s' username already exists." % (form.data["username"],), 'danger')
            except Exception as e:  # If there is another exception
                flash(u"Unexpected exception:\n%s %s" % (type(e), e,), 'danger')

    info = FormPageInfo(form=form, title="Sign Up")

    return render_template("form.html", info=info)


@login_required
def add_websuer_page():
    if not current_user.is_admin:
        abort(404)

    form = WebuserForm()

    if form.validate_on_submit():
        if form.data["password"] != form.data["password_verify"]:
            flash(u"Passwords are not same.", 'danger')
        else:
            try:
                add_webuser(form)
                return redirect(url_for("home_page"))
            except TransactionIntegrityError:  # If username already exists in database
                flash(u"'%s' username already exists." % (form.data["username"],), 'danger')
            except Exception as e:  # If there is another exception
                flash(u"Unexpected exception:\n%s %s" % (type(e), e,), 'danger')

    info = FormPageInfo(form=form, title="Sign Up")

    return render_template("form.html", info=info)


def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = FlaskUser(form.data['username'])
            if hasher.verify(form.data['password'], user.webuser.password_hash) and user.is_active:
                login_user(user)
                flash("You have logged in.", 'success')
                next_page = request.args.get("next", url_for("home_page"))
                return redirect(next_page)
            else:  # If password is incorrect
                flash(u"Username or password is incorrect.", 'danger')
            # with db_session:
            #     if hasher.verify(form.data['password'], WebUser[form.data['username']].password_hash ):
            #         login_user(WebUser[form.data['username']])
            #         flash("You have logged in.")
            #         next_page = request.args.get("next", url_for("home_page"))
            #         return redirect(next_page)
            #     else:
            #         info.errors += ("Username or password is incorrect.",)
        except ObjectNotFound:  # If username already exists in database
            flash(u"Username or password is incorrect.", 'danger')

    info = FormPageInfo(title='Login', form=form)

    return render_template("form.html", info=info)


@login_required
def logout_page():
    logout_user()
    flash(u"You have logged out.", 'success')
    return redirect(url_for("home_page"))


class FlaskUser(UserMixin):
    def __init__(self, username):
        self.username = username
        with db_session:
            self.username = username
            self.webuser = WebUser[username]
            self.is_admin = self.webuser.is_admin

    def get_id(self):
        return self.webuser.username

    @property
    def is_active(self):
        return self.webuser.is_active
