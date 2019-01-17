from datetime import date
from pony.orm import *


db = Database()


class Sandik(db.Entity):
    sandik_id = PrimaryKey(int, auto=True)
    name = Required(str, 40)
    date_of_opening = Required(date, default=lambda: date.today())
    is_active = Required(bool, default=True)
    explanation = Optional(str, 200)
    members_index = Set('Member')
    member_authority_types_index = Set('MemberAuthorityType')
    debt_types_index = Set('DebtType')


class WebUser(db.Entity):
    username = PrimaryKey(str, 20)
    password_hash = Required(str, 87)
    name = Optional(str, 40)
    surname = Optional(str, 40)
    date_of_registration = Required(date, default=lambda: date.today())
    is_admin = Required(bool, default=False)
    is_active = Required(bool, default=True)
    members_index = Set('Member')


class Member(db.Entity):
    """Her sandıktaki üyelik
Örneğin bir kişinin(webuser) birden fazla sandıkta üyeliği(member) olabilir. """
    member_id = PrimaryKey(int, auto=True)
    webuser_ref = Required(WebUser)
    sandik_ref = Required(Sandik)
    date_of_membership = Required(date, default=lambda: date.today())
    is_active = Required(bool, default=True)
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
    max_number_of_installments = Optional(int, unsigned=True)
    max_amount = Optional(int, unsigned=True)
    min_installment_amount = Optional(int, unsigned=True)
    debts_index = Set(Debt)


class Payment(Transaction):
    debt_ref = Required(Debt)
    payment_number_of_debt = Required(int)
    paid_debt_so_far = Required(int)
    paid_installment_so_far = Required(int, size=8)
    remaining_debt_so_far = Required(int)
    remaining_installment_so_far = Required(int, size=8)


# TODO yetkileri ayarla (üye ekle/çıkar, tüm işlemleri görüntüle, tüm işlemleri düzenle gibi...)
class MemberAuthorityType(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    max_number_of_members = Required(int, default="-1")
    sandik_ref = Required(Sandik)
    members_index = Set(Member)
    is_admin = Required(bool, default=False)


# PostgreSQL
# db.bind(provider='postgres', user='sandikadmin', password='sandikadminpw', host='localhost', database='sandikdb', port='5432')
db.bind(provider='postgres', user='auykhzkqcbtuek', password='dea61b13d38a6b893a353b30e865fedacc805572c9d035975a248f0ef09fbd93', host='ec2-54-247-125-116.eu-west-1.compute.amazonaws.com', database='dfuubeej01nmtv', port='5432')


db.generate_mapping(create_tables=True)

if __name__ == "__main__":
    with db_session:
        WebUser(username='admin', password_hash='$pbkdf2-sha256$29000$PIdwDqH03hvjXAuhlLL2Pg$B1K8TX6Efq3GzvKlxDKIk4T7yJzIIzsuSegjZ6hAKLk', name='adminName', surname='adminSurname', is_admin=True)
        WebUser(username='tty', password_hash='$pbkdf2-sha256$29000$Umotxdhbq9UaI2TsnTMmZA$uVtN2jo0I/de/Kz9/seebkM0n0MG./KGBc1EPw5X.f0', name='userName', surname='userSurname')

