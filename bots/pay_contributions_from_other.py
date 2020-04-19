from datetime import date

from pony.orm import db_session

from bots.telegram_bot import sandik_bot, admin_chat_id
from database.auxiliary import insert_transaction, insert_contribution
from database.dbinit import Share, Member, Sandik
from views.transaction.auxiliary import Period, unpaid_contribution_periods


def pay_contribution_of_share(share_id=None, share=None):
    share = share if share else Share[share_id]
    other_amount = share.amount_other()
    contribution_amount = share.member_ref.sandik_ref.contribution_amount
    if other_amount >= contribution_amount and share.is_active \
            and Period.period_of_this_month() in unpaid_contribution_periods(share=share):
        insert_transaction(in_date=date.today(), amount=contribution_amount, share_id=share.id,
                           explanation="Otomatik aidat ödemesi (Diğer'den)", created_by_username='admin'
                           )
        insert_contribution(in_date=date.today(), amount=contribution_amount, share_id=share.id,
                            explanation="Otomatik aidat ödemesi için", created_by_username='admin',
                            new_periods=[Period.period_of_this_month()]
                            )
        telegram_message = "%s adına otomatik aidat ödeme yapıldı." % (share.name_surname_share())
        sandik_bot.sendMessage(admin_chat_id, telegram_message)
        print(share.name_surname_share(), other_amount)


def pay_contributions_of_member(member_id=None, member=None):
    member = member if member else Member[member_id]
    # TODO otomatik ödeme açık mı ve üüye aktif mi
    if member.is_active:
        for share in member.shares_index:
            if share.is_active:
                pay_contribution_of_share(share=share)


@db_session
def pay_contributions_in_sandik(sandik_id=None, sandik=None):
    sandik = sandik if sandik else Sandik[sandik_id]
    for member in sandik.members_index:
        if member.is_active:
            pay_contributions_of_member(member=member)


@db_session
def pay_all_contributions_in_website():
    for sandik in Sandik.select():
        pay_contributions_in_sandik(sandik=sandik)


if __name__ == "__main__":
    if date.today().day == 1:
        pay_all_contributions_in_website()