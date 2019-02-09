from flask import abort, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from pony.orm import db_session, select, count
from datetime import date
import json

from database.dbinit import Sandik, Transaction, Share, Contribution, Member, DebtType, Debt, Payment, WebUser
from forms import ContributionForm, FormPageInfo, DebtForm, PaymentForm, TransactionForm, CustomTransactionSelectForm


def add_transaction(form):
    # Add the transaction to database
    Transaction(share_ref=Share[form.share.data], transaction_date=form.transaction_date.data,
                amount=form.amount.data, type='other', explanation=form.explanation.data)


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

            # TODO url_for ile işlemler sayfasına yönlendir
            return redirect(url_for('home_page'))

        info = FormPageInfo(form=form, title="Add Transaction")
        return render_template("form.html", info=info)


def add_contribution(form: ContributionForm):
    # TODO kontrolleri yap
    # TODO Çoklu aidat ödemesi için ayrı bir ekleme yap
    # Add the transaction of contribution to database
    Contribution(
        transaction_ref=Transaction(
            share_ref=Share[form.share.data], transaction_date=form.transaction_date.data, amount=25,
            type='contribution', explanation=form.explanation.data),
        contribution_period=form.contribution_period.data)


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

            # TODO url_for ile işlemler sayfasına yönlendir
            return redirect(url_for('home_page'))
        info = FormPageInfo(form=form, title="Add Contribution")
        return render_template("transaction/contribution_form.html", info=info,
                               periodsDict=json.dumps(unpaid_dues_choices(member)))


def add_debt(form):
    # TODO kontrolleri yap, (borcu varsa bir daha alamaz[sayfaya giriş de engellenebilir], en fazla taksit, parasına göre en fazla borç)

    # Add the transaction of debt to database
    t_date = form.transaction_date.data
    t_amount = form.amount.data
    d_inst = form.number_of_installment.data
    ia = t_amount / d_inst
    ia = int(ia) if ia % 1 == 0 else int(ia)+1
    Debt(
        transaction_ref=Transaction(
            share_ref=Share[form.share.data], transaction_date=t_date, amount=t_amount, type='debt',
            explanation=form.explanation.data),
        debt_type_ref=DebtType[form.debt_type.data], number_of_installment=d_inst, installment_amount=ia,
        paid_debt=0, paid_installment=0, remaining_debt=t_amount, remaining_installment=d_inst,
        starting_period=Period.last_period(t_date, 1), due_period=Period.last_period(t_date, d_inst + 1))


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

            # TODO url_for ile işlemler sayfasına yönlendir
            return redirect(url_for('home_page'))

        info = FormPageInfo(form=form, title="Take Debt")
        return render_template('form.html', info=info)


def add_payment(form):
    # Get values
    amount = form.amount.data
    debt = Debt[form.debt.data]
    print(debt.installment_amount, debt.number_of_installment)
    share = debt.transaction_ref.share_ref
    t_date = form.transaction_date.data
    expl = form.explanation.data

    # Final controls
    if amount > debt.remaining_debt:  # If new paid amount is bigger than remaining amount of the debt
        flash(u"Paid amount cannot be more than the remaining debt", 'danger')
        return False
    else:  # There is no problem
        pnod = count(select(p for p in Payment if p.debt_ref == debt))
        pdsf = debt.paid_debt + amount
        pisf = int(pdsf / debt.installment_amount)
        rdsf = debt.remaining_debt - amount
        risf = debt.number_of_installment - pisf
        Payment(debt_ref=debt, payment_number_of_debt=pnod, paid_debt_so_far=pdsf, paid_installment_so_far=pisf,
                remaining_debt_so_far=rdsf, remaining_installment_so_far=risf,
                transaction_ref=Transaction(share_ref=share, transaction_date=t_date, amount=amount,
                                            type='payment', explanation=expl
                                            )
                )
        debt.paid_debt = pdsf
        debt.paid_installment = pisf
        debt.remaining_debt = rdsf
        debt.remaining_installment = risf
        return True


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


