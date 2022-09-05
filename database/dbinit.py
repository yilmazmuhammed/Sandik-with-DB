import json
import os
from datetime import date, datetime, time
from json import JSONEncoder

from pony.orm import *

db = Database()


class Sandik(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, 40)
    date_of_opening = Required(date, default=lambda: date.today())
    is_active = Required(bool, default=True)
    explanation = Optional(str, 200)
    members_index = Set('Member')
    member_authority_types_index = Set('MemberAuthorityType')
    debt_types_index = Set('DebtType')
    contribution_amount = Required(int)

    def active_members(self):
        return select(member for member in self.members_index if member.is_active)


class WebUser(db.Entity):
    username = PrimaryKey(str, 20)
    password_hash = Required(str, 87)
    name = Optional(str, 40)
    surname = Optional(str, 40)
    date_of_registration = Required(date, default=lambda: date.today())
    is_admin = Required(bool, default=False)
    is_active = Required(bool, default=True)
    members_index = Set('Member')
    telegram_chat_id = Optional(int)
    created_transactions = Set('Transaction', reverse='created_by')
    confirmed_transactions = Set('Transaction', reverse='confirmed_by')
    deleted_transactions = Set('Transaction', reverse='deleted_by')

    def name_surname(self):
        return self.name + " " + self.surname


class Member(db.Entity):
    """Her sandıktaki üyelik
Örneğin bir kişinin(webuser) birden fazla sandıkta üyeliği(member) olabilir. """
    id = PrimaryKey(int, auto=True)
    webuser_ref: WebUser = Required(WebUser)
    sandik_ref: Sandik = Required(Sandik)
    date_of_membership = Required(date, default=lambda: date.today())
    is_active = Required(bool, default=True)
    member_authority_type_ref = Required('MemberAuthorityType')
    shares_index = Set('Share')
    do_pay_contributions_automatically = Required(bool, default=False)
    # PrimaryKey(webuser_ref, sandik_ref)   # TODO
    composite_key(webuser_ref, sandik_ref)

    def main_share(self):
        return select(share for share in self.shares_index.order_by(Share.share_order_of_member))[:][0]

    def name_surname(self):
        return self.webuser_ref.name_surname()


class Share(db.Entity):
    id = PrimaryKey(int, auto=True)
    member_ref = Required(Member)
    share_order_of_member = Required(int, size=8)
    date_of_opening = Required(date, default=lambda: date.today())
    is_active = Required(bool, default=True)
    transactions_index = Set('Transaction')

    def name_surname_share(self):
        return self.member_ref.webuser_ref.name_surname() + " - " + str(self.share_order_of_member)

    def amount_other(self):
        return select(transaction.amount for transaction in self.transactions_index
                      if transaction.is_other_transaction() and transaction.is_valid()).sum()


class Transaction(db.Entity):
    id = PrimaryKey(int, auto=True)
    share_ref = Required(Share)
    transaction_date = Required(date)
    amount = Required(int)
    type = Required(str, 15)  # Bu işlem tipi diye kendi veri tipim olması gerekiyor. CONTRIBUTION, DEBT, PAYMENT, OTHER
    explanation = Optional(str, 400)
    contribution_index = Set('Contribution')
    payment_ref = Optional('Payment')
    debt_ref = Optional('Debt')
    created_by = Required(WebUser, reverse='created_transactions')
    creation_time = Optional(datetime)
    confirmed_by = Optional(WebUser, reverse='confirmed_transactions')
    confirmion_time = Optional(datetime)
    deleted_by = Optional(WebUser, reverse='deleted_transactions')
    deletion_time = Optional(datetime)

    def is_valid(self):
        return self.confirmed_by and not self.deleted_by

    def is_other_transaction(self):
        return not self.contribution_index and not self.debt_ref and not self.payment_ref

    def of(self, webuser=None, sandik=None):
        """
        do not use in select
        """
        ret = True
        if webuser:
            ret = ret and self.share_ref.member_ref.webuser_ref.username == webuser.username
        if sandik:
            ret = ret and self.share_ref.member_ref.sandik_ref.id == sandik.id
        return ret

    def is_unconfirmed(self):
        return not self.confirmed_by and not self.deleted_by


class Contribution(db.Entity):
    id = PrimaryKey(int, auto=True)
    transaction_ref = Required(Transaction)
    contribution_period = Required(str, 10)


class Debt(db.Entity):
    id = PrimaryKey(int, auto=True)
    transaction_ref = Required(Transaction)
    debt_type_ref = Required('DebtType')
    number_of_installment = Required(int, size=8)
    installment_amount = Required(int)
    paid_debt = Required(int)
    paid_installment = Required(int, size=8)
    remaining_debt = Required(int)
    remaining_installment = Required(int, size=8)
    starting_period = Required(str, 10)
    due_period = Required(str, 10)
    payments_index = Set('Payment')


