import csv
import io
import ssl
import urllib.request
from datetime import date

from database.auxiliary import insert_debt, insert_payment, insert_contribution, insert_transaction
from database.dbinit import DebtType


class LineTransaction:
    """docstring for Transaction"""

    def __init__(self, t_id, t_date, amount, share_name, t_type, explanation, additional_info):
        s_date = t_date.split('.')
        day = int(s_date[0])
        month = int(s_date[1])
        year = int(s_date[2])
        self.id = int(t_id)
        self.date = date(year, month, day)
        self.amount = int(amount)
        self.share_name = share_name
        self.inner_type = t_type
        self.explanation = explanation
        self.additional_info = additional_info

        if self.inner_type == 'APB' or self.inner_type == 'PDAY':
            self.type = 'Debt'
            self.number_of_installment = int(additional_info)
        elif self.inner_type == 'APB-Ö' or self.inner_type == 'PDAY-Ö':
            self.type = 'Payment'
            self.transaction_id = int(additional_info)
        elif self.inner_type == 'Aidat':
            self.type = 'Contribution'
            self.period = additional_info
        elif self.inner_type == 'Diğer':
            self.type = 'Other'

    def print(self):
        print(self.id, "\t", self.date, "\t", self.amount, "\t",
              self.share_name, "\t", self.type, "\t",
              self.explanation, "\t", self.additional_info)


def read_data_online(url):
    context = ssl._create_unverified_context()
    web_page = urllib.request.urlopen(url, context=context)
    data_reader = csv.reader(io.TextIOWrapper(web_page), delimiter=';', quotechar='|')

    transactions = []
    for row in data_reader:
        transaction = LineTransaction(*row)
        transactions.append(transaction)

    return transactions


def add_transactions(trs, sandik):
    share_ids = {}
    for member in sandik.members_index:
        for share in member.shares_index:
            share_name = share.member_ref.webuser_ref.name + " " + \
                         share.member_ref.webuser_ref.surname + " " + \
                         str(share.share_order_of_member)
            share_ids[share_name] = share.share_id

    for t in trs:
        if t.type == 'Debt':
            insert_debt(t.date, -t.amount, share_ids[t.share_name], DebtType.get(name=t.inner_type).id, t.explanation,
                        t.number_of_installment)
        elif t.type == 'Payment':
            insert_payment(t.date, t.amount, t.explanation, transaction_id=t.transaction_id)
        elif t.type == 'Contribution':
            insert_contribution(t.date, t.amount, share_ids[t.share_name], t.explanation, t.period.split(" "))
        elif t.type == 'Other':
            insert_transaction(t.date, t.amount, share_ids[t.share_name], t.explanation)