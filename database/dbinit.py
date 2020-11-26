import os
from datetime import date, datetime

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
    sandik_ref = Required(Sandik)
    date_of_membership = Required(date, default=lambda: date.today())
    is_active = Required(bool, default=True)
    member_authority_type_ref = Required('MemberAuthorityType')
    shares_index = Set('Share')
    do_pay_contributions_automatically = Required(bool, default=False)
    # PrimaryKey(webuser_ref, sandik_ref)   # TODO
    composite_key(webuser_ref, sandik_ref)

    def main_share(self):
        return select(share for share in self.shares_index.order_by(Share.share_order_of_member))[:][0]


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

if __name__ == "__main__":
    with db_session:
        WebUser(username='admin',
                password_hash='$pbkdf2-sha256$29000$lpLy/t8bo3TuXat1rlVKiQ$iXwe.imUemN2QLCwG/q5qADvWforaCydKxRE3rRe10s',
                name='Muhammed', surname='YILMAZ',
                is_admin=True)
    pass


class DbTypes:
    Sandik = Sandik
    WebUser = WebUser
    Member = Member
    Share = Share
    Transaction = Transaction
