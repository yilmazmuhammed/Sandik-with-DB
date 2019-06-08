from functools import wraps

from flask import current_app, flash
from flask_login import login_required, current_user
from pony.orm import db_session


def authorization_to_the_sandik_required(reading_transaction=False, writing_transaction=False,
                                  adding_member=False, throwing_member=False, is_admin=False):
    def authorization_to_the_sandik_required_decorator(func):
        @login_required
        @wraps(func)
        def decorated_view(sandik_id, *args, **kwargs):
            # TODO bir sandıkta bir webuser'ın sadece 1 üyeliği olmalı
            if current_user.is_admin:
                return func(sandik_id, *args, **kwargs)

            with db_session:
                member = current_user.webuser.members_index.select(lambda m: m.sandik_ref.id == sandik_id)[:][0]
                ma = member.member_authority_type_ref
                if not ma.is_admin and not (ma.is_admin >= is_admin
                                            and ma.reading_transaction >= reading_transaction
                                            and ma.writing_transaction >= writing_transaction
                                            and ma.adding_member >= adding_member
                                            and ma.throwing_member >= throwing_member):
                    # TODO yetkilere göre sayfa
                    flash(u"Bu sayfaya giriş yetkiniz yok.", 'danger')
                    return current_app.login_manager.unauthorized()
            return func(sandik_id, *args, **kwargs)
        return decorated_view
    return authorization_to_the_sandik_required_decorator


def admin_required(func):
    @login_required
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            flash(u"Bu sayfaya giriş yetkiniz yok.", 'danger')
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view


@login_required
def is_there_authorization_to_the_sandik(sandik_id, reading_transaction=False, writing_transaction=False,
                                         adding_member=False, throwing_member=False):
    if current_user.is_admin:
        return True
    with db_session:
        # TODO DENE member = current_user.webuser.members_index[sandik_ref.id = sandik_id]
        member = current_user.webuser.members_index.select(lambda m: m.sandik_ref.id == sandik_id)[:][0]
        ma = member.member_authority_type_ref
        if ma.is_admin:
            return True
        if ma.reading_transaction >= reading_transaction and ma.writing_transaction >= writing_transaction \
                and ma.adding_member >= adding_member and ma.throwing_member >= throwing_member:
            return True

    return False
