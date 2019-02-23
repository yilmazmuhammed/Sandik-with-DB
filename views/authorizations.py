from functools import wraps

from flask import current_app, flash
from flask_login import login_required, current_user
from pony.orm import db_session


def authorization_to_the_required(reading_transaction=False, writing_transaction=False,
                                  adding_member=False, throwing_member=False):
    def authorization_to_the_required_decorator(func):
        @login_required
        @wraps(func)
        def decorated_view(sandik_id, *args, **kwargs):
            # TODO bir sandıkta bir webuser'ın sadece 1 üyeliği olmalı
            with db_session:
                member = current_user.webuser.members_index.select(lambda m: m.sandik_ref.id == sandik_id)[:][0]
                ma = member.member_authority_type_ref
                if not ma.is_admin and not (ma.reading_transaction >= reading_transaction
                                            and ma.writing_transaction >= writing_transaction
                                            and ma.adding_member >= adding_member
                                            and ma.throwing_member >= throwing_member):
                    # TODO yetkilere göre sayfa
                    flash(u"Bu sayfaya giriş yetkiniz yok.", 'danger')
                    return current_app.login_manager.unauthorized()
            return func(sandik_id, *args, **kwargs)
        return decorated_view
    return authorization_to_the_required_decorator
