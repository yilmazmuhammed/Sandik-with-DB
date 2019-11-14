import json
from copy import copy
from datetime import date

from flask import abort, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from pony.orm import db_session, select, desc

from database.auxiliary import insert_contribution, insert_debt, insert_payment, insert_transaction, name_surname
from database.dbinit import Member, Sandik, WebUser, Transaction, Debt, Share
from forms import TransactionForm, FormPageInfo, ContributionForm, DebtForm, PaymentForm, CustomTransactionSelectForm
from views import LayoutPageInfo
from views.authorizations import authorization_to_the_sandik_required
from views.transaction.auxiliary import debt_type_choices, share_choices, unpaid_dues_choices, debt_choices, \
    member_choices, Period, UnpaidDebt, local_name_surname
from views.transaction.db import add_contribution


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
            insert_transaction(form.transaction_date.data, form.amount.data, form.share.data, form.explanation.data,
                               created_by_username=current_user.webuser.username)

            return redirect(url_for('member_transactions_in_sandik_page', sandik_id=sandik_id))

        info = FormPageInfo(form=form, title="Add Transaction")
        return render_template("form.html", layout_page=LayoutPageInfo("Add Transaction"), info=info)


@login_required
def add_contribution_page(sandik_id):
    with db_session:
        member = Member.get(sandik_ref=Sandik[sandik_id], webuser_ref=WebUser[current_user.username])

        # If member is not in members of the sandik
        if not member:
            abort(404)

        # Create contribution form
        form = ContributionForm()

        # Add shares of member to form.share
        form.share.choices += share_choices(member)

        if form.validate_on_submit():
            # TODO kontrolleri yap
            if add_contribution(form):
                return redirect(url_for('transactions_in_sandik', sandik_id=sandik_id))

        info = FormPageInfo(form=form, title="Add Contribution")
        return render_template("transaction/contribution_form.html", layout_page=LayoutPageInfo("Add Contribution"),
                               info=info, periods_of=json.dumps(unpaid_dues_choices(member)),
                               all_periods_of=json.dumps(unpaid_dues_choices(member, is_there_old=True)))


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
            insert_debt(form.transaction_date.data, form.amount.data, form.share.data, form.explanation.data,
                        form.debt_type.data, form.number_of_installment.data,
                        created_by_username=current_user.webuser.username)

            return redirect(url_for('member_transactions_in_sandik_page', sandik_id=sandik_id))

        info = FormPageInfo(form=form, title="Take Debt")
        return render_template('form.html', layout_page=LayoutPageInfo("Take Debt"), info=info)


@login_required
def add_payment_page(sandik_id):
    with db_session:
        member = Member.get(sandik_ref=Sandik[sandik_id], webuser_ref=WebUser[current_user.username])

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
            elif insert_payment(form.transaction_date.data, form.amount.data, form.explanation.data,
                                created_by_username=current_user.webuser.username, debt_id=form.debt.data):
                return redirect(url_for('member_transactions_in_sandik_page', sandik_id=sandik_id))

        info = FormPageInfo(form=form, title="Add payment")
        return render_template('form.html', layout_page=LayoutPageInfo("Add payment"), info=info)


@authorization_to_the_sandik_required(writing_transaction=True)
def add_custom_transaction_for_admin_page(sandik_id):
    with db_session:
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

        # Add debt types of the sandik to d_form.debt_type
        d_form.debt_type.choices += debt_type_choices(sandik)

        # TODO taksit sayısı borç tipine ve miktarına göre değiş
        # Add number of installment range to d_form.number_of_installment
        d_form.number_of_installment.choices += [(i, i) for i in range(1, 13)]

        if c_form.validate_on_submit():
            if insert_contribution(c_form.transaction_date.data, c_form.amount.data, c_form.share.data,
                                   c_form.explanation.data, c_form.contribution_period.data,
                                   created_by_username=current_user.webuser.username,
                                   confirmed_by_username=current_user.webuser.username):
                return redirect(url_for('add_custom_transaction_for_admin_page', sandik_id=sandik_id))
        elif d_form.validate_on_submit():
            insert_debt(d_form.transaction_date.data, d_form.amount.data, d_form.share.data, d_form.explanation.data,
                        d_form.debt_type.data, d_form.number_of_installment.data,
                        created_by_username=current_user.webuser.username,
                        confirmed_by_username=current_user.webuser.username)
            return redirect(url_for('add_custom_transaction_for_admin_page', sandik_id=sandik_id))
        elif p_form.validate_on_submit():
            if insert_payment(p_form.transaction_date.data, p_form.amount.data, p_form.explanation.data,
                              created_by_username=current_user.webuser.username,
                              confirmed_by_username=current_user.webuser.username,
                              debt_id=p_form.debt.data):
                return redirect(url_for('add_custom_transaction_for_admin_page', sandik_id=sandik_id))
        elif o_form.validate_on_submit():
            insert_transaction(o_form.transaction_date.data, o_form.amount.data, o_form.share.data,
                               o_form.explanation.data, created_by_username=current_user.webuser.username,
                               confirmed_by_username=current_user.webuser.username)
            return redirect(url_for('add_custom_transaction_for_admin_page', sandik_id=sandik_id))

        forms = [c_form, d_form, p_form, o_form]
        errors = []
        for form in forms:
            for field in form:
                errors += field.errors

        select_form = CustomTransactionSelectForm()
        select_form.member.choices += member_choices(sandik.id)
        forms.insert(0, select_form)
        return render_template("transaction/custom_transaction_form.html", forms=forms, errors=errors,
                               layout_page=LayoutPageInfo("Add Transaction"),
                               periods_of=json.dumps(periods_of), all_periods_of=json.dumps(all_periods_of),
                               shares_of=json.dumps(shares_of), debts_of=json.dumps(debts_of))


