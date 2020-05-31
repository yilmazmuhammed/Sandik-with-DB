from datetime import date, datetime

from pony.orm import db_session, commit, select

from bots.telegram_bot import telegram_bot
from database.auxiliary import insert_transaction
from database.dbinit import Share, Member, Sandik
from views.sandik.auxiliary import get_chat_ids_of_sandik_admins
from views.transaction.db import fast_pay
from views.webuser.auxiliary import get_chat_ids_of_site_admins


created_by_username = 'admin'


@db_session
def pay_automatic_instruction_of_share(share_id=None, share=None):
    share = share if share else Share[share_id]

    # TODO Exception
    if not share.is_active:
        return

    member = share.member_ref
    sandik = member.sandik_ref

    if member.do_pay_contributions_automatically or member.do_pay_contributions_automatically:
        telegram_bot.send_message_to_list(
            get_chat_ids_of_site_admins(),
            "*%s*\n%s %s" % (sandik.name, share.name_surname_share(),
                             "adına otomatik ödeme talimatı gerçekleştiriliyor."
                             )
        )

    other_amount = select(transaction.amount for transaction in member.main_share().transactions_index
                          if transaction.is_other_transaction() and not transaction.deleted_by
                          ).sum()
    paid_amount = fast_pay(amount=other_amount, created_by_username=created_by_username, creation_time=datetime.now(),
                           share=share, explanation="Otomatik ödeme talimatı",
                           pay_contributions=member.do_pay_contributions_automatically,
                           pay_installments=member.do_pay_contributions_automatically,
                           pay_other=False
                           )

    # TODO Önceki işlemlerin eklenip bu işlemin eklenememe durumuna dikkat et
    if paid_amount != 0:
        insert_transaction(in_date=date.today(), amount=-paid_amount, share_id=member.main_share().id,
                           explanation="Otomatik ödeme talimatı gerçekleşti. (Hisse %s)" % share.share_order_of_member,
                           created_by_username=created_by_username
                           )
        commit()
        telegram_bot.send_message_to_list(
            get_chat_ids_of_sandik_admins(sandik=sandik) + get_chat_ids_of_site_admins(),
            "*%s*\n%s %s" % (sandik.name, share.name_surname_share(), "adına otomatik ödeme talimatı gerçekleşti.")
        )
    else:
        telegram_bot.send_message_to_list(
            get_chat_ids_of_sandik_admins(sandik=sandik) + get_chat_ids_of_site_admins(),
            "*%s*\n%s %s" % (sandik.name, share.name_surname_share(), "adına herhangi bir ödeme gerçekleşmedi.")
        )


@db_session
def pay_automatic_instruction_of_member(member_id=None, member=None, **kwargs):
    member = member if member else Member[member_id]
    for share in member.shares_index.filter(lambda s: s.is_active):
        pay_automatic_instruction_of_share(share=share)


@db_session
def pay_automatic_instructions_in_sandik(sandik_id=None, sandik=None):
    sandik = sandik if sandik else Sandik[sandik_id]
    for member in sandik.members_index.filter(lambda m: m.is_active):
        pay_automatic_instruction_of_member(member=member)


@db_session
def pay_automatic_instructions_in_website():
    for sandik in Sandik.select():
        pay_automatic_instructions_in_sandik(sandik=sandik)


if __name__ == "__main__":
    if date.today().day in [1, 25]:
        pay_automatic_instructions_in_website()