from datetime import date
from pony.orm import *


db = Database()


class Sandik(db.Entity):
    sandik_id = PrimaryKey(int, auto=True)
    name = Required(str, 40)
    date_of_opening = Required(date)
    is_active = Required(bool)
    explanation = Optional(str, 200)
    members_index = Set('Member')
    member_authority_type_index = Optional('MemberAuthorityType')
    debt_types_index = Set('DebtType')


class WebUser(db.Entity):
    username = PrimaryKey(str, 20)
    password_hash = Required(str, 87)
    name = Optional(str, 40)
    surname = Optional(str, 40)
    date_of_registration = Required(date)
    is_admin = Required(bool, default=False)
    is_active = Required(bool, default=True)
    members_index = Set('Member')


class Member(db.Entity):
    """Her sandıktaki üyelik
Örneğin bir kişinin(webuser) birden fazla sandıkta üyeliği(member) olabilir. """
    member_id = PrimaryKey(int, auto=True)
    webuser_ref = Required(WebUser)
    sandik_ref = Required(Sandik)
    date_of_membership = Required(date)
    is_active = Required(bool)
    member_authority_type_ref = Required('MemberAuthorityType')
    shares_index = Set('Share')


class Share(db.Entity):
    share_id = PrimaryKey(int, auto=True)
    member_ref = Required(Member)
    share_order_of_member = Required(int, size=8)
    date_of_opening = Required(date)
    is_active = Required(bool)
    transactions_index = Set('Transaction')


class Transaction(db.Entity):
    transaction_id = PrimaryKey(int, auto=True)
    share_ref = Required(Share)
    transaction_date = Required(date)
    amount = Required(int)
    type = Required(str, 15)  # Bu işlem tipi diye kendi veri tipim olması gerekiyor. CONTRIBUTION, DEBT, PAYMENT, OTHER
    explanation = Optional(str, 200)


class Contribution(Transaction):
    contribution_period = Required(int, size=8)


class Debt(Transaction):
    debt_type_ref = Required('DebtType')
    number_of_installment = Required(int, size=8)
    installment_amount = Required(int)
    paid_debt = Required(int)
    paid_installment = Required(int, size=8)
    remaining_debt = Required(int)
    remaining_installment = Required(int, size=8)
    starting_date = Required(date)
    due_date = Required(date)
    payments_index = Set('Payment')


class DebtType(db.Entity):
    """Her borç tipi için ayrı kurallar olabilir, max taksit sayısı, max miktar gibi"""
    debt_type_id = PrimaryKey(int, auto=True)
    sandik_ref = Required(Sandik)
    name = Required(str, 20)
    explanation = Optional(str, 200)
    max_number_of_installment = Optional(str)
    max_amount = Optional(str)
    max_installment_amount = Optional(str)
    debts_index = Set(Debt)


class Payment(Transaction):
    debt_ref = Required(Debt)
    payment_number_of_debt = Required(int)
    paid_debt_so_far = Required(int)
    paid_installment_so_far = Required(int, size=8)
    remaining_debt_so_far = Required(int)
    remaining_installment_so_far = Required(int, size=8)


class MemberAuthorityType(db.Entity):
    id = PrimaryKey(int, auto=True)
    sandik_ref = Required(Sandik)
    members_index = Set(Member)


# # PostgreSQL
# db.bind(provider='postgres', user='sandikadmin', password='sandikadminpw', host='localhost', database='sandikdb')


db.generate_mapping(create_tables=True)