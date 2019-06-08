from flask import render_template, flash
from pony.orm import db_session, select

from database.dbinit import Transaction, Member, WebUser, Share, Sandik, MemberAuthorityType, DebtType
from forms import FormPageInfo, ImportAllDataForm
from views import LayoutPageInfo
from views.authorizations import admin_required
from views.backup.auxiliary import add_transactions, add_members, \
    add_shares, add_webusers, db_tables, add_sandiklar, add_member_authority_types, add_debt_types


@admin_required
def export_all_datas():
    html = ""
    with db_session:

        # webuser html
        webusers = select(webuser for webuser in WebUser).sort_by(WebUser.username)[:]
        html += "WEBUSERS;%s<br>" % len(webusers)
        html += "username;password_hash;name;surname;date_of_registration;is_admin;is_active<br>"
        for wu in webusers:
            html += "%s;%s;%s;%s;%s;%s;%s<br>" % (wu.username, wu.password_hash, wu.name, wu.surname,
                                                  wu.date_of_registration, wu.is_admin, wu.is_active)

        # html of sandiks
        sandiks = select(sandik for sandik in Sandik).sort_by(Sandik.id)[:]
        html += "SANDIKLAR;%s<br>" %len(sandiks)
        html += "id;name;date_of_opening;is_active;explanation<br>"
        for sandik in sandiks:
            html += "%s;%s;%s;%s;%s<br>" % (sandik.id, sandik.name, sandik.date_of_opening, sandik.is_active,
                                           sandik.explanation)

        # html of member_authority_types
        ma_types = select(ma_type for ma_type in MemberAuthorityType).sort_by(MemberAuthorityType.id)[:]
        html += "MEMBER_AUTHORITY_TYPES;%s<br>" % len(ma_types)
        html += "id;name;max_number_of_members;sandik_ref;is_admin;reading_transaction;writing_transaction;" \
                "adding_member;throwing_member<br>"
        for mat in ma_types:
            html += "%s;%s;%s;%s;%s;%s;%s;%s;%s<br>" % (mat.id, mat.name, mat.max_number_of_members,
                                                        mat.sandik_ref.id, mat.is_admin, mat.reading_transaction,
                                                        mat.writing_transaction, mat.adding_member, mat.throwing_member)

        # html of members
        members = select(member for member in Member).sort_by(Member.id)[:]
        html += "MEMBERS;%s<br>" % len(members)
        html += "id;webuser_ref;sandik_ref;date_of_membership;is_active;member_authority_type_ref<br>"
        for m in members:
            html += "%s;%s;%s;%s;%s;%s<br>" % (m.id, m.webuser_ref.username, m.sandik_ref.id, m.date_of_membership,
                                               m.is_active, m.member_authority_type_ref.id)

        # html of shares
        shares = select(share for share in Share).sort_by(Share.id)[:]
        html += "SHARES;%s<br>" % len(shares)
        html += "id;member_ref.id;share_order_of_member;date_of_opening;is_active<br>"
        for s in shares:
            html += "%s;%s;%s;%s;%s<br>" % (s.id, s.member_ref.id, s.share_order_of_member, s.date_of_opening,
                                            s.is_active)

        # html of debt_type
        debt_types = select(debt_type for debt_type in DebtType).sort_by(DebtType.id)[:]
        html += "DEBT_TYPES;%s<br>" % len(debt_types)
        html += "id;sandik_ref.id;name;explanation;max_number_of_installments;max_amount;min_installment_amount<br>"
        for dt in debt_types:
            html += "%s;%s;%s;%s;%s;%s;%s<br>" % (dt.id, dt.sandik_ref.id, dt.name, dt.explanation,
                                                  dt.max_number_of_installments, dt.max_amount,
                                                  dt.min_installment_amount)

        # html of transactions
        transactions = select(transaction for transaction in Transaction).sort_by(lambda tr: tr.id)[:]
        html += "TRANSACTIONS;%s<br>" % len(transactions)
        html += "id;transaction_date;amount;share_ref.id;transaction_type;explanation;additional_info<br>"

        for t in transactions:
            html += "%s;%s;%s;%s;" % (t.id, t.transaction_date, t.amount, t.share_ref.id)

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
def import_all_datas():
    form = ImportAllDataForm()

    if form.validate_on_submit():
        if form.data_file.data:
            file = form.data_file.data
            file_data = file.read().decode("utf-8")
            csv_table = [row.split(';') for row in file_data.split('\n')]
            tables = db_tables(csv_table)
            add_webusers(tables['WEBUSERS'])
            add_sandiklar(tables['SANDIKLAR'])
            add_member_authority_types(tables['MEMBER_AUTHORITY_TYPES'])
            add_members(tables['MEMBERS'])
            add_shares(tables['SHARES'])
            add_debt_types(tables['DEBT_TYPES'])
            add_transactions(tables['TRANSACTIONS'])
            flash(u'Geri yükleme başarılı', 'success')
    info = FormPageInfo(form=form, title="Import all data from url")
    return render_template("form.html", layout_page=LayoutPageInfo("Import all data from url"), info=info)
