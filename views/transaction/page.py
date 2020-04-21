import json
from copy import copy
from datetime import date

from flask import abort, redirect, url_for, render_template, flash, current_app
from flask_login import login_required, current_user
from pony.orm import db_session, select, desc

import database.auxiliary as db_aux
from bots.telegram_bot import telegram_bot
from database.auxiliary import name_surname
from database.dbinit import Member, Sandik, WebUser, Transaction, Debt, Share
from database.exceptions import NegativeTransaction, DuplicateContributionPeriod, Overpayment
from forms import TransactionForm, FormPageInfo, ContributionForm, DebtForm, PaymentForm, CustomTransactionSelectForm
from views import LayoutPageInfo, get_translation
from views.authorizations import authorization_to_the_sandik_required, is_there_authorization_to_the_sandik
from views.sandik.auxiliary import get_chat_ids_of_sandik_admins
from views.transaction.auxiliary import debt_type_choices, share_choices, unpaid_dues_choices, debt_choices, \
    member_choices, Period, UnpaidDebt, local_name_surname
from views.transaction.db import remove_transaction_vw
import views.transaction.db as transaction_db


@login_required
def add_transaction_page(sandik_id):
    with db_session:
        member = Member.get(sandik_ref=Sandik[sandik_id], webuser_ref=WebUser[current_user.username])

        # If member is not in members of the sandik
        if not member:
            abort(404)

        # Create contribution form
        form = TransactionForm()

        # Add shares of member to form.share
        form.share.choices += share_choices(member)

        if form.validate_on_submit():
            try:
                transaction_db.add_other_transaction(form, current_user.username)
                return redirect(url_for('member_unconfirmed_transactions_page', sandik_id=sandik_id))
            except NegativeTransaction as nt:
                flash(u'%s' % nt, 'danger')

        info = FormPageInfo(form=form, title=get_translation()['forms']['transaction']["page_name"])
        return render_template("form.html",
                               layout_page=LayoutPageInfo(get_translation()['forms']['transaction']["page_name"]),
                               info=info)


@login_required
def add_contribution_page(sandik_id):
    with db_session:
        member = Member.get(sandik_ref=Sandik[sandik_id], webuser_ref=WebUser[current_user.username])
        sandik = Sandik[sandik_id]
        # If member is not in members of the sandik
        if not member:
            abort(404)

        # Create contribution form
        form = ContributionForm()

        # Add shares of member to form.share
        form.share.choices += share_choices(member)
        form.amount.render_kw["value"] = sandik.contribution_amount

        if form.validate_on_submit():
            # TODO kontrolleri yap
            try:
                transaction_db.add_contributions(form, current_user.username)
                telegram_bot.send_message_to_list(
                    get_chat_ids_of_sandik_admins(sandik=sandik),
                    "*%s*\n%s aidat işlemi ekledi. İşlem onay bekliyor." % (sandik.name, member.webuser_ref.name_surname())
                )
                return redirect(url_for('member_unconfirmed_transactions_page', sandik_id=sandik_id))
            except DuplicateContributionPeriod as dcp:
                flash(u'%s' % dcp, 'danger')

        info = FormPageInfo(form=form, title=get_translation()['forms']['contribution']["page_name"])
        return render_template("transaction/contribution_form.html",
                               layout_page=LayoutPageInfo(get_translation()['forms']['contribution']["page_name"]),
                               info=info, periods_of=json.dumps(unpaid_dues_choices(member)),
                               all_periods_of=json.dumps(unpaid_dues_choices(member, is_there_old=True)),
                               contribution_amount=sandik.contribution_amount)