class DebtType(db.Entity):
    """Her borç tipi için ayrı kurallar olabilir, max taksit sayısı, max miktar gibi"""
    id = PrimaryKey(int, auto=True)
    sandik_ref = Required(Sandik)
    name = Required(str, 20)
    explanation = Optional(str, 200)
    max_number_of_installments = Optional(int, default=0, unsigned=True)
    max_amount = Optional(int, default=0, unsigned=True)
    min_installment_amount = Optional(int, default=0, unsigned=True)
    debts_index = Set(Debt)


class Payment(db.Entity):
    id = PrimaryKey(int, auto=True)
    debt_ref = Required(Debt)
    payment_number_of_debt = Required(int)
    paid_debt_so_far = Required(int)
    paid_installment_so_far = Required(int, size=8)
    remaining_debt_so_far = Required(int)
    remaining_installment_so_far = Required(int, size=8)
    transaction_ref = Required(Transaction)


# TODO yetkileri ayarla (tüm işlemleri düzenle gibi...)
# TODO max_number_of_members'e göre sınır koy
class MemberAuthorityType(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    max_number_of_members = Required(int, default=0)
    sandik_ref = Required(Sandik)
    is_admin = Required(bool, default=False)
    reading_transaction = Required(bool, default=False)
    writing_transaction = Required(bool, default=False)
    adding_member = Required(bool, default=False)
    throwing_member = Required(bool, default=False)
    members_index = Set(Member)


# PostgreSQL
url = os.getenv("DATABASE_URL")
if url:
    user = url.split('://')[1].split(':')[0]
    password = url.split('://')[1].split(':')[1].split('@')[0]
    host = url.split('://')[1].split(':')[1].split('@')[1]
    port = url.split('://')[1].split(':')[2].split('/')[0]
    database = url.split('://')[1].split(':')[2].split('/')[1]
    db.bind(provider='postgres', user=user, password=password, host=host, database=database, port=port)
else:
    db.bind(provider="postgres", dsn=os.getenv('HEROKU_DATABASE_URL'))
# set_sql_debug(True)

db.generate_mapping(create_tables=True)


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.strftime("%Y-%m-%d %H:%M:%S.%f")
            elif isinstance(obj, date):
                return obj.strftime("%Y-%m-%d")
            elif isinstance(obj, time):
                return obj.strftime("%H:%M")
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


if __name__ == "__main__":
    with db_session:
        sandik_id = 2
        sandik: Sandik = Sandik[sandik_id]
        print("Selected sandik:", sandik.to_dict())
        data = {
            "sandik": {"name": sandik.name,
                       "contribution_amount": sandik.contribution_amount,
                       "detail": sandik.explanation,
                       "date_of_opening": sandik.date_of_opening},
            "web_users": [{"username": member.webuser_ref.username,
                           "name": member.webuser_ref.name,
                           "surname": member.webuser_ref.surname} for member in sandik.members_index],
            "members": [{"id": member.id, "username": member.webuser_ref.username,
                         "date_of_membership": member.date_of_membership,
                         "contribution_amount": member.sandik_ref.contribution_amount,
                         "detail": ""} for member in sandik.members_index],
            "shares": [{"id": share.id, "member_id": share.member_ref.id,
                        "date_of_membership": share.date_of_opening} for share in
                       select(share for share in Share if share.member_ref.sandik_ref == sandik)],
            "contributions": [],
            "debts": [],
            "payments": [],
            "others": []
        }
        transaction = select(tr for tr in Transaction if tr.share_ref.member_ref.sandik_ref == sandik
                                                     and tr.is_valid()).order_by(lambda t: t.id)
        count = transaction.count()
        for i, tr in enumerate(transaction):
            print(f"{i}/{count}")
            tr_data = {
                "share_id": tr.share_ref.id,
                "amount": tr.amount,
                "created_by": tr.created_by.username if tr.created_by.username != "admin" else "myilmaz",
                "date": tr.transaction_date,
                "detail": tr.explanation,
            }
            if tr.debt_ref:
                tr_data["id"] = tr.debt_ref.id
                tr_data["number_of_installment"] = tr.debt_ref.number_of_installment
                data["debts"].append(tr_data)
            elif tr.contribution_index.count() > 0:
                for contribution in tr.contribution_index:
                    c_data = tr_data.copy()
                    c_data["amount"] = tr.amount / tr.contribution_index.count()
                    year = contribution.contribution_period.split("-")[0]
                    month = contribution.contribution_period.split("-")[1]
                    c_data["period"] = year + "-" + ("0" if len(month) == 1 else "") + month
                    if c_data["period"] == "0-00":
                        c_data["period"] = "9999-01"
                    data["contributions"].append(c_data)
            elif tr.payment_ref:
                tr_data["debt_id"] = tr.payment_ref.debt_ref.id
                data["payments"].append(tr_data)
            else:
                data["others"].append(tr_data)

        with open("data.json", "w") as file:
            json.dump(data, file, indent=4, cls=CustomJSONEncoder)


class DbTypes:
    Sandik = Sandik
    WebUser = WebUser
    Member = Member
    Share = Share
    Transaction = Transaction
