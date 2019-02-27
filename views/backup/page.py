from flask import render_template, redirect, url_for, flash
from pony.orm import db_session, select

from database.dbinit import Transaction, Member, WebUser, Share
from forms import ImportDataForm, FormPageInfo
from views.authorizations import admin_required
from views.backup.auxiliary import LineTransaction, LineWebUser, LineShare, LineMember, add_transactions, add_members, \
    add_shares, add_webusers
from views.others.auxiliary import read_data_online


@admin_required
def export_transactions_as_csv_page():
    with db_session:

        transactions = select(transaction for transaction in Transaction).sort_by(lambda tr: tr.id)[:]

        html = ""
        for t in transactions:
            html += "%s;%s.%s.%s;%s;%s %s %s;" % (t.id, t.transaction_date.day, t.transaction_date.month,
                                                  t.transaction_date.year, t.amount,
                                                  t.share_ref.member_ref.webuser_ref.name,
                                                  t.share_ref.member_ref.webuser_ref.surname,
                                                  t.share_ref.share_order_of_member,)

            if t.debt_ref:
                html += "%s;" % (t.debt_ref.debt_type_ref.name,)
            elif t.payment_ref:
                html += "%s-Ö;" % (t.payment_ref.debt_ref.debt_type_ref.name,)
            elif t.contribution_index:
                html += "Aidat;"
            else:
                # html += "%s;" % (t.type.capitalize(),)
                html += "Diğer;"

            html += "%s;" % (t.explanation,)

            if t.debt_ref:
                html += "%s" % t.debt_ref.number_of_installment
            elif t.payment_ref:
                html += "%s" % t.payment_ref.debt_ref.transaction_ref.id
            elif t.contribution_index:
                for c in t.contribution_index.sort_by(lambda co: co.contribution_period):
                    html += "%s " % c.contribution_period
                html = html[:-1]

            html += '<br>'
        return html


@admin_required
def export_webusers_as_csv_page():
    with db_session:
        webusers = select(webuser for webuser in WebUser).sort_by(WebUser.username)[:]

        html = ""
        for wu in webusers:
            if wu.username == 'admin':
                continue
            html += "%s;%s;%s;%s;%s.%s.%s;%s;%s<br>" % (wu.username, wu.password_hash, wu.name, wu.surname,
                                                        wu.date_of_registration.day, wu.date_of_registration.month,
                                                        wu.date_of_registration.year, wu.is_admin, wu.is_active)
        return html


@admin_required
def export_members_as_csv_page():
    with db_session:
        members = select(member for member in Member).sort_by(Member.id)[:]

        html = ""
        for m in members:
            html += "%s;%s;%s;%s.%s.%s;%s;%s<br>" % (m.id, m.webuser_ref.username, m.sandik_ref.id,
                                                     m.date_of_membership.day, m.date_of_membership.month,
                                                     m.date_of_membership.year, m.is_active,
                                                     m.member_authority_type_ref.id)
        return html


@admin_required
def export_shares_as_csv_page():
    with db_session:
        shares = select(share for share in Share).sort_by(Share.id)[:]

        html = ""
        for s in shares:
            html += "%s;%s;%s;%s.%s.%s;%s<br>" % (s.id, s.member_ref.id, s.share_order_of_member,
                                                  s.date_of_opening.day, s.date_of_opening.month,
                                                  s.date_of_opening.year, s.is_active)
        return html


@admin_required
def import_transactions_from_csv_page():
    form = ImportDataForm()

    if form.validate_on_submit():
        if form.webusers_url.data:
            webusers = read_data_online(form.webusers_url.data, LineWebUser)
            add_webusers(webusers)
        if form.members_url.data:
            members = read_data_online(form.members_url.data, LineMember)
            add_members(members)
        if form.shares_url.data:
            shares = read_data_online(form.shares_url.data, LineShare)
            add_shares(shares)
        if form.transactions_url.data:
            transactions = read_data_online(form.transactions_url.data, LineTransaction)
            add_transactions(transactions)

        flash(u'İşlemleri içe aktarma başarılı', 'success')
        return redirect(url_for('home_page'))

    info = FormPageInfo(form=form, title="Import transactions from url")
    return render_template("transaction/contribution_form.html", info=info)
