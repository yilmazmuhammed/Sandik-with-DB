from flask import abort, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from pony.orm import db_session, select, count
from datetime import date
import json

from database.dbinit import Sandik, Transaction, Share, Contribution, Member, DebtType, Debt, Payment
from forms import ContributionForm, FormPageInfo, DebtForm, PaymentForm


@login_required
def add_transaction_page(sandik_id):
    with db_session:
        member = Member.get(sandik_ref=Sandik[sandik_id], webuser_ref=current_user.webuser)
        if not member:
            abort(404)


def add_contribution_page(sandik_id):
    with db_session:
        member = Member.get(sandik_ref=Sandik[sandik_id], webuser_ref=current_user.webuser)

        # If member is not in members of the sandik
        if not member:
            abort(404)

        # Create contribution form
        form = ContributionForm()

        # Add shares of member to form.share
        form.share.choices += share_choices(member)

        if form.validate_on_submit():
            # TODO kontrolleri yap
            # TODO Çoklu aidat ödemesi için ayrı bir ekleme yap
            # Add the transaction of contribution to database
            Contribution(
                transaction_ref=Transaction(
                    share_ref=Share[form.share.data], transaction_date=form.transaction_date.data, amount=25,
                    type='contribution'),
                contribution_period=form.contribution_period.data)
            # TODO url_for ile işlemler sayfasına yönlendir
            return redirect(url_for('home_page'))
        info = FormPageInfo(form=form, title="Add Contribution")
        # TODO period listesinde ekranda görülen isim ve değer şu an aynı, ekranda 'mmmm yyyy' formatında göster
        return render_template("transaction/contribution_form.html", info=info,
                               periodsDict=json.dumps(unpaid_dues(member)))


def add_debt_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]
        member = Member.get(sandik_ref=sandik, webuser_ref=current_user.webuser)

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
            # TODO kontrolleri yap, (borcu varsa bir daha alamaz[sayfaya giriş de engellenebilir], en fazla taksit, parasına göre en fazla borç)

            # Add the transaction of debt to database
            t_date = form.transaction_date.data
            t_amount = form.amount.data
            d_inst = form.number_of_installment.data
            Debt(
                transaction_ref=Transaction(
                    share_ref=Share[form.share.data], transaction_date=t_date, amount=t_amount, type='debt'),
                debt_type_ref=DebtType[form.debt_type.data], number_of_installment=d_inst,
                installment_amount=int(t_amount / d_inst),
                paid_debt=0, paid_installment=0, remaining_debt=t_amount, remaining_installment=d_inst,
                starting_period=Period.last_period(t_date, 1), due_period=Period.last_period(t_date, d_inst + 1))

            # TODO url_for ile işlemler sayfasına yönlendir
            return redirect(url_for('home_page'))

        info = FormPageInfo(form=form, title="Take Debt")
        return render_template('form.html', info=info)


def add_payment_page(sandik_id):
    with db_session:
        member = Member.get(sandik_ref=Sandik[sandik_id], webuser_ref=current_user.webuser)

        # If member is not in members of the sandik
        if not member:
            abort(404)

        # Create contribution form
        form = PaymentForm()

        # Add all debts of all shares of member to form.debt
        form.debt.choices = debt_choices(member)

        if form.validate_on_submit():
            # Get values
            amount = form.amount.data
            debt = Debt[form.debt.data]
            share = debt.transaction_ref.share_ref
            t_date = form.transaction_date.data
            expl = form.explanation.data

            # Final controls
            if amount > debt.remaining_debt:  # If new paid amount is bigger than remaining amount of the debt
                flash(u"Paid amount cannot be more than the remaining debt", 'danger')
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

                # TODO return işlemler sayfasına
                return redirect(url_for('home_page'))

        info = FormPageInfo(form=form, title="Add payment")
        return render_template('form.html', info=info)


# Return the dictionary that key is share_id and value is list of unpaid_dueses
def unpaid_dues(member):
    months = Period.months_between_two_date(member.sandik_ref.date_of_opening, date.today())
    ret_list = {}
    for share in member.shares_index:
        share_list = months.copy()
        # for dues in select(t.contribution_index for t in Transaction if t.contribution_ref and t.share_ref == share):
        for period in select(c.contribution_period for c in Contribution if c.transaction_ref.share_ref == share):
            share_list.remove(period)
        ret_list[share.share_id] = share_list
    return ret_list


def share_choices(member):
    return [(share.share_id, "Share %s" % (share.share_order_of_member,))
            for share in member.shares_index.sort_by(Share.share_order_of_member)]


def debt_type_choices(sandik):
    return [(debt_type.id, debt_type.name) for debt_type in sandik.debt_types_index.sort_by(DebtType.name)]


def debt_choices(member):
    debts = select(transaction.debt_ref for transaction in
                   select(share.transactions_index for share in Share if share.member_ref == member)
                   if transaction.debt_ref)[:]
    return [(debt.id, "Share %s - %s - %stl - kalan:%stl Görünen ad" % (
            debt.transaction_ref.share_ref.share_order_of_member, debt.transaction_ref.transaction_date,
            debt.transaction_ref.amount, debt.remaining_debt)) for debt in debts if debt.remaining_debt > 0]


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
