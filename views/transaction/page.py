import json

from flask import abort, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from pony.orm import db_session, select

from database.auxiliary import insert_contribution, insert_debt, insert_payment, insert_transaction
from database.dbinit import Member, Sandik, WebUser, Transaction, Debt
from forms import TransactionForm, FormPageInfo, ContributionForm, DebtForm, PaymentForm, CustomTransactionSelectForm
from views.authorizations import authorization_to_the_sandik_required
from views.transaction.auxiliary import debt_type_choices, share_choices, unpaid_dues_choices, debt_choices, \
    member_choices
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
            insert_transaction(form.transaction_date.data, form.amount.data, form.share.data, form.explanation.data)

            return redirect(url_for('transactions_in_sandik', sandik_id=sandik_id))

        info = FormPageInfo(form=form, title="Add Transaction")
        return render_template("form.html", info=info)


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
        return render_template("transaction/contribution_form.html", info=info,
                               periods_of=json.dumps(unpaid_dues_choices(member)),
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
            insert_debt(form.transaction_date.data, form.amount.data, form.share.data, form.debt_type.data,
                        form.explanation.data, form.number_of_installment.data)

            return redirect(url_for('transactions_in_sandik', sandik_id=sandik_id))

        info = FormPageInfo(form=form, title="Take Debt")
        return render_template('form.html', info=info)


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
            if Debt[form.debt.data].transaction_ref.share_ref.member_ref.webuser_ref != current_user.webuser:
                flash(u'Başka birisinin borcunu ödeyemezsiniz. Yöneticiye başvurunuz.', 'danger')
            elif insert_payment(form.transaction_date.data, form.amount.data, form.explanation.data, form.debt.data):
                return redirect(url_for('transactions_in_sandik', sandik_id=sandik_id))

        info = FormPageInfo(form=form, title="Add payment")
        return render_template('form.html', info=info)


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
                                   c_form.explanation.data, c_form.contribution_period.data):
                # TODO return işlemler sayfasına
                return redirect(url_for('add_custom_transaction_for_admin_page'))
        elif d_form.validate_on_submit():
            insert_debt(d_form.transaction_date.data, d_form.amount.data, d_form.share.data, d_form.debt_type.data,
                        d_form.explanation.data, d_form.number_of_installment.data)
            # TODO return işlemler sayfasına
            return redirect(url_for('add_custom_transaction_for_admin_page'))
        elif p_form.validate_on_submit():
            if insert_payment(p_form.transaction_date.data, p_form.amount.data, p_form.explanation.data,
                              p_form.debt.data):
                # TODO return işlemler sayfasına
                return redirect(url_for('add_custom_transaction_for_admin_page'))
        elif o_form.validate_on_submit():
            insert_transaction(o_form.transaction_date.data, o_form.amount.data, o_form.share.data,
                               o_form.explanation.data)
            # TODO return işlemler sayfasına
            return redirect(url_for('add_custom_transaction_for_admin_page'))

        forms = [c_form, d_form, p_form, o_form]
        errors = []
        for form in forms:
            for field in form:
                errors += field.errors

        select_form = CustomTransactionSelectForm()
        select_form.member.choices += member_choices(sandik.id)
        forms.insert(0, select_form)
        return render_template("transaction/custom_transaction_form.html", forms=forms, errors=errors,
                               title="Add Contribution",
                               periods_of=json.dumps(periods_of), all_periods_of=json.dumps(all_periods_of),
                               shares_of=json.dumps(shares_of), debts_of=json.dumps(debts_of))


@authorization_to_the_sandik_required(reading_transaction=True)
def transactions_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]

        transactions = select(transaction for transaction in Transaction
                              if transaction.share_ref.member_ref.sandik_ref == sandik)[:]
        return render_template("transactions.html", transactions=transactions)


@authorization_to_the_sandik_required(reading_transaction=True)
def transaction_in_transactions_page(sandik_id, transaction_id):
    return "Bu sayfa henüz yapılmadı"


@login_required
def member_transactions_in_sandik_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]
        webuser = current_user.webuser

        transactions = select(transaction for transaction in Transaction
                              if transaction.share_ref.member_ref.webuser_ref == webuser
                              and transaction.share_ref.member_ref.sandik_ref == sandik)[:]
        return render_template("transactions.html", transactions=transactions)
