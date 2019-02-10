from flask import redirect, url_for, flash, render_template, abort, request, current_app
from flask_login import current_user, login_required, login_user, logout_user
from passlib.hash import pbkdf2_sha256 as hasher
from pony.orm import TransactionIntegrityError, ObjectNotFound, db_session, select

from database.dbinit import WebUser, Sandik, Transaction
from forms import SingUpForm, FormPageInfo, WebuserForm, LoginForm
from views.webuser.auxiliary import FlaskUser, MemberInfo
from views.webuser.db import add_webuser


def signup():
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
def add_webuser():
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


def login():
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
        except ObjectNotFound:  # If username already exists in database
            flash(u"Username or password is incorrect.", 'danger')

    info = FormPageInfo(title='Login', form=form)

    return render_template("form.html", info=info)


@login_required
def logout():
    logout_user()
    flash(u"You have logged out.", 'success')
    return redirect(url_for("home_page"))


@login_required
def profile():
    with db_session:
        webuser = WebUser[current_user.username]
        members = []
        for member in webuser.members_index:
            members.append(MemberInfo(member))
        return render_template("webuser/profile.html", user=webuser, members=members)


@login_required
def transactions_in_sandik(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]
        webuser = current_user.webuser

        transactions = select(transaction for transaction in Transaction
                              if transaction.share_ref.member_ref.webuser_ref == webuser
                              and transaction.share_ref.member_ref.sandik_ref == sandik)[:]
        return render_template("transactions.html", transactions=transactions)
