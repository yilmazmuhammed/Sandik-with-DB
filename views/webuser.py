from forms import SingUpForm, FormPageInfo
from flask import render_template, current_app, redirect
from database.dbinit import WebUser
from passlib.hash import pbkdf2_sha256 as hasher
from pony.orm import db_session
from pony.orm.core import TransactionIntegrityError


def signup_page():
    form = SingUpForm()
    form_errors = form.username.errors + form.password.errors + form.password_verify.errors + \
                  form.date_of_registration.errors + form.name.errors + form.surname.errors
    info = FormPageInfo(form=form, title="Sign Up", errors=form_errors)

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
                # TODO Kayıt olunca nereye yönlendirecek, url_for ile yaz
                return redirect("/")
            # If username already exists in database
            except TransactionIntegrityError:
                info.errors += ("'" + form.data["username"] + "' username already exists.",)

    return render_template("webuser/signup.html", info=info)