@login_required
def add_debt_page(sandik_id):
    # TODO max amount borç tipine, içerdeki parasına ve diğer kurallara göre belirlenecek, burada da olabilir,
    #  formu aldıktan sonra da
    with db_session:
        sandik = Sandik[sandik_id]
        member = Member.get(sandik_ref=sandik, webuser_ref=WebUser[current_user.username])

        # If member is not in members of the sandik
        if not member:
            abort(404)

        # Create contribution form
        form = DebtForm()

        # Add shares of member to form.share
        form.share.choices += share_choices(member)

        # Add debt types of the sandik to form.debt_type
        form.debt_type.choices += debt_type_choices(sandik)

        # TODO taksit sayısı borç tipine ve miktarına göre değiş
        # Add number of installment range to form.number_of_installment
        form.number_of_installment.choices += [(i, i) for i in range(1, 13)]

        if form.validate_on_submit():
            # TODO kontrolleri yap, (borcu varsa bir daha alamaz[sayfaya giriş de engellenebilir], en fazla taksit,
            #  parasına göre en fazla borç)
            transaction_db.add_debt(form, current_user.username)
            telegram_bot.send_message_to_list(
                get_chat_ids_of_sandik_admins(sandik=sandik),
                "*%s*\n%s borç işlemi ekledi. İşlem onay bekliyor." % (sandik.name, member.webuser_ref.name_surname())
            )

            return redirect(url_for('member_unconfirmed_transactions_page', sandik_id=sandik_id))

        info = FormPageInfo(form=form, title=get_translation()['forms']['debt']["page_name"])
        return render_template('form.html',
                               layout_page=LayoutPageInfo(get_translation()['forms']['debt']["page_name"]), info=info)


@login_required
def add_payment_page(sandik_id):
    with db_session:
        member = Member.get(sandik_ref=Sandik[sandik_id], webuser_ref=WebUser[current_user.username])
        sandik = Sandik[sandik_id]
        # If member is not in members of the sandik
        if not member:
            abort(404)

        # Create contribution form
        form = PaymentForm()

        # Add all debts of all shares of member to form.debt
        form.debt.choices = debt_choices(member)

        if form.validate_on_submit():
            if Debt[form.debt.data].transaction_ref.share_ref.member_ref.webuser_ref.username != current_user.webuser.username:
                flash(u'Başka birisinin borcunu ödeyemezsiniz. Yöneticiye başvurunuz.', 'danger')
            else:
                try:
                    transaction_db.add_payment(form, current_user.username)
                    telegram_bot.send_message_to_list(
                        get_chat_ids_of_sandik_admins(sandik=sandik),
                        "*%s*\n%s borç işlemi ekledi. İşlem onay bekliyor." % (sandik.name, member.webuser_ref.name_surname())
                    )
                    return redirect(url_for('member_unconfirmed_transactions_page', sandik_id=sandik_id))
                except Overpayment as op:
                    flash(u'%s' % op, 'danger')

        info = FormPageInfo(form=form, title=get_translation()['forms']['payment']["page_name"])
        return render_template('form.html',
                               layout_page=LayoutPageInfo(get_translation()['forms']['payment']["page_name"]),
                               info=info)


@authorization_to_the_sandik_required(writing_transaction=True)
def add_custom_transaction_for_admin_page(sandik_id):
    with db_session:
        max_id = select(t.id for t in Transaction).max() + 1
        sandik = Sandik[sandik_id]
        # member = Member.get(sandik_ref=sandik, webuser_ref=WebUser[current_user.username])

        # # If member is not in members of the sandik
        # if not member:
        #     abort(404)
        # if not member.member_authority_type_ref.is_admin:
        #     abort(401)

        # Create forms
        c_form = ContributionForm()
        d_form = DebtForm()
        p_form = PaymentForm()
        o_form = TransactionForm()

        # Prepare dictionary of shares, debts, and periods of all members for add choices of forms
        shares_of = {}
        debts_of = {}
        periods_of = {}
        all_periods_of = {}
        for member in sandik.members_index:
            shares_of[member.id] = share_choices(member)
            debts_of[member.id] = debt_choices(member)
            periods_of.update(unpaid_dues_choices(member))
            all_periods_of.update(unpaid_dues_choices(member, is_there_old=True))

        # add contribution amount
        c_form.amount.render_kw["value"] = sandik.contribution_amount

        # Add debt types of the sandik to d_form.debt_type
        d_form.debt_type.choices += debt_type_choices(sandik)

        # TODO taksit sayısı borç tipine ve miktarına göre değiş
        # Add number of installment range to d_form.number_of_installment
        d_form.number_of_installment.choices += [(i, i) for i in range(1, 13)]

        if c_form.validate_on_submit():
            try:
                transaction_db.add_contributions(c_form, current_user.username, is_confirmed=True)
                return redirect(url_for('add_custom_transaction_for_admin_page', sandik_id=sandik_id))
            except DuplicateContributionPeriod as dcp:
                flash(u'%s' % dcp, 'danger')
        elif d_form.validate_on_submit():
            transaction_db.add_debt(d_form, current_user.username, is_confirmed=True)
            return redirect(url_for('add_custom_transaction_for_admin_page', sandik_id=sandik_id))
        elif p_form.validate_on_submit():
            try:
                transaction_db.add_payment(p_form, current_user.username, is_confirmed=True)
                return redirect(url_for('add_custom_transaction_for_admin_page', sandik_id=sandik_id))
            except Overpayment as op:
                flash(u'%s' % op, 'danger')
        elif o_form.validate_on_submit():
            try:
                transaction_db.add_other_transaction(o_form, current_user.username, is_confirmed=True)
                return redirect(url_for('add_custom_transaction_for_admin_page', sandik_id=sandik_id))
            except NegativeTransaction as nt:
                flash(u'%s' % nt, 'danger')

        forms = [c_form, d_form, p_form, o_form]
        errors = []
        for form in forms:
            for field in form:
                errors += field.errors

        select_form = CustomTransactionSelectForm()
        select_form.member.choices += member_choices(sandik.id)
        forms.insert(0, select_form)
        return render_template("transaction/custom_transaction_form.html", forms=forms, errors=errors,
                               layout_page=LayoutPageInfo(get_translation()['forms']['transaction']["page_name"]),
                               periods_of=json.dumps(periods_of), all_periods_of=json.dumps(all_periods_of),
                               shares_of=json.dumps(shares_of), debts_of=json.dumps(debts_of),
                               contribution_amount=sandik.contribution_amount)


