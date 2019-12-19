from datetime import date

from flask import flash
from flask_login import current_user
from pony.orm import select, db_session, count

import database.auxiliary as db_aux
from database.dbinit import Share, Contribution, Transaction, Debt
from database.exceptions import RemoveTransactionError, NegativeTransaction, DuplicateContributionPeriod, Overpayment
from forms import ContributionForm, TransactionForm, DebtForm, PaymentForm
from views import get_translation


# TODO Flash'a çeviri ekle
@db_session
def remove_transaction_vw(transaction_id):
    transaction = Transaction[transaction_id]
    if transaction.confirmed_by:
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


@db_session
def add_other_transaction(form: TransactionForm, username, is_confirmed=False):
    share = Share[form.share.data]
    sum_of_other = select(t.amount for t in share.transactions_index
                          if not t.contribution_index and not t.debt_ref and not t.payment_ref
                          and t.confirmed_by and not t.deleted_by).sum()
    if sum_of_other + form.amount.data < 0:
        raise NegativeTransaction(get_translation()['exceptions']['negative_other'])

    t = db_aux.insert_transaction(form.transaction_date.data, form.amount.data, form.share.data, form.explanation.data,
                                  created_by_username=username)

    if is_confirmed:
        db_aux.confirm_other_transaction(t_id=t.id, confirmed_by_username=username)

    return True


@db_session
def add_debt(form: DebtForm, username, is_confirmed=False):
    d = db_aux.insert_debt(form.transaction_date.data, form.amount.data, form.share.data, form.explanation.data,
                           form.debt_type.data, form.number_of_installment.data,
                           created_by_username=username)

    if is_confirmed:
        db_aux.confirm_debt(t_id=d.transaction_ref.id, confirmed_by_username=username)

    return True


@db_session
def add_contributions(form: ContributionForm, username, is_confirmed=False):
    share = Share[form.share.data]
    new_periods = form.contribution_period.data

    old_periods = select(c.contribution_period for c in Contribution
                         if c.transaction_ref.share_ref == share
                         and c.transaction_ref.confirmed_by and not c.transaction_ref.deleted_by)[:]

    for new_period in new_periods:
        if new_period in old_periods:
            raise DuplicateContributionPeriod(get_translation()['exceptions']['duplicate_contribution_period'])

    contributions = db_aux.insert_contribution(form.transaction_date.data, form.amount.data, share.id,
                                               form.explanation.data, new_periods, created_by_username=username)

    if not contributions:
        return False

    if is_confirmed:
        db_aux.confirm_contributions(t_id=contributions[0].transaction_ref.id, confirmed_by_username=username)

    return True


@db_session
def add_payment(form: PaymentForm, username, is_confirmed=False):
    debt = Debt[form.debt.data]

    if form.amount.data > debt.remaining_debt:
        raise Overpayment(get_translation()['exceptions']['overpayment'])

    p = db_aux.insert_payment(form.transaction_date.data, form.amount.data, form.explanation.data,
                              created_by_username=username, debt_id=form.debt.data)

    if is_confirmed:
        db_aux.confirm_payment(t_id=p.transaction_ref.id, confirmed_by_username=username)

    return True
