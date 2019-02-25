from flask import flash
from pony.orm import select

from database.auxiliary import insert_contribution
from database.dbinit import Share, Contribution
from forms import ContributionForm


def add_contribution(form: ContributionForm):
    share = Share[form.share.data]
    periods = form.contribution_period.data

    for period in periods:
        if period in select(c.contribution_period for c in Contribution if c.transaction_ref.share_ref == share)[:]:
            flash(u"Daha önce ödenmiş aidat tekrar ödenemez.", 'danger')
            return False

    if insert_contribution(form.transaction_date.data, form.amount.data, share.share_id,
                           form.explanation.data, periods):
        return True

    return False