@authorization_to_the_sandik_required(reading_transaction=True)
def transactions_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]

        transactions = select(transaction for transaction in Transaction
                              if transaction.share_ref.member_ref.sandik_ref == sandik and
                              transaction.confirmed_by and not transaction.deleted_by).sort_by(desc(Transaction.id))[:]
        return render_template("transactions.html", layout_page=LayoutPageInfo("All Transactions of The Sandik"),
                               transactions=transactions)


@login_required
def transaction_information_page(sandik_id, transaction_id):
    with db_session:
        transaction = Transaction[transaction_id]
        is_authorized = False
        # TODO abort u değistir
        if transaction.share_ref.member_ref.sandik_ref.id != sandik_id:
            abort(404)
        elif is_there_authorization_to_the_sandik(sandik_id, reading_transaction=True):
            is_authorized = True
            pass
        elif transaction.share_ref.member_ref.webuser_ref.username != current_user.webuser.username:
            flash(u"Bu sayfaya giriş yetkiniz yok.", 'danger')
            return current_app.login_manager.unauthorized()

        if transaction.deleted_by:
            flash(u'Bu işlem %s (%s) tarafından silinmiştir...' % (
                local_name_surname(webuser=transaction.deleted_by), transaction.deleted_by.username,), 'warning')
        if not transaction.confirmed_by:
            flash(u'Bu işlem henüz onaylanmamış...', 'warning')

        payments = None
        if transaction.debt_ref or transaction.payment_ref:
            debt = transaction.debt_ref or transaction.payment_ref.debt_ref
            payments = debt.payments_index.filter(
                lambda p: bool(p.transaction_ref.confirmed_by) and not bool(p.transaction_ref.deleted_by)).sort_by(
                lambda p: p.id)

        return render_template("transaction/transaction_information.html",
                               layout_page=LayoutPageInfo("Transaction information"), t=transaction, payments=payments,
                               is_authorized=is_authorized)


@login_required
def member_transactions_in_sandik_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]
        webuser = current_user.webuser

        transactions = select(transaction for transaction in Transaction
                              if transaction.share_ref.member_ref.webuser_ref == webuser
                              and transaction.share_ref.member_ref.sandik_ref == sandik
                              and transaction.confirmed_by and not transaction.deleted_by)[:]
        return render_template("transactions.html", layout_page=LayoutPageInfo("My Transactions"),
                               transactions=transactions)


