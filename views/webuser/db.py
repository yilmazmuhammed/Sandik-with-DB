from datetime import date

from passlib.hash import pbkdf2_sha256 as hasher
from pony.orm import db_session

from database.dbinit import WebUser
from forms import SingUpForm


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
