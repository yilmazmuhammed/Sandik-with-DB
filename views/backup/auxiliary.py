from datetime import date, datetime

from pony.orm import db_session, select

from database.auxiliary import insert_debt, insert_payment, insert_contribution, insert_transaction, insert_member, \
    insert_share, insert_webuser, insert_sandik, insert_member_authority_type, insert_debt_type, remove_transaction
from database.dbinit import DebtType, Share, WebUser, Sandik, MemberAuthorityType, Member, Transaction


def db_tables(csv_table):
    lines = len(csv_table)

    next_table_name_line = 0

    tables = {}
    while next_table_name_line < lines - 1:
        table_name_line = next_table_name_line
        table_start_line = table_name_line + 2
        next_table_name_line = table_start_line + int(csv_table[table_name_line][1])

        table_name = csv_table[table_name_line][0]
        tables[table_name] = csv_table[table_start_line:next_table_name_line]

    bool_col = {'WEBUSERS': [5, 6], 'SANDIKLAR': [3], 'MEMBER_AUTHORITY_TYPES': [4, 5, 6, 7, 8], 'MEMBERS': [4, 6],
                'SHARES': [4], 'DEBT_TYPES': [], 'TRANSACTIONS': []}

    for header in bool_col.keys():
        for i in range(len(tables[header])):
            for j in bool_col[header]:
                if tables[header][i][j] == 'False':
                    tables[header][i][j] = False

    return tables


def add_webusers(webusers):
    if webusers[0][0] == 'admin':
        webusers.remove(webusers[0])

    with db_session:
        for wu in webusers:
            date_of_registration = date(*(list(map(int, wu[4].split('-')))))
            insert_webuser(username=wu[0], password_hash=wu[1], name=wu[2], surname=wu[3],
                           date_of_registration=date_of_registration, is_admin=wu[5], is_active=wu[6],
                           telegram_chat_id=wu[7] if wu[7] != 'None' else None)


def add_sandiklar(sandiklar):
    with db_session:
        for s in sandiklar:
            date_of_opening = date(*(list(map(int, s[2].split('-')))))
            insert_sandik(id=s[0], name=s[1], contribution_amount=s[3], explanation=s[5],
                          date_of_opening=date_of_opening, is_active=s[4])


def add_member_authority_types(member_authority_types):
    with db_session:
        for mat in member_authority_types:
            insert_member_authority_type(id=mat[0], name=mat[1], max_number_of_members=mat[2], sandik_id=mat[3],
                                         is_admin=mat[4],
                                         reading_transaction=mat[5], writing_transaction=mat[6],
                                         adding_member=mat[7], throwing_member=mat[8])


def add_members(members):
    with db_session:
        for m in members:
            date_of_membership = date(*(list(map(int, m[3].split('-')))))
            insert_member(username=m[1], sandik_id=m[2], authority_id=m[5], do_pay_contributions_automatically=m[6],
                          date_of_membership=date_of_membership, is_active=m[4], id=m[0])


def add_shares(shares):
    with db_session:
        for s in shares:
            date_of_opening = date(*(list(map(int, s[3].split('-')))))
            insert_share(s[1], date_of_opening, s[4], s[2], id=s[0])


def add_debt_types(debt_types):
    with db_session:
        for dt in debt_types:
            insert_debt_type(id=dt[0], sandik_id=dt[1], name=dt[2], explanation=dt[3], max_number_of_instalments=dt[4],
                             max_amount=dt[5], min_installment_amount=dt[6])