@login_required
def unpaid_transactions_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]
        webuser = WebUser[current_user.username]
        member = Member.get(webuser_ref=webuser, sandik_ref=sandik)
        if not (member or current_user.is_admin):
            flash(u"Bu sandığın üyesi değilsiniz.", 'danger')
            return current_app.login_manager.unauthorized()
        is_autrorized = is_there_authorization_to_the_sandik(sandik_id, reading_transaction=True)
        member_list = sandik.members_index.sort_by(lambda m: m.webuser_ref.name + " " + m.webuser_ref.surname) if is_autrorized else [member]

        unpaid_contributions = {}
        for member in member_list:
            unpaid_dues = unpaid_dues_choices(member)
            for share in unpaid_dues:
                for due in unpaid_dues[share]:
                    if unpaid_contributions.get(due[0]):
                        unpaid_contributions[due[0]].append((Share[share], name_surname(share_id=share)))
                    else:
                        unpaid_contributions[due[0]] = [(Share[share], name_surname(share_id=share))]

        unpaid_payments = {}
        for debt in select(debt for debt in Debt if debt.transaction_ref.share_ref.member_ref in member_list
                                                    and debt.remaining_debt and debt.transaction_ref.confirmed_by
                                                    and not debt.transaction_ref.deleted_by).sort_by(lambda
                                                                                                             d: d.transaction_ref.share_ref.member_ref.webuser_ref.name + " " + d.transaction_ref.share_ref.member_ref.webuser_ref.surname + " " + str(
            d.transaction_ref.share_ref.share_order_of_member))[:]:
            unpaid_first = Period.last_period_2(period=debt.starting_period, times=debt.paid_installment)
            add_debt = UnpaidDebt(debt)
            for period in Period.months_between_two_period(first_period=unpaid_first, second_period=debt.due_period):
                add_debt.order_of_installment += 1
                x = copy(add_debt)
                add_debt.installment_amount_of_this_period = add_debt.debt.installment_amount
                if unpaid_payments.get(period):
                    unpaid_payments[period].append(x)
                else:
                    unpaid_payments[period] = [x]

        periods = []
        for ekle in list(set(list(unpaid_contributions.keys()) + list(unpaid_payments.keys()))):
            if len(periods) == 0:
                periods.append((ekle, Period.period_name(ekle),))
            else:
                eklendi = False
                for i in range(len(periods)):
                    if Period.compare(after=periods[i][0], before=ekle):
                        periods.insert(i, (ekle, Period.period_name(ekle),))
                        eklendi = True
                        break
                if not eklendi:
                    periods.append((ekle, Period.period_name(ekle),))

        return render_template("transaction/unpaid_transactions.html",
                               layout_page=LayoutPageInfo("Unpaid transactions"), periods=periods,
                               contributions=unpaid_contributions, payments=unpaid_payments)


@login_required
def unpaid_transactions_of_member_page(sandik_id):
    sandik = Sandik[sandik_id]
    webuser = WebUser[current_user.username]
    member = Member.get(webuser_ref=webuser, sandik_ref=sandik)
    if not member:
        flash(u"Bu sandığın üyesi değilsiniz.", 'danger')
        return current_app.login_manager.unauthorized()
    member_list = [member]

    unpaid_contributions = {}
    unpaid_dues = unpaid_dues_choices(member)
    for share in unpaid_dues:
        for due in unpaid_dues[share]:
            if unpaid_contributions.get(due[0]):
                unpaid_contributions[due[0]].append((Share[share], name_surname(share_id=share)))
            else:
                unpaid_contributions[due[0]] = [(Share[share], name_surname(share_id=share))]

    unpaid_payments = {}
    for debt in select(debt for debt in Debt
                       if debt.transaction_ref.share_ref.member_ref == member and debt.remaining_debt and
                          debt.transaction_ref.is_valid()
                       ).sort_by(lambda d: d.transaction_ref.share_ref.name_surname_share())[:]:
        unpaid_first = Period.last_period_2(period=debt.starting_period, times=debt.paid_installment)
        add_debt = UnpaidDebt(debt)
        for period in Period.months_between_two_period(first_period=unpaid_first, second_period=debt.due_period):
            add_debt.order_of_installment += 1
            x = copy(add_debt)
            add_debt.installment_amount_of_this_period = add_debt.debt.installment_amount
            if unpaid_payments.get(period):
                unpaid_payments[period].append(x)
            else:
                unpaid_payments[period] = [x]

    periods = []
    for ekle in list(set(list(unpaid_contributions.keys()) + list(unpaid_payments.keys()))):
        if len(periods) == 0:
            periods.append((ekle, Period.period_name(ekle),))
        else:
            eklendi = False
            for i in range(len(periods)):
                if Period.compare(after=periods[i][0], before=ekle):
                    periods.insert(i, (ekle, Period.period_name(ekle),))
                    eklendi = True
                    break
            if not eklendi:
                periods.append((ekle, Period.period_name(ekle),))

    return render_template("transaction/unpaid_transactions.html",
                           layout_page=LayoutPageInfo("Unpaid transactions"), periods=periods,
                           contributions=unpaid_contributions, payments=unpaid_payments)


