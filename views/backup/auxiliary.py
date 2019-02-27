from datetime import date

from pony.orm import select, db_session

from database.auxiliary import insert_debt, insert_payment, insert_contribution, insert_transaction, insert_member, \
    insert_share, insert_webuser
from database.dbinit import Member, DebtType


class LineTransaction:
    """docstring for Transaction"""

    def __init__(self, t_id, t_date, amount, share_name, t_type, explanation, additional_info):
        s_date = t_date.split('.')
        day = int(s_date[0])
        month = int(s_date[1])
        year = int(s_date[2])
        self.id = int(t_id)
        self.date = date(year, month, day)
        self.amount = int(amount)
        self.share_name = share_name
        self.inner_type = t_type
        self.explanation = explanation
        self.additional_info = additional_info

        if self.inner_type == 'APB' or self.inner_type == 'PDAY':
            self.type = 'Debt'
            self.amount = abs(self.amount)
            self.number_of_installment = int(additional_info)
        elif self.inner_type == 'APB-Ö' or self.inner_type == 'PDAY-Ö':
            self.type = 'Payment'
            self.transaction_id = int(additional_info)
        elif self.inner_type == 'Aidat':
            self.type = 'Contribution'
            self.period = additional_info
        elif self.inner_type == 'Diğer':
            self.type = 'Other'

    def print(self):
        print(self.id, "\t", self.date, "\t", self.amount, "\t",
              self.share_name, "\t", self.type, "\t",
              self.explanation, "\t", self.additional_info)


class LineWebUser:
    def __init__(self, username, password_hash, name, surname, str_date, is_admin, is_active):
        s_date = str_date.split('.')
        day = int(s_date[0])
        month = int(s_date[1])
        year = int(s_date[2])

        self.username = username
        self.password_hash = password_hash
        self.name = name
        self.surname = surname
        self.date_of_registration = date(year, month, day)
        self.is_admin = False if is_admin == 'False' else True
        self.is_active = False if is_active == 'False' else True


class LineMember:
    def __init__(self, id, webuser_username, sandik_id, str_date, is_active, member_authority_type_id,):
        s_date = str_date.split('.')
        day = int(s_date[0])
        month = int(s_date[1])
        year = int(s_date[2])

        self.id = id
        self.webuser_username = webuser_username
        self.sandik_id = sandik_id
        self.date_of_registration = date(year, month, day)
        self.is_active = False if is_active == 'False' else True
        self.member_authority_type_id = member_authority_type_id


class LineShare:
    def __init__(self, id, member_id, share_order_of_member, str_date, is_active):
        s_date = str_date.split('.')
        day = int(s_date[0])
        month = int(s_date[1])
        year = int(s_date[2])

        self.id = id
        self.member_id = member_id
        self.share_order_of_member = share_order_of_member
        self.date_of_opening = date(year, month, day)
        self.is_active = False if is_active == 'False' else True


def add_transactions(trs):
    with db_session:
        share_ids = {}
        for member in select(member for member in Member):
            for share in member.shares_index:
                share_name = share.member_ref.webuser_ref.name + " " + \
                             share.member_ref.webuser_ref.surname + " " + \
                             str(share.share_order_of_member)
                share_ids[share_name] = share.id

        for t in trs:
            if t.type == 'Debt':
                insert_debt(t.date, t.amount, share_ids[t.share_name], DebtType.get(name=t.inner_type).id, t.explanation,
                            t.number_of_installment)
            elif t.type == 'Payment':
                insert_payment(t.date, t.amount, t.explanation, transaction_id=t.transaction_id)
            elif t.type == 'Contribution':
                insert_contribution(t.date, t.amount, share_ids[t.share_name], t.explanation, t.period.split(" "),
                                    is_from_import_data=True)
            elif t.type == 'Other':
                insert_transaction(t.date, t.amount, share_ids[t.share_name], t.explanation)


def add_webusers(webusers):
    with db_session:
        for wu in webusers:
            insert_webuser(username=wu.username, password_hash=wu.password_hash,
                           date_of_registration=wu.date_of_registration, name=wu.name, surname=wu.surname,
                           is_admin=wu.is_admin,  is_active=wu.is_active)


def add_members(members):
    with db_session:
        for m in members:
            insert_member(m.webuser_username, m.sandik_id, m.member_authority_type_id, m.date_of_registration,
                          m.is_active)


def add_shares(shares):
    with db_session:
        for s in shares:
            insert_share(s.member_id, s.date_of_opening, s.is_active, s.share_order_of_member)

