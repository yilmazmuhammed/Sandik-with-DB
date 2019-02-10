from flask import redirect, url_for, render_template
from flask_login import login_required
from pony.orm import db_session

from database.dbinit import Sandik
from forms import ImportDataForm, FormPageInfo
from views.others.auxiliary import read_data_online, add_transactions


def home_page():
    return render_template("layout.html")


@login_required
def import_data(sandik_id):
    form = ImportDataForm()

    if form.validate_on_submit():
        url = form.url.data
        transactions = read_data_online(url)

        with db_session:
            sandik = Sandik[sandik_id]
            add_transactions(transactions, sandik)
        return redirect(url_for('transactions_in_sandik', sandik_id=sandik_id))

    info = FormPageInfo(form=form, title="Import transactions from url")
    return render_template("transaction/contribution_form.html", info=info)