def add_transactions(transactions):
    with db_session:
        for t in transactions:
            transaction_date = date(*(list(map(int, t[1].split('-')))))
            creation_time = datetime.strptime(t[10], "%Y-%m-%d %H:%M:%S")
            confirmion_time = datetime.strptime(t[11], "%Y-%m-%d %H:%M:%S") if t[11] else None
            deletion_time = datetime.strptime(t[12], "%Y-%m-%d %H:%M:%S") if t[12] else None
            # TODO Burada Payment ve Debt yani türleri her sandığın kendi borç türlerine göre belirle
            debt = ['APB', 'PDAY']
            payment = ['APB-Ö', 'PDAY-Ö']
            if t[4] in debt:
                insert_debt(transaction_date, t[2], t[3], t[5],
                            DebtType.get(name=t[4], sandik_ref=Share[t[3]].member_ref.sandik_ref).id, t[6],
                            created_by_username=t[7], confirmed_by_username=t[8], id=t[0],
                            creation_time=creation_time, confirmion_time=confirmion_time, deletion_time=deletion_time
                            )
            elif t[4] in payment:
                insert_payment(transaction_date, t[2], t[5], created_by_username=t[7], confirmed_by_username=t[8],
                               transaction_id=t[6], id=t[0],
                               creation_time=creation_time, confirmion_time=confirmion_time, deletion_time=deletion_time
                               )
            elif t[4] == 'Aidat':
                insert_contribution(transaction_date, t[2], t[3], t[5], t[6].split(" "),
                                    created_by_username=t[7], confirmed_by_username=t[8],
                                    is_from_import_data=True, id=t[0],
                                    creation_time=creation_time, confirmion_time=confirmion_time,
                                    deletion_time=deletion_time
                                    )
            elif t[4] == 'Diğer':
                insert_transaction(transaction_date, t[2], t[3], t[5],
                                   created_by_username=t[7], confirmed_by_username=t[8], id=t[0],
                                   creation_time=creation_time, confirmion_time=confirmion_time,
                                   deletion_time=deletion_time
                                   )
            if t[9]:
                remove_transaction(t[0], t[9])


