from datetime import date
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
    id = PrimaryKey(int, auto=True)
    webuser_ref = Required(WebUser)
    sandik_ref = Required(Sandik)
    date_of_membership = Required(date, default=lambda: date.today())
    is_active = Required(bool, default=True)
    member_authority_type_ref = Required('MemberAuthorityType')
    shares_index = Set('Share')


class Share(db.Entity):
    id = PrimaryKey(int, auto=True)
    member_ref = Required(Member)
    share_order_of_member = Required(int, size=8)
    date_of_opening = Required(date, default=lambda: date.today())
    is_active = Required(bool, default=True)
    transactions_index = Set('Transaction')


class Transaction(db.Entity):
    id = PrimaryKey(int, auto=True)
    share_ref = Required(Share)
    transaction_date = Required(date)
    amount = Required(int)
    type = Required(str, 15)  # Bu işlem tipi diye kendi veri tipim olması gerekiyor. CONTRIBUTION, DEBT, PAYMENT, OTHER
    explanation = Optional(str, 300)
    is_confirm = Required(bool, default=False)
    contribution_index = Set('Contribution')
    payment_ref = Optional('Payment')
    debt_ref = Optional('Debt')


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
    max_number_of_installments = Optional(int, unsigned=True)
    max_amount = Optional(int, unsigned=True)
    min_installment_amount = Optional(int, unsigned=True)
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


# TODO yetkileri ayarla (üye ekle/çıkar, tüm işlemleri görüntüle, tüm işlemleri düzenle gibi...)
# TODO max_number_of_members'e göre sınır koy
class MemberAuthorityType(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    max_number_of_members = Required(int, default="-1")
    sandik_ref = Required(Sandik)
    members_index = Set(Member)
    is_admin = Required(bool, default=False)
    reading_transaction = Required(bool, default=False)
    writing_transaction = Required(bool, default=False)
    adding_member = Required(bool, default=False)
    throwing_member = Required(bool, default=False)


# PostgreSQL
db.bind(provider='postgres', user='sandikadmin', password='sandikadminpw', host='localhost', database='sandikdb',
        port='5432')
# db.bind(provider='postgres', user='auykhzkqcbtuek',
#         password='dea61b13d38a6b893a353b30e865fedacc805572c9d035975a248f0ef09fbd93',
#         host='ec2-54-247-125-116.eu-west-1.compute.amazonaws.com', database='dfuubeej01nmtv', port='5432')

# set_sql_debug(True)

db.generate_mapping(create_tables=True)


def create_sandik_and_users():
    sandik = Sandik(name='Yardımlaşma Sandığı', date_of_opening=date(2016, 5, 21))

    MemberAuthorityType(name='Sandık Başkanı', sandik_ref=sandik, is_admin=True)
    MemberAuthorityType(name='Sandık Başkan Yardımcısı', sandik_ref=sandik, reading_transaction=True)
    MemberAuthorityType(name='Üye', sandik_ref=sandik)

    DebtType(sandik_ref=sandik, name="APB")
    DebtType(sandik_ref=sandik, name="PDAY")

    return sandik


# TODO Bir sandıktan aynı webuser'ın sadece 1 tane üyeliği olabilir
if __name__ == "__main__":
    from passlib.hash import pbkdf2_sha256 as hasher

    with db_session:
        WebUser(username='admin',
                password_hash='$pbkdf2-sha256$29000$lpLy/t8bo3TuXat1rlVKiQ$iXwe.imUemN2QLCwG/q5qADvWforaCydKxRE3rRe10s',
                name='Muhammed', surname='YILMAZ',
                is_admin=True)
        create_sandik_and_users()


class DbTypes:
    Sandik = Sandik
    WebUser = WebUser
    Member = Member
    Share = Share
    Transaction = Transaction