@authorization_to_the_sandik_required(reading_transaction=True)
def transactions_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]

        transactions = select(transaction for transaction in Transaction
                              if transaction.share_ref.member_ref.sandik_ref == sandik and
                              transaction.confirmed_by and not transaction.deleted_by).sort_by(desc(Transaction.id))[:]
        return render_template("transactions.html", layout_page=LayoutPageInfo("All Transactions of The Sandik"),
                               transactions=transactions)


@authorization_to_the_sandik_required(reading_transaction=True)
def transaction_in_transactions_page(sandik_id, transaction_id):
    with db_session:
        transaction = Transaction[transaction_id]
        # TODO abort u değistir
        if transaction.share_ref.member_ref.sandik_ref.id != sandik_id:
            abort(404)

        if transaction.deleted_by:
            flash(u'Bu işlem %s (%s) tarafından silinmiştir...' % (
                local_name_surname(webuser=transaction.deleted_by), transaction.deleted_by.username,), 'danger')
        elif not transaction.confirmed_by:
            flash(u'Bu işlem henüz onaylanmamış...', 'danger')

        payments = None
        if transaction.debt_ref:
            payments = transaction.debt_ref.payments_index.filter(
                lambda p: bool(p.transaction_ref.confirmed_by) and not bool(p.transaction_ref.deleted_by)).sort_by(
                lambda p: p.id)
        elif transaction.payment_ref:
            payments = transaction.payment_ref.debt_ref.payments_index.filter(
                lambda p: bool(p.transaction_ref.confirmed_by) and not bool(p.transaction_ref.deleted_by)).sort_by(
                lambda p: p.id)

        return render_template("transaction/transaction_information.html",
                               layout_page=LayoutPageInfo("Transaction information"), t=transaction, payments=payments)


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


@authorization_to_the_sandik_required(reading_transaction=True)
def unpaid_transactions_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]

        unpaid_contributions = {}
        for member in sandik.members_index.sort_by(lambda m: m.webuser_ref.name + " " + m.webuser_ref.surname):
            unpaid_dues = unpaid_dues_choices(member)
            for share in unpaid_dues:
                for due in unpaid_dues[share]:
                    if unpaid_contributions.get(due[0]):
                        unpaid_contributions[due[0]].append((Share[share], name_surname(share_id=share)))
                    else:
                        unpaid_contributions[due[0]] = [(Share[share], name_surname(share_id=share))]

        unpaid_payments = {}
        for debt in select(debt for debt in Debt if debt.transaction_ref.share_ref.member_ref.sandik_ref == sandik
                                                    and debt.remaining_debt and debt.transaction_ref.confirmed_by
                                                    and not debt.transaction_ref.deleted_by).sort_by(lambda d: d.transaction_ref.share_ref.member_ref.webuser_ref.name + " " + d.transaction_ref.share_ref.member_ref.webuser_ref.surname + " " + str(d.transaction_ref.share_ref.share_order_of_member))[:]:
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


@authorization_to_the_sandik_required(is_admin=True)
def delete_transaction(sandik_id, transaction_id):
    with db_session:
        transaction = Transaction[transaction_id]

        if (date.today() - transaction.transaction_date).days > 1:
            flash(u'1 günden eski işlemleri silmek için yönetici ile iletişime geçiniz..', 'danger')
            return redirect(
                url_for('transaction_in_transactions_page', sandik_id=sandik_id, transaction_id=transaction_id))
        elif select(t for t in Transaction if
                    t.id >= transaction.id and t.share_ref.member_ref.sandik_ref.id == sandik_id).count() > 10:
            flash(u'Son 10 işlemden öncesi silinemez..', 'danger')
            return redirect(
                url_for('transaction_in_transactions_page', sandik_id=sandik_id, transaction_id=transaction_id))

        if transaction.debt_ref and transaction.debt_ref.payments_index.select(
                lambda p: not p.transaction_ref.deleted_by):
            flash(u'Ödeme yapılmış bir borç silinemez..', 'danger')
            return redirect(
                url_for('transaction_in_transactions_page', sandik_id=sandik_id, transaction_id=transaction_id))
        elif transaction.payment_ref and max([pn.payment_number_of_debt for pn in
                                              transaction.payment_ref.debt_ref.payments_index]) > transaction.payment_ref.payment_number_of_debt:
            flash(u'Bir borcun son ödemesi dışındaki ödemeler silinemez...', 'danger')
            return redirect(
                url_for('transaction_in_transactions_page', sandik_id=sandik_id, transaction_id=transaction_id))
        elif transaction.deleted_by:
            flash(u'Silinmiş bir işlem bir daha silinemez..', 'danger')
            return redirect(
                url_for('transaction_in_transactions_page', sandik_id=sandik_id, transaction_id=transaction_id))
        else:
            if transaction.contribution_index:
                pass
            elif transaction.debt_ref:
                pass
            elif transaction.payment_ref:
                debt = transaction.payment_ref.debt_ref
                debt.paid_debt = debt.paid_debt - transaction.amount
                debt.paid_installment = int(debt.paid_debt / debt.installment_amount)
                debt.remaining_debt = debt.transaction_ref.amount - debt.paid_debt
                debt.remaining_installment = debt.number_of_installment - debt.paid_installment

            transaction.deleted_by = WebUser[current_user.username]
    return redirect(url_for('transactions_page', sandik_id=sandik_id))