class csv_list_backup:
    @staticmethod
    def all_data_list():
        liste = []
        liste += csv_list_backup.webusers()
        liste += csv_list_backup.sandiks()
        liste += csv_list_backup.member_authority_types()
        liste += csv_list_backup.members()
        liste += csv_list_backup.shares()
        liste += csv_list_backup.debt_types()
        liste += csv_list_backup.transactions()
        return liste

    @staticmethod
    @db_session
    def webusers():
        liste = []
        webusers = select(webuser for webuser in WebUser).sort_by(WebUser.username)[:]
        liste.append("WEBUSERS;%s" % len(webusers))
        liste.append("username;password_hash;name;surname;date_of_registration;is_admin;is_active;telegram_chat_id")
        for wu in webusers:
            liste.append("%s;%s;%s;%s;%s;%s;%s;%s" % (wu.username, wu.password_hash, wu.name, wu.surname,
                                                      wu.date_of_registration, wu.is_admin, wu.is_active,
                                                      wu.telegram_chat_id
                                                      )
                         )
        return liste

    @staticmethod
    @db_session
    def sandiks():
        liste = []
        sandiks = select(sandik for sandik in Sandik).sort_by(Sandik.id)[:]
        liste.append("SANDIKLAR;%s" % len(sandiks))
        liste.append("id;name;date_of_opening;contribution_amount;is_active;explanation")
        for sandik in sandiks:
            liste.append("%s;%s;%s;%s;%s;%s" % (sandik.id, sandik.name, sandik.date_of_opening,
                                                sandik.contribution_amount, sandik.is_active, sandik.explanation))
        return liste

    @staticmethod
    @db_session
    def member_authority_types():
        liste = []
        ma_types = select(ma_type for ma_type in MemberAuthorityType).sort_by(MemberAuthorityType.id)[:]
        liste.append("MEMBER_AUTHORITY_TYPES;%s" % len(ma_types))
        liste.append(
            "id;name;max_number_of_members;sandik_ref;is_admin;reading_transaction;writing_transaction;adding_member;"
            "throwing_member")
        for mat in ma_types:
            liste.append("%s;%s;%s;%s;%s;%s;%s;%s;%s" % (mat.id, mat.name, mat.max_number_of_members,
                                                         mat.sandik_ref.id, mat.is_admin, mat.reading_transaction,
                                                         mat.writing_transaction, mat.adding_member,
                                                         mat.throwing_member))
        return liste

    @staticmethod
    @db_session
    def members():
        liste = []
        members = select(member for member in Member).sort_by(Member.id)[:]
        liste.append("MEMBERS;%s" % len(members))
        liste.append("id;webuser_ref;sandik_ref;date_of_membership;is_active;member_authority_type_ref;"
                     "do_pay_contributions_automatically")
        for m in members:
            liste.append("%s;%s;%s;%s;%s;%s;%s" % (m.id, m.webuser_ref.username, m.sandik_ref.id, m.date_of_membership,
                                                   m.is_active, m.member_authority_type_ref.id,
                                                   m.do_pay_contributions_automatically))
        return liste

    @staticmethod
    @db_session
    def shares():
        liste = []
        shares = select(share for share in Share).sort_by(Share.id)[:]
        liste.append("SHARES;%s" % len(shares))
        liste.append("id;member_ref.id;share_order_of_member;date_of_opening;is_active")
        for s in shares:
            liste.append("%s;%s;%s;%s;%s" % (s.id, s.member_ref.id, s.share_order_of_member, s.date_of_opening,
                                             s.is_active))
        return liste

    @staticmethod
    @db_session
    def debt_types():
        liste = []
        debt_types = select(debt_type for debt_type in DebtType).sort_by(DebtType.id)[:]
        liste.append("DEBT_TYPES;%s" % len(debt_types))
        liste.append("id;sandik_ref.id;name;explanation;max_number_of_installments;max_amount;min_installment_amount")
        for dt in debt_types:
            liste.append("%s;%s;%s;%s;%s;%s;%s" % (dt.id, dt.sandik_ref.id, dt.name, dt.explanation,
                                                   dt.max_number_of_installments, dt.max_amount,
                                                   dt.min_installment_amount))
        return liste

    @staticmethod
    @db_session
    def transactions():
        liste = []
        transactions = select(transaction for transaction in Transaction).sort_by(lambda tr: tr.id)[:]
        liste.append("TRANSACTIONS;%s" % len(transactions))
        liste.append("id;transaction_date;amount;share_ref.id;transaction_type;explanation;additional_info;"
                     "created_by.username;confirmed_by.username;deleted_by.username;"
                     "creation_time;confirmion_time;deletion_time"
                     )
        for t in transactions:
            line = ""
            line += "%s;%s;%s;%s;" % (t.id, t.transaction_date, t.amount, t.share_ref.id)

            if t.debt_ref:
                line += "%s;" % (t.debt_ref.debt_type_ref.name,)
            elif t.payment_ref:
                line += "%s-Ö;" % (t.payment_ref.debt_ref.debt_type_ref.name,)
            elif t.contribution_index:
                line += "Aidat;"
            else:
                # html += "%s;" % (t.type.capitalize(),)
                line += "Diğer;"

            line += "%s;" % (t.explanation,)

            if t.debt_ref:
                line += "%s" % t.debt_ref.number_of_installment
            elif t.payment_ref:
                line += "%s" % t.payment_ref.debt_ref.transaction_ref.id
            elif t.contribution_index:
                for c in t.contribution_index.sort_by(lambda co: co.contribution_period):
                    line += "%s " % c.contribution_period
                line = line[:-1]

            line += ";"
            line += "%s;" % (t.created_by.username,)
            line += "%s;" % (t.confirmed_by.username if t.confirmed_by else "",)
            line += "%s;" % (t.deleted_by.username if t.deleted_by else "",)
            line += "%s;" % (t.creation_time.strftime("%Y-%m-%d %H:%M:%S") if t.creation_time else "",)
            line += "%s;" % (t.confirmion_time.strftime("%Y-%m-%d %H:%M:%S") if t.confirmion_time else "",)
            line += "%s" % (t.deletion_time.strftime("%Y-%m-%d %H:%M:%S") if t.deletion_time else "",)
            liste.append(line)
        return liste
