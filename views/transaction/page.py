import json

from flask import abort, redirect, url_for, render_template
from flask_login import login_required, current_user
from pony.orm import db_session

from database.dbinit import Member, Sandik, WebUser
from forms import TransactionForm, FormPageInfo, ContributionForm, DebtForm, PaymentForm, CustomTransactionSelectForm
from views.transaction.auxiliary import debt_type_choices, share_choices, unpaid_dues_choices, debt_choices, \
    member_choices
from views.transaction.db import add_contribution, add_transaction, add_debt, add_payment


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
            add_transaction(form)

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
            add_contribution(form)

            return redirect(url_for('transactions_in_sandik', sandik_id=sandik_id))
        info = FormPageInfo(form=form, title="Add Contribution")
        return render_template("transaction/contribution_form.html", info=info,
                               periodsDict=json.dumps(unpaid_dues_choices(member)))


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
            add_debt(form)

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
            if add_payment(form):
                # TODO return işlemler sayfasına
                return redirect(url_for('home_page'))

        info = FormPageInfo(form=form, title="Add payment")
        return render_template('form.html', info=info)


# TODO login_admin_required
# @login_required
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
        for member in sandik.members_index:
            shares_of[member.member_id] = share_choices(member)
            debts_of[member.member_id] = debt_choices(member)
            periods_of[member.member_id] = unpaid_dues_choices(member)

        # Add debt types of the sandik to d_form.debt_type
        d_form.debt_type.choices += debt_type_choices(sandik)

        # TODO taksit sayısı borç tipine ve miktarına göre değiş
        # Add number of installment range to d_form.number_of_installment
        d_form.number_of_installment.choices += [(i, i) for i in range(1, 13)]

        if c_form.validate_on_submit():
            add_contribution(c_form)
            # TODO return işlemler sayfasına
            return redirect(url_for('home_page'))
        if d_form.validate_on_submit():
            add_debt(d_form)
            # TODO return işlemler sayfasına
            return redirect(url_for('home_page'))
        if p_form.validate_on_submit():
            if add_payment(p_form):
                # TODO return işlemler sayfasına
                return redirect(url_for('home_page'))
        if o_form.validate_on_submit():
            add_transaction(o_form)
            # TODO return işlemler sayfasına
            return redirect(url_for('home_page'))

        forms = [c_form, d_form, p_form, o_form]
        errors = []
        for form in forms:
            for field in form:
                errors += field.errors

        select_form = CustomTransactionSelectForm()
        select_form.member.choices += member_choices(sandik)
        forms.insert(0, select_form)
        return render_template("transaction/custom_transaction_form.html", forms=forms, errors=errors,
                               title="Add Contribution", periods_of=json.dumps(periods_of),
                               shares_of=json.dumps(shares_of), debts_of=json.dumps(debts_of))