# TODO işlem, sandığın işlemi olmak zorunda
@authorization_to_the_sandik_required(is_admin=True)
def delete_transaction(sandik_id, transaction_id):
    with db_session:
        if not remove_transaction_vw(transaction_id):
            return redirect(url_for('transaction_information_page',
                                    sandik_id=sandik_id, transaction_id=transaction_id))
    return redirect(url_for('transactions_page', sandik_id=sandik_id))


@authorization_to_the_sandik_required(reading_transaction=True)
def unconfirmed_transactions_page(sandik_id):
    with db_session:
        unconfirmed_transactions = select(
            t for t in Transaction if
            t.share_ref.member_ref.sandik_ref.id == sandik_id and not t.confirmed_by and not t.deleted_by).sort_by(
            lambda t: t.id)
        return render_template("transaction/unconfirmed_transactions.html",
                               layout_page=LayoutPageInfo("Unpaid transactions"),
                               unconfirmed_transactions=unconfirmed_transactions, is_authorized=True)


@login_required
def member_unconfirmed_transactions_page(sandik_id):
    with db_session:
        if not Member.get(webuser_ref=WebUser[current_user.username], sandik_ref=Sandik[sandik_id]):
            flash(u"Bu sandığın üyesi değilsiniz.", 'danger')
            return current_app.login_manager.unauthorized()
        unconfirmed_transactions = select(t for t in Transaction
                                          if t.share_ref.member_ref.webuser_ref.username == current_user.username
                                          and t.share_ref.member_ref.sandik_ref.id == sandik_id
                                          and not t.confirmed_by and not t.deleted_by).sort_by(lambda t: t.id)
        return render_template("transaction/unconfirmed_transactions.html",
                               layout_page=LayoutPageInfo("Unpaid transactions"),
                               unconfirmed_transactions=unconfirmed_transactions, is_authorized=False)


# TODO islem sandıkta mı diye kontrol et
@authorization_to_the_sandik_required(is_admin=True)
def confirm_transaction(sandik_id, transaction_id):
    with db_session:
        transaction = Transaction[transaction_id]

        if transaction.deleted_by:
            flash(u"%s" % get_translation()['unconfirmed']['deleted'], 'danger')
            return redirect(url_for('transaction_information_page', sandik_id=sandik_id, transaction_id=transaction.id))
        elif transaction.id != select(t.id for t in Transaction
                                      if t.share_ref.member_ref.sandik_ref.id == sandik_id and not t.confirmed_by
                                      and not t.deleted_by and t.share_ref == transaction.share_ref
                                      and t.transaction_date <= date.today()).min():
            flash(u"%s" % get_translation()['unconfirmed']['not_first_transaction'], 'danger')
            return redirect(url_for('unconfirmed_transactions_page', sandik_id=sandik_id))

        if transaction.payment_ref:
            try:
                db_aux.confirm_payment(transaction_id, current_user.username)
            except Overpayment as op:
                flash(u"%s" % op, 'danger')
        elif transaction.debt_ref:
            db_aux.confirm_debt(t_id=transaction_id, confirmed_by_username=current_user.username)
            pass
        elif transaction.contribution_index:
            try:
                db_aux.confirm_contributions(transaction_id, current_user.username)
            except DuplicateContributionPeriod as dcp:
                flash(u'%s' % dcp, 'danger')
        else:
            try:
                db_aux.confirm_other_transaction(t_id=transaction_id, confirmed_by_username=current_user.username)
            except NegativeTransaction as nt:
                flash(u'%s' % nt, 'danger')

    return redirect(url_for('unconfirmed_transactions_page', sandik_id=sandik_id))
