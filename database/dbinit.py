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
    listem = [
        [
            ('myilmaz', hasher.hash('myilmaz'), 'Muhammed', 'YILMAZ', date(2016, 5, 21), True,),
            (date(2016, 5, 21), 'Sandık Başkanı', True,),
            [(1, date(2016, 5, 21), True,), (2, date(2016, 5, 21), True,)]
        ],
        [
            ('yildirim', hasher.hash('yildirim1'), 'Abbas', 'YILDIRIM', date(2016, 5, 21), True,),
            (date(2016, 5, 21), 'Üye', True,),
            [(1, date(2016, 5, 21), True,), (2, date(2018, 4, 3), True,)]
        ],
        [
            ('yuksek', hasher.hash('yuksek2'), 'Abdullah', 'YÜKSEK', date(2016, 5, 21), True,),
            (date(2016, 5, 21), 'Üye', True,),
            [(1, date(2016, 5, 21), True), (2, date(2017, 12, 23), False,),
             (3, date(2018, 1, 5), False,), (4, date(2018, 1, 5), False,)
             ]
        ],
        [
            ('dere', hasher.hash('dere3'), 'Ahmet Kutsay', 'DERE', date(2016, 5, 21), True,),
            (date(2016, 5, 21), 'Üye', True,),
            [(1, date(2016, 5, 21), True)]
        ],
        [
            ('gunes', hasher.hash('gunes4'), 'Feyzi', 'GÜNEŞ', date(2016, 5, 21), True,),
            (date(2016, 5, 21), 'Sandık Başkan Yardımcısı', True,),
            [(1, date(2016, 5, 21), True,)]
        ],
        [
            ('tekin', hasher.hash('tekin5'), 'Furkan Necati', 'TEKİN', date(2018, 12, 19), True,),
            (date(2018, 12, 19), 'Üye', True,),
            [(1, date(2018, 12, 19), True,)]
        ],
        [
            ('balci', hasher.hash('balci6'), 'Gökhan', 'BALCI', date(2016, 5, 21), False,),
            (date(2016, 5, 21), 'Üye', False,),
            [(1, date(2016, 5, 21), False,), (2, date(2016, 5, 21), False,)]
        ],
        [
            ('altiok', hasher.hash('altiok7'), 'Huzeyfe', 'ALTIOK', date(2016, 5, 21), True,),
            (date(2016, 5, 21), 'Üye', True,),
            [(1, date(2016, 5, 21), True,)]
        ],
        [
            ('tekinm', hasher.hash('tekinm8'), 'Mehmet Nazım', 'TEKİN', date(2019, 1, 1), True,),
            (date(2019, 1, 1), 'Üye', True,),
            [(1, date(2019, 1, 1), True,)]
        ],
        [
            ('erdem', hasher.hash('erdem9'), 'Muhammed Hamidullah', 'ERDEM', date(2017, 7, 27), True,),
            (date(2017, 7, 27), 'Üye', True,),
            [(1, date(2017, 7, 27), True,), (2, date(2018, 10, 24), True,)]
        ],
        [
            ('tekeli', hasher.hash('tekeli10'), 'Muhammed Refik', 'TEKELİ', date(2018, 8, 20), True,),
            (date(2018, 8, 20), 'Üye', True,),
            [(1, date(2018, 8, 20), True,), (2, date(2018, 8, 20), True,)]
        ],
        [
            ('leventler', hasher.hash('leventler11'), 'Muhammet Emin', 'LEVENTLER', date(2016, 5, 21), True,),
            (date(2016, 5, 21), 'Üye', True,),
            [(1, date(2016, 5, 21), True,)]
        ],
        [
            ('yilmazmusa', hasher.hash('yilmazmusa11'), 'Musa Alperen', 'YILMAZ', date(2017, 12, 14), True,),
            (date(2017, 12, 14), 'Üye', True,),
            [(1, date(2017, 12, 14), True,), (2, date(2018, 9, 13), True,)]
        ],
        [
            ('yanik', hasher.hash('yanik12'), 'Ömer', 'YANIK', date(2018, 10, 26), True,),
            (date(2018, 10, 26), 'Üye', True,),
            [(1, date(2018, 10, 26), True,), (2, date(2018, 10, 26), True,),
             (3, date(2018, 10, 26), True,), (4, date(2018, 10, 26), True,)
             ]
        ],
        [
            ('akcan', hasher.hash('akcan13'), 'Talha', 'AKCAN', date(2016, 5, 21), False,),
            (date(2016, 5, 21), 'Üye', False,),
            [(1, date(2016, 5, 21), False)]
        ],

        [
            ('isik', hasher.hash('isik14'), 'Yusuf', 'IŞIK', date(2017, 5, 12), True,),
            (date(2017, 5, 12), 'Üye', True,),
            [(1, date(2017, 5, 12), True)]
        ],
    ]

    sandik = Sandik(name='Yardımlaşma Sandığı', date_of_opening=date(2016, 5, 21))

    MemberAuthorityType(name='Sandık Başkanı', sandik_ref=sandik, is_admin=True)
    MemberAuthorityType(name='Sandık Başkan Yardımcısı', sandik_ref=sandik, reading_transaction=True)
    MemberAuthorityType(name='Üye', sandik_ref=sandik)

    DebtType(sandik_ref=sandik, name="APB")
    DebtType(sandik_ref=sandik, name="PDAY")

    for wu, m, shares in listem:
        username, password_hash, name, surname, date_of_registration, ia = wu
        webuser = WebUser(username=username, password_hash=password_hash, name=name, surname=surname,
                          date_of_registration=date_of_registration, is_active=ia)

        dof, mat, ia = m
        member = Member(webuser_ref=webuser, sandik_ref=sandik, date_of_membership=dof,
                        member_authority_type_ref=MemberAuthorityType.select(lambda p: p.name == mat)[:][0], is_active=ia)
                        # member_authority_type_ref=MemberAuthorityType.select(name=mat)[0], is_active=ia) # pony==0.7.7

        for soof, dor, ia in shares:
            Share(member_ref=member, share_order_of_member=soof, date_of_opening=dor, is_active=ia)

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
