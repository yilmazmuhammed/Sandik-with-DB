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
    reading_transaction = Required(bool, default=False)
    writing_transaction = Required(bool, default=False)
    adding_member = Required(bool, default=False)
    throwing_member = Required(bool, default=False)


# PostgreSQL
# db.bind(provider='postgres', user='sandikadmin', password='sandikadminpw', host='localhost', database='sandikdb',
#         port='5432')
db.bind(provider='postgres', user='auykhzkqcbtuek',
        password='dea61b13d38a6b893a353b30e865fedacc805572c9d035975a248f0ef09fbd93',
        host='ec2-54-247-125-116.eu-west-1.compute.amazonaws.com', database='dfuubeej01nmtv', port='5432')

# set_sql_debug(True)

db.generate_mapping(create_tables=True)


def create_sandik_and_users():
    sandik = Sandik(name='Yardımlaşma Sandığı', date_of_opening=date(2016, 5, 21))

    admin = MemberAuthorityType(name='Sandık Başkanı', sandik_ref=sandik, is_admin=True)
    member = MemberAuthorityType(name='Üye', sandik_ref=sandik)

    DebtType(sandik_ref=sandik, name="APB")
    DebtType(sandik_ref=sandik, name="PDAY")

    myilmaz = WebUser(username='myilmaz', password_hash=hasher.hash('myilmaz'), name='Muhammed', surname='YILMAZ',
                      date_of_registration=date(2016, 5, 21))
    myilmaz = Member(webuser_ref=myilmaz, sandik_ref=sandik, date_of_membership=date(2016, 5, 21),
                     member_authority_type_ref=admin)
    Share(member_ref=myilmaz, share_order_of_member=1, date_of_opening=date(2016, 5, 21))
    Share(member_ref=myilmaz, share_order_of_member=2, date_of_opening=date(2016, 5, 21))

    yildirim = WebUser(username='yildirim', password_hash=hasher.hash('yildirim1'), name='Abbas',
                       surname='YILDIRIM', date_of_registration=date(2016, 5, 21))
    yildirim_m = Member(webuser_ref=yildirim, sandik_ref=sandik, date_of_membership=date(2016, 5, 21),
                        member_authority_type_ref=member)
    Share(member_ref=yildirim_m, share_order_of_member=1, date_of_opening=date(2016, 5, 21))
    Share(member_ref=yildirim_m, share_order_of_member=2, date_of_opening=date(2018, 4, 3))

    yuksek = WebUser(username='yuksek', password_hash=hasher.hash('yuksek2'), name='Abdullah', surname='YÜKSEK',
                     date_of_registration=date(2016, 5, 21))
    yuksek_m = Member(webuser_ref=yuksek, sandik_ref=sandik, date_of_membership=date.today(),
                      member_authority_type_ref=member)
    Share(member_ref=yuksek_m, share_order_of_member=1, date_of_opening=date(2016, 5, 21))
    Share(member_ref=yuksek_m, share_order_of_member=2, date_of_opening=date(2017, 12, 23), is_active=False)
    Share(member_ref=yuksek_m, share_order_of_member=3, date_of_opening=date(2018, 1, 5), is_active=False)
    Share(member_ref=yuksek_m, share_order_of_member=4, date_of_opening=date(2018, 1, 5), is_active=False)

    dere = WebUser(username='dere', password_hash=hasher.hash('dere3'), name='Ahmet Kutsay', surname='DERE',
                   date_of_registration=date(2016, 5, 21))
    dere = Member(webuser_ref=dere, sandik_ref=sandik, date_of_membership=date(2016, 5, 21),
                  member_authority_type_ref=member)
    Share(member_ref=dere, share_order_of_member=1, date_of_opening=date(2016, 5, 21))

    gunes = WebUser(username='gunes', password_hash=hasher.hash('user4'), name='Feyzi', surname='GÜNEŞ',
                    date_of_registration=date(2016, 5, 21))
    gunes = Member(webuser_ref=gunes, sandik_ref=sandik, date_of_membership=date(2016, 5, 21),
                   member_authority_type_ref=member)
    Share(member_ref=gunes, share_order_of_member=1, date_of_opening=date(2016, 5, 21))

    tekin = WebUser(username='tekin', password_hash=hasher.hash('tekin5'), name='Furkan Necati', surname='TEKİN',
                    date_of_registration=date(2018, 12, 19))
    tekin = Member(webuser_ref=tekin, sandik_ref=sandik, date_of_membership=date(2018, 12, 19),
                   member_authority_type_ref=member)
    Share(member_ref=tekin, share_order_of_member=1, date_of_opening=date(2018, 12, 19))

    balci = WebUser(username='balci', password_hash=hasher.hash('balci6'), name='Gökhan', surname='BALCI',
                    date_of_registration=date(2016, 5, 21), is_active=False)
    balci = Member(webuser_ref=balci, sandik_ref=sandik, date_of_membership=date(2016, 5, 21),
                   member_authority_type_ref=member, is_active=False)
    Share(member_ref=balci, share_order_of_member=1, date_of_opening=date(2016, 5, 21), is_active=False)
    Share(member_ref=balci, share_order_of_member=2, date_of_opening=date(2016, 5, 21), is_active=False)

    altiok = WebUser(username='altiok', password_hash=hasher.hash('altiok7'), name='Huzeyfe', surname='ALTIOK',
                     date_of_registration=date(2016, 5, 21))
    altiok = Member(webuser_ref=altiok, sandik_ref=sandik, date_of_membership=date(2016, 5, 21),
                    member_authority_type_ref=member)
    Share(member_ref=altiok, share_order_of_member=1, date_of_opening=date(2016, 5, 21))

    tekinm = WebUser(username='tekinm', password_hash=hasher.hash('tekinm8'), name='Mehmet Nazım', surname='TEKİN',
                     date_of_registration=date(2016, 1, 1))
    tekinm = Member(webuser_ref=tekinm, sandik_ref=sandik, date_of_membership=date(2016, 1, 1),
                    member_authority_type_ref=member)
    Share(member_ref=tekinm, share_order_of_member=1, date_of_opening=date(2016, 1, 1))

    erdem = WebUser(username='erdem', password_hash=hasher.hash('erdem9'), name='Muhammed Hamidullah',
                    surname='ERDEM', date_of_registration=date(2017, 7, 27))
    erdem = Member(webuser_ref=erdem, sandik_ref=sandik, date_of_membership=date(2017, 7, 27),
                   member_authority_type_ref=member)
    Share(member_ref=erdem, share_order_of_member=1, date_of_opening=date(2017, 7, 27))
    Share(member_ref=erdem, share_order_of_member=2, date_of_opening=date(2018, 10, 24))

    tekeli = WebUser(username='tekeli', password_hash=hasher.hash('tekeli10'), name='Muhammed Refik',
                     surname='TEKELİ', date_of_registration=date(2018, 8, 20))
    tekeli = Member(webuser_ref=tekeli, sandik_ref=sandik, date_of_membership=date(2018, 8, 20),
                    member_authority_type_ref=member)
    Share(member_ref=tekeli, share_order_of_member=1, date_of_opening=date(2018, 8, 20))
    Share(member_ref=tekeli, share_order_of_member=2, date_of_opening=date(2018, 8, 20))

    leventler = WebUser(username='leventler', password_hash=hasher.hash('leventler11'), name='Muhammet Emin',
                        surname='LEVENTLER', date_of_registration=date(2016, 5, 21))
    leventler_m = Member(webuser_ref=leventler, sandik_ref=sandik, date_of_membership=date(2016, 5, 21),
                         member_authority_type_ref=member)
    Share(member_ref=leventler_m, share_order_of_member=1, date_of_opening=date(2016, 5, 21))

    yilmazmusa = WebUser(username='yilmazmusa', password_hash=hasher.hash('yilmazmusa11'), name='Musa Alperen',
                         surname='YILMAZ', date_of_registration=date(2017, 12, 14))
    yilmazmusa = Member(webuser_ref=yilmazmusa, sandik_ref=sandik, date_of_membership=date(2017, 12, 14),
                        member_authority_type_ref=member)
    Share(member_ref=yilmazmusa, share_order_of_member=1, date_of_opening=date(2017, 12, 14))
    Share(member_ref=yilmazmusa, share_order_of_member=2, date_of_opening=date(2018, 9, 13))

    yanik = WebUser(username='yanik', password_hash=hasher.hash('yanik12'), name='Ömer', surname='YANIK',
                    date_of_registration=date(2018, 10, 26))
    yanik = Member(webuser_ref=yanik, sandik_ref=sandik, date_of_membership=date(2018, 10, 26),
                   member_authority_type_ref=member)
    Share(member_ref=yanik, share_order_of_member=1, date_of_opening=date(2018, 10, 26))
    Share(member_ref=yanik, share_order_of_member=2, date_of_opening=date(2018, 10, 26))
    Share(member_ref=yanik, share_order_of_member=3, date_of_opening=date(2018, 10, 26))
    Share(member_ref=yanik, share_order_of_member=4, date_of_opening=date(2018, 10, 26))

    akcan = WebUser(username='akcan', password_hash=hasher.hash('akcan13'), name='Talha', surname='AKCAN',
                    date_of_registration=date(2016, 5, 21), is_active=False)
    akcan = Member(webuser_ref=akcan, sandik_ref=sandik, date_of_membership=date(2016, 5, 21),
                   member_authority_type_ref=member, is_active=False)
    Share(member_ref=akcan, share_order_of_member=1, date_of_opening=date(2016, 5, 21), is_active=False)

    isik = WebUser(username='isik', password_hash=hasher.hash('isik14'), name='Yusuf', surname='IŞIK',
                   date_of_registration=date(2017, 5, 12))
    isik = Member(webuser_ref=isik, sandik_ref=sandik, date_of_membership=date(2017, 5, 12),
                  member_authority_type_ref=member)
    Share(member_ref=isik, share_order_of_member=1, date_of_opening=date(2017, 5, 12))
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
