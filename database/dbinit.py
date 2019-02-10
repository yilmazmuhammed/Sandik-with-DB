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


# TODO get url from old dbinit.py
# PostgreSQL
# db.bind(provider='postgres', user='sandikadmin', password='sandikadminpw', host='localhost', database='sandikdb', port='5432')
db.bind(provider='postgres', user='auykhzkqcbtuek', password='dea61b13d38a6b893a353b30e865fedacc805572c9d035975a248f0ef09fbd93', host='ec2-54-247-125-116.eu-west-1.compute.amazonaws.com', database='dfuubeej01nmtv', port='5432')

# set_sql_debug(True)

db.generate_mapping(create_tables=True)

# TODO Bir sandıktan aynı webuser'ın sadece 1 tane üyeliği olabilir
if __name__ == "__main__":
    from passlib.hash import pbkdf2_sha256 as hasher

    with db_session:
        WebUser(username='admin', password_hash=hasher.hash('admin'), name='adminName', surname='adminSurname', is_admin=True)
        WebUser(username='tty', password_hash=hasher.hash('tty'), name='ttyName', surname='ttySurname')

        sandik = Sandik(name='Yardımlaşma Sandığı', date_of_opening=date(2018, 7, 1))
        admin = MemberAuthorityType(name='Sandık Başkanı', sandik_ref=sandik, is_admin=True)
        member = MemberAuthorityType(name='Üye', sandik_ref=sandik)
        DebtType(sandik_ref=sandik, name="type1")
        DebtType(sandik_ref=sandik, name="type322")
        DebtType(sandik_ref=sandik, name="type33")

        myilmazWU = WebUser(username='myilmaz', password_hash=hasher.hash('myilmaz'), name='Muhammed', surname='YILMAZ')
        myilmazM = Member(webuser_ref=myilmazWU, sandik_ref=sandik, date_of_membership=date.today(), member_authority_type_ref=admin)
        myilmazS1 = Share(member_ref=myilmazM, share_order_of_member=1, date_of_opening=date.today())
        myilmazS2 = Share(member_ref=myilmazM, share_order_of_member=2, date_of_opening=date.today())
        Contribution(transaction_ref=Transaction(share_ref=myilmazS1, transaction_date=date.today(), amount=5, type='cont'), contribution_period='2018-9')
        Contribution(transaction_ref=Transaction(share_ref=myilmazS1, transaction_date=date.today(), amount=5, type='cont'), contribution_period='2018-11')

        user1WU = WebUser(username='user1', password_hash=hasher.hash('user1'), name='Abbas', surname='YILDIRIM')
        user1M = Member(webuser_ref=user1WU, sandik_ref=sandik, date_of_membership=date.today(), member_authority_type_ref=member)
        user1S1 = Share(member_ref=user1M, share_order_of_member=1, date_of_opening=date.today())
        user1S2 = Share(member_ref=user1M, share_order_of_member=2, date_of_opening=date.today())

        user2WU = WebUser(username='user2', password_hash=hasher.hash('user2'), name='Abdullah', surname='YÜKSEK')
        user2M = Member(webuser_ref=user2WU, sandik_ref=sandik, date_of_membership=date.today(), member_authority_type_ref=member)
        Share(member_ref=user2M, share_order_of_member=1, date_of_opening=date.today())
        Share(member_ref=user2M, share_order_of_member=2, date_of_opening=date.today())
        Share(member_ref=user2M, share_order_of_member=3, date_of_opening=date.today())
        Share(member_ref=user2M, share_order_of_member=4, date_of_opening=date.today())

        user3WU = WebUser(username='user3', password_hash=hasher.hash('user3'), name='Ahmet Kutsay', surname='DERE')
        user3M = Member(webuser_ref=user3WU, sandik_ref=sandik, date_of_membership=date.today(), member_authority_type_ref=member)
        Share(member_ref=user3M, share_order_of_member=1, date_of_opening=date.today())

        user4WU = WebUser(username='user4', password_hash=hasher.hash('user4'), name='Feyzi', surname='GÜNEŞ')
        user4M = Member(webuser_ref=user4WU, sandik_ref=sandik, date_of_membership=date.today(), member_authority_type_ref=member)
        Share(member_ref=user4M, share_order_of_member=1, date_of_opening=date.today())

        user = Member[4]
        print(user.webuser_ref.name)
        print(select(s.share_order_of_member for s in Share if s.member_ref == user)[:])
        print(max(s.share_order_of_member for s in Share if s.member_ref == user))
        print(sandik.date_of_opening)


class DbTypes:
    Sandik = Sandik
    WebUser = WebUser
    Member = Member
    Share = Share
    Transaction = Transaction
