from flask import render_template, flash

from bots.mail import send_mail_all_data
from forms import FormPageInfo, ImportAllDataForm
from views import LayoutPageInfo
from views.authorizations import admin_required
from views.backup.auxiliary import add_transactions, add_members, add_shares, add_webusers, db_tables, add_sandiklar, \
    add_member_authority_types, add_debt_types, csv_list_backup


@admin_required
def export_all_datas():
    html = "<br>".join(csv_list_backup.all_data_list()) + "<br>"
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
