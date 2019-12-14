from datetime import date

from flask import flash
from flask_login import current_user
from pony.orm import select, db_session

import database.auxiliary as db_aux
from database.dbinit import Share, Contribution, Transaction
from database.exceptions import RemoveTransactionError
from forms import ContributionForm


def add_contribution(form: ContributionForm):
    share = Share[form.share.data]
    periods = form.contribution_period.data

    for period in periods:
        if period in select(c.contribution_period for c in Contribution if c.transaction_ref.share_ref == share)[:]:
            flash(u"Daha önce ödenmiş aidat tekrar ödenemez.", 'danger')
            return False

    if db_aux.insert_contribution(form.transaction_date.data, form.amount.data, share.share_id,
                                  form.explanation.data, periods, created_by_username=current_user.webuser.username):
        return True

    return False


# TODO Flash'a çeviri ekle
@db_session
def remove_transaction_vw(transaction_id):
    transaction = Transaction[transaction_id]
    if (date.today() - transaction.transaction_date).days > 1 and not current_user.is_admin:
        flash(u'1 günden eski işlemleri silmek için yönetici ile iletişime geçiniz..', 'danger')
        return False
    elif select(t for t in Transaction if
                t.id >= transaction.id and t.share_ref.member_ref.sandik_ref.id == transaction.share_ref.member_ref.sandik_ref.id).count() > 10 and not current_user.is_admin:
        flash(u'Son 10 işlemden öncesi silinemez..', 'danger')
        return False

    try:
        db_aux.remove_transaction(transaction_id, current_user.username)
    except RemoveTransactionError as rte:
        flash(u'%s' % rte, 'danger')
        return False
    return True
