from forms import SingUpForm, FormPageInfo, LoginForm
from flask import render_template, current_app, redirect, flash, request, url_for
from database.dbinit import WebUser
from passlib.hash import pbkdf2_sha256 as hasher
from pony.orm import db_session
from pony.orm.core import TransactionIntegrityError, ObjectNotFound
from flask_login import login_user, logout_user, UserMixin


def signup_page():
    form = SingUpForm()
    info = FormPageInfo(form=form, title="Sign Up", form_name='signup-form')

    if form.validate_on_submit():
        if form.data["password"] != form.data["password_verify"]:
            info.errors += ("Passwords are not same",)
        else:
            try:
                with db_session:
                    WebUser(username=form.data["username"],
                            password_hash=hasher.hash(form.data["password"]),
                            date_of_registration=form.data["date_of_registration"],
                            name=form.data["name"],
                            surname=form.data["surname"],
                            is_admin=form.data["username"] in current_app.config["ADMIN_USERS"]
                            )
                return redirect(url_for("home_page"))
            # If username already exists in database
            except TransactionIntegrityError:
                info.errors += ("'" + form.data["username"] + "' username already exists.",)
            except Exception as e:
                info.errors += (type(e), e,)

    return render_template("form.html", info=info)


def login_page():
    form = LoginForm()
    info = FormPageInfo(title='Login', form=form, form_name='login-form')

    if form.validate_on_submit():
        try:
            user = FlaskUser(form.data['username'])
            if hasher.verify(form.data['password'], user.webuser.password_hash) and user.is_active:
                login_user(user)
                flash("You have logged in.")
                next_page = request.args.get("next", url_for("home_page"))
                return redirect(next_page)
            else:
                info.errors += ("Username or password is incorrect.",)
            # with db_session:
            #     if hasher.verify(form.data['password'], WebUser[form.data['username']].password_hash ):
            #         login_user(WebUser[form.data['username']])
            #         flash("You have logged in.")
            #         next_page = request.args.get("next", url_for("home_page"))
            #         return redirect(next_page)
            #     else:
            #         info.errors += ("Username or password is incorrect.",)
        # If username already exists in database
        except ObjectNotFound:
            info.errors += ("Username or password is incorrect.",)

    return render_template("form.html", info=info)


def logout_page():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for("home_page"))


class FlaskUser(UserMixin):
    def __init__(self, username):
        self.username = username
        with db_session:
            self.webuser = WebUser[username]
            self.is_admin = self.webuser.is_admin

    def get_id(self):
        return self.webuser.username

    @property
    def is_active(self):
        return self.webuser.is_active
