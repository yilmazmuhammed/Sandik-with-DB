from flask import abort, render_template, redirect, url_for
from flask_login import login_required, current_user
from pony.orm import db_session, select
from datetime import date
import json

from database.dbinit import Sandik, Transaction, Share, Contribution
from forms import ContributionForm, FormPageInfo


@login_required
def add_transaction_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]
        member = webuser_to_member(sandik, current_user.webuser)
        if not member:
            abort(404)


def add_contribution_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]
        member = webuser_to_member(sandik, current_user.webuser)

        # If member is not in members of the sandik
        if not member:
            abort(404)

        # Create contribution form
        form = ContributionForm()

        # Add shares of member to form.share
        # for share in member.shares_index.sort_by(Share.share_order_of_member):
        #     form.share.choices.append((share.share_id, "Share %s" % (share.share_order_of_member,),))
        form.share.choices += [(share.share_id, "Share %s" % (share.share_order_of_member,))
                               for share in member.shares_index.sort_by(Share.share_order_of_member)]

        if form.validate_on_submit():
            # TODO kontrolleri yap
            # Çoklu aidat ödemesi için ayrı bir ekleme yap
            Contribution(
                transaction_ref=Transaction(
                    share_ref=Share[form.share.data], transaction_date=form.transaction_date.data, amount=25,
                    type='contribution'),
                contribution_period=form.contribution_period.data)
            # TODO url_for ile işlemler sayfasına yönlendir
            return redirect(url_for('home_page'))
        info = FormPageInfo(form=form, title="Add Contribution")
        # TODO period listesinde ekranda görülen isim ve değer şu an aynı, ekranda 'mmmm yyyy' formatında göster
        return render_template("contribution_form.html", info=info, periodsDict=json.dumps(unpaid_dues(member)))


def webuser_to_member(sandik, webuser):
    print(sandik.members_index)
    for m in sandik.members_index:
        if m.webuser_ref.username == webuser.username:
            return m
    return None


# Return the dictionary that key is share_id and value is list of unpaid_dueses
def unpaid_dues(member):
    months = months_between_two_date(member.sandik_ref.date_of_opening, date.today())
    ret_list = {}
    for share in member.shares_index:
        share_list = months.copy()
        # for dues in select(t.contribution_index for t in Transaction if t.contribution_ref and t.share_ref == share):
        for period in select(c.contribution_period for c in Contribution if c.transaction_ref.share_ref == share):
            share_list.remove(period)
        ret_list[share.share_id] = share_list
    return ret_list


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
