from flask import redirect, url_for, flash, render_template, request, current_app
from flask_login import current_user, login_required, login_user, logout_user
from passlib.hash import pbkdf2_sha256 as hasher
from pony.orm import TransactionIntegrityError, ObjectNotFound, db_session

from database.dbinit import WebUser
from forms import SingUpForm, FormPageInfo, WebuserForm, LoginForm, EditWebUserForm
from bots.telegram_bot import telegram_bot, admin_chat_id
from views import LayoutPageInfo, get_translation
from views.authorizations import admin_required
from views.webuser.auxiliary import FlaskUser, MemberInfo
from views.webuser.db import add_webuser


def signup_page():
    t = get_translation()['views']['webuser']['signup_page']
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = SingUpForm()

    if form.validate_on_submit():
        if form.data["password"] != form.data["password_verify"]:
            flash(u"%s" % t['passwords_not_same'], 'danger')
        else:
            try:
                add_webuser(form, is_admin=form.data["username"] in current_app.config["ADMIN_USERS"])
                return redirect(url_for("home_page"))
            except TransactionIntegrityError:  # If username already exists in database
                flash(u"'%s' %s" % (form.data["username"], t['username_exists'],), 'danger')
            except Exception as e:  # If there is another exception
                flash(u"%s:\n%s %s" % (t['unexpected_exception'], type(e), e,), 'danger')

    info = FormPageInfo(form=form, title="Sign Up")

    return render_template("form.html", layout_page=LayoutPageInfo("Sign Up"), info=info)


@admin_required
def add_webuser_page():
    t = get_translation()['views']['webuser']['add_webuser_page']
    form = WebuserForm()

    if form.validate_on_submit():
        if form.data["password"] != form.data["password_verify"]:
            flash(u"%s" % t['passwords_not_same'], 'danger')
        else:
            try:
                add_webuser(form)
                return redirect(url_for("home_page"))
            except TransactionIntegrityError:  # If username already exists in database
                flash(u"'%s' %s" % (form.data["username"], t['username_exists'],), 'danger')
            except Exception as e:  # If there is another exception
                flash(u"%s:\n%s %s" % (t['unexpected_exception'], type(e), e,), 'danger')

    info = FormPageInfo(form=form, title="Sign Up")

    return render_template("form.html", layout_page=LayoutPageInfo("Sign Up"), info=info)


def login_page():
    t = get_translation()['views']['webuser']['login_page']

    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = FlaskUser(form.data['username'])
            if hasher.verify(form.data['password'], user.webuser.password_hash) and user.is_active:
                telegram_message = "%s (%s) giriş yaptı." % (user.webuser.name_surname(), user.username)
                telegram_bot.sendMessage(admin_chat_id, telegram_message)
                login_user(user)
                flash("%s" % t['success'], 'success')
                next_page = request.args.get("next", url_for("home_page"))
                return redirect(next_page)
            else:  # If password is incorrect
                flash(u"%s" % t['unsuccess'], 'danger')
        except ObjectNotFound:  # If username already exists in database
            flash(u"%s" % t['unsuccess'], 'danger')

    info = FormPageInfo(title='Login', form=form)

    return render_template("form.html", layout_page=LayoutPageInfo("Login"), info=info)


@login_required
def logout():
    t = get_translation()['views']['webuser']['logout']
    logout_user()
    flash(u"%s" % t['success'], 'success')
    return redirect(url_for("home_page"))


@login_required
def profile():
    with db_session:
        webuser = WebUser[current_user.username]
        members = []
        for member in webuser.members_index.sort_by(lambda m: m.sandik_ref.id):
            members.append(MemberInfo(member))
        return render_template("webuser/profile.html", layout_page=LayoutPageInfo("Profile"), user=webuser,
                               members=members)


@login_required
@db_session
def edit_webuser_info_page():
    t = get_translation()['views']['webuser']['edit_webuser_info_page']
    webuser = WebUser[current_user.username]

    form = EditWebUserForm()
    form.username.data = webuser.username
    form.name.render_kw["placeholder"] = webuser.name
    form.surname.render_kw["placeholder"] = webuser.surname
    form.password_verify = None
    form.telegram_chat_id.render_kw["placeholder"] = webuser.telegram_chat_id

    if form.validate_on_submit():
        if not hasher.verify(form.old_password.data, webuser.password_hash):
            flash(u"%s" % t['old_password_not_correct'], 'danger')
        elif form.new_password.data != form.new_password_verify.data:
            print(form.new_password, form.new_password_verify)
            flash(u"%s" % t['new_passwords_not_same'], 'danger')
        else:
            try:
                # if form.username.data:
                #     webuser.username = form.username.data
                if form.name.data:
                    webuser.name = form.name.data
                if form.surname.data:
                    webuser.surname = form.surname.data
                if form.new_password.data:
                    webuser.password_hash = hasher.hash(form.new_password.data)
                if form.telegram_chat_id.data:
                    webuser.telegram_chat_id = form.telegram_chat_id.data
                    telegram_bot.send_message(form.telegram_chat_id.data, "Bot aktif edildi.")
                return redirect(url_for("home_page"))
            except TransactionIntegrityError:  # If username already exists in database
                flash(u"'%s' username already exists." % (form.data["username"],), 'danger')
            except Exception as e:  # If there is another exception
                flash(u"%s:\n%s %s" % (t['unexpected_exception'], type(e), e,), 'danger')

    info = FormPageInfo(form=form, title="Edit User's Info Page")
    flash(u'Değiştirmek istemediğiniz alanları boş bırakabilirsiniz.', 'info')
    return render_template("form.html", layout_page=LayoutPageInfo("Edit User's Info Page"), info=info)
