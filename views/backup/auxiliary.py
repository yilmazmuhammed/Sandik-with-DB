from datetime import date

from pony.orm import db_session

from database.auxiliary import insert_debt, insert_payment, insert_contribution, insert_transaction, insert_member, \
    insert_share, insert_webuser, insert_sandik, insert_member_authority_type, insert_debt_type
from database.dbinit import DebtType, Share


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

    bool_col = {'WEBUSERS': [5, 6], 'SANDIKLAR': [3], 'MEMBER_AUTHORITY_TYPES': [4, 5, 6, 7, 8], 'MEMBERS': [4],
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
            insert_webuser(username=wu[0], password_hash=wu[1],
                           date_of_registration=date_of_registration, name=wu[2], surname=wu[3],
                           is_admin=wu[5], is_active=wu[6])


def add_sandiklar(sandiklar):
    with db_session:
        for s in sandiklar:
            date_of_opening = date(*(list(map(int, s[2].split('-')))))
            insert_sandik(name=s[1], explanation=s[4], date_of_opening=date_of_opening, is_active=s[3])


def add_member_authority_types(member_authority_types):
    with db_session:
        for mat in member_authority_types:
            insert_member_authority_type(name=mat[1], capacity=mat[2], sandik_id=mat[3], is_admin=mat[4],
                                         reading_transaction=mat[5], writing_transaction=mat[6],
                                         adding_member=mat[7], throwing_member=mat[8])


def add_members(members):
    with db_session:
        for m in members:
            date_of_membership = date(*(list(map(int, m[3].split('-')))))
            insert_member(m[1], m[2], m[5], date_of_membership, m[4])


def add_shares(shares):
    with db_session:
        for s in shares:
            date_of_opening = date(*(list(map(int, s[3].split('-')))))
            insert_share(s[1], date_of_opening, s[4], s[2])


def add_debt_types(debt_types):
    with db_session:
        for dt in debt_types:
            insert_debt_type(sandik_id=dt[1], name=dt[2], explanation=dt[3], max_number_of_instalments=dt[4],
                             max_amount=dt[5], min_installment_amount=dt[6])


def add_transactions(transactions):
    with db_session:
        for t in transactions:
            transaction_date = date(*(list(map(int, t[1].split('-')))))
            # TODO Burada Payment ve Debt yani türleri her sandığın kendi borç türlerine göre belirle
            debt = ['APB', 'PDAY']
            payment = ['APB-Ö', 'PDAY-Ö']
            if t[4] in debt:
                insert_debt(transaction_date, t[2], t[3], t[5],
                            DebtType.get(name=t[4], sandik_ref=Share[t[3]].member_ref.sandik_ref).id, t[6],
                            created_by_username=t[7], confirmed_by_username=t[8], deleted_by_username=t[9])
            elif t[4] in payment:
                insert_payment(transaction_date, t[2], t[5], created_by_username=t[7], confirmed_by_username=t[8],
                               deleted_by_username=t[9], transaction_id=t[6])
            elif t[4] == 'Aidat':
                insert_contribution(transaction_date, t[2], t[3], t[5], t[6].split(" "),
                                    created_by_username=t[7], confirmed_by_username=t[8], deleted_by_username=t[9],
                                    is_from_import_data=True)
            elif t[4] == 'Diğer':
                insert_transaction(transaction_date, t[2], t[3], t[5],
                                   created_by_username=t[7], confirmed_by_username=t[8], deleted_by_username=t[9])