# Return the dictionary that key is share_id and value is list of unpaid_dueses
def unpaid_dues(member):
    months = Period.all_months_of_sandik(member.sandik_ref)
    ret_list = {}
    for share in member.shares_index:
        share_list = months.copy()
        # for dues in select(t.contribution_index for t in Transaction if t.contribution_ref and t.share_ref == share):
        for period in select(c.contribution_period for c in Contribution if c.transaction_ref.share_ref == share):
            share_list.remove(period)
        ret_list[share.share_id] = share_list
    return ret_list


def unpaid_dues_choices(member):
    # TODO dil seçimine göre ay listesi
    month_names = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
    all_months = Period.all_months_of_sandik(member.sandik_ref)
    ret_list = {}
    for share in member.shares_index:
        share_list = all_months.copy()
        # for dues in select(t.contribution_index for t in Transaction if t.contribution_ref and t.share_ref == share):
        for period in select(c.contribution_period for c in Contribution if c.transaction_ref.share_ref == share):
            share_list.remove(period)
        ret_list[share.share_id] = [(l, '%s %s' % (month_names[int(l[5:])], l[:4]),) for l in share_list]
    return ret_list


def share_choices(member):
    return [(share.share_id, "Share %s" % (share.share_order_of_member,))
            for share in member.shares_index.sort_by(Share.share_order_of_member)]


def debt_type_choices(sandik):
    return [(debt_type.id, debt_type.name) for debt_type in sandik.debt_types_index.sort_by(DebtType.name)]


def member_choices(sandik):
    return [(member.member_id, "%s %s" % (member.webuser_ref.name, member.webuser_ref.surname))
            for member in sandik.members_index.sort_by(Member.member_id)]


def debt_choices(member):
    debts = select(transaction.debt_ref for transaction in
                   select(share.transactions_index for share in Share if share.member_ref == member)
                   if transaction.debt_ref)[:]
    ret = [(debt.id, "Share %s - %s - %stl - kalan:%stl Görünen ad" % (
        debt.transaction_ref.share_ref.share_order_of_member, debt.transaction_ref.transaction_date,
        debt.transaction_ref.amount, debt.remaining_debt)) for debt in debts if debt.remaining_debt > 0]
    return ret if len(ret) > 0 else [("", "Ödenmemiş borcunuz bulunmamaktadır...")]


class Period:
    @staticmethod
    def last_period(first, times):
        month = first.month
        year = first.year

        for i in range(times):
            if month < 12:
                month += 1
            else:
                year += 1
                month = 1
        return "%s-%s" % (year, month)

    @staticmethod
    def months_between_two_date(first: date, second: date):
        if first > second:
            first, second = second, first

        month = first.month
        year = first.year

        month_list = []
        while date(year, month, 1) < second:
            month_list.append("%s-%s" % (year, month,))
            if month < 12:
                month += 1
            else:
                year += 1
                month = 1
        return month_list

    @staticmethod
    def all_months_of_sandik(sandik):
        months = Period.months_between_two_date(sandik.date_of_opening, date.today())
        return months


# # TODO kendi yetkilendirmem için
# def login_required(func):
#     '''
#     If you decorate a view with this, it will ensure that the current user is
#     logged in and authenticated before calling the actual view. (If they are
#     not, it calls the :attr:`LoginManager.unauthorized` callback.) For
#     example::
#
#         @app.route('/post')
#         @login_required
#         def post():
#             pass
#
#     If there are only certain times you need to require that your user is
#     logged in, you can do so with::
#
#         if not current_user.is_authenticated:
#             return current_app.login_manager.unauthorized()
#
#     ...which is essentially the code that this function adds to your views.
#
#     It can be convenient to globally turn off authentication when unit testing.
#     To enable this, if the application configuration variable `LOGIN_DISABLED`
#     is set to `True`, this decorator will be ignored.
#
#     .. Note ::
#
#         Per `W3 guidelines for CORS preflight requests
#         <http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0>`_,
#         HTTP ``OPTIONS`` requests are exempt from login checks.
#
#     :param func: The view function to decorate.
#     :type func: function
#     '''
#     @wraps(func)
#     def decorated_view(*args, **kwargs):
#         if request.method in EXEMPT_METHODS:
#             return func(*args, **kwargs)
#         elif current_app.login_manager._login_disabled:
#             return func(*args, **kwargs)
#         elif not current_user.is_authenticated:
#             return current_app.login_manager.unauthorized()
#         return func(*args, **kwargs)
#     return decorated_view
