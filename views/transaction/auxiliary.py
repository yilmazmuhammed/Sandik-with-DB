from datetime import date

from pony.orm import select, db_session

from database.auxiliary import Contribution, Share, DebtType

from database.dbinit import Member, Sandik, WebUser


# Return the dictionary that key is share.id and value is list of unpaid_dueses
def unpaid_dues(member, only_active_shares=True, is_there_old=False):
    ret_list = {}
    for share in member.shares_index.filter(lambda s: s.is_active == only_active_shares):
        if is_there_old:
            share_list = Period.all_months_from_date(member.sandik_ref.date_of_opening)
        else:
            share_list = Period.all_months_from_date(share.date_of_opening)
        for period in select(c.contribution_period for c in Contribution if c.transaction_ref.share_ref == share):
            if period in share_list:
                share_list.remove(period)
        ret_list[share.id] = share_list
    return ret_list


def unpaid_dues_choices(member: Member, only_active_shares=True, is_there_old=False):
    # TODO dil seçimine göre ay listesi
    month_names = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim',
                   'Kasım', 'Aralık']

    ret_list = {}
    for share in member.shares_index.filter(lambda s: s.is_active == only_active_shares).sort_by(Share.id):
        if is_there_old:
            share_list = Period.all_months_from_date(member.sandik_ref.date_of_opening)
        else:
            share_list = Period.all_months_from_date(share.date_of_opening)

        for period in select(c.contribution_period for c in Contribution if c.transaction_ref.share_ref == share):
            if period in share_list:
                share_list.remove(period)

        ret_list[share.id] = [(l, '%s %s' % (month_names[int(l[5:])], l[:4]),) for l in share_list]
    return ret_list


def share_choices(member, only_active_shares=True):
    return [(share.id, "Share %s" % (share.share_order_of_member,))
            for share in member.shares_index.filter(lambda share: share.is_active == only_active_shares).sort_by(
            Share.share_order_of_member)]


def debt_type_choices(sandik):
    return [(debt_type.id, debt_type.name) for debt_type in sandik.debt_types_index.sort_by(DebtType.name)]


@db_session
def member_choices(sandik_id, only_active_member=True):
    sandik = Sandik[sandik_id]
    return [(member.id, "%s %s" % (member.webuser_ref.name, member.webuser_ref.surname))
            for member in sandik.members_index.filter(lambda member: member.is_active >= only_active_member).sort_by(
            lambda m: m.webuser_ref.name + " " + m.webuser_ref.surname)]


def debt_choices(member):
    debts = select(transaction.debt_ref for transaction in
                   select(share.transactions_index for share in Share if share.member_ref == member)
                   if transaction.debt_ref)[:]
    ret = [(debt.id, "%s: H-%s -> %stl - %s/%s" % (
        debt.transaction_ref.transaction_date, debt.transaction_ref.share_ref.share_order_of_member,
        debt.installment_amount, debt.paid_installment, debt.number_of_installment)) for debt in debts if debt.remaining_debt > 0]
    return ret if len(ret) > 0 else [("", "Ödenmemiş borcunuz bulunmamaktadır...")]


class Period:
    # İlk tarihten (first) belli sayıda (times) ay sonra hangi ay oluyor
    @staticmethod
    def last_period(first: date, times: int) -> str:
        first_month = first.month
        first_year = first.year
        month = (first_month + times) % 12
        year = first_year + int((first_month + times) / 12)
        return "%s-%s" % (year, month)

    @staticmethod
    def last_period_2(period: str, times: int) -> str:
        first_month = int(period[5:])
        first_year = int(period[:4])
        month = (first_month + times) % 12
        year = first_year + int((first_month + times) / 12)
        return "%s-%s" % (year, month)

    @staticmethod
    def months_between_two_date(first: date, second: date) -> list:
        if first > second:
            first, second = second, first

        month = first.month
        year = first.year

        month_list = []
        while date(year, month, 1) <= second:
            month_list.append("%s-%s" % (year, month,))
            if month < 12:
                month += 1
            else:
                year += 1
                month = 1
        return month_list

    @staticmethod
    def months_between_two_period(first_period: str, second_period: str) -> list:
        if first_period > second_period:
            first_period, second_period = second_period, first_period

        month = int(first_period[5:])
        year = int(first_period[:4])

        month_list = []
        while "%s-%s" % (year, month) <= second_period:
            month_list.append("%s-%s" % (year, month,))
            if month < 12:
                month += 1
            else:
                year += 1
                month = 1
        return month_list

    @staticmethod
    def all_months_of_sandik(sandik: Sandik) -> list:
        months = Period.months_between_two_date(sandik.date_of_opening, date.today())
        return months

    @staticmethod
    def all_months_from_date(in_date: date) -> list:
        months = Period.months_between_two_date(in_date, date.today())
        return months

    @staticmethod
    def period_of_this_month(after: int = 0) -> str:
        return Period.last_period(date.today(), after)

    @staticmethod
    def period_of_the_month(indate: date, after: int = 0) -> str:
        return Period.last_period(indate, after)

    # TODO isimlendirme
    @staticmethod
    def months_by_number_of_months(first: date = date.today(), number_of_months: int = 0) -> list:
        last = Period.date_after_months(first, number_of_months)
        return Period.months_between_two_date(first, last)

    # TODO isimlendirme
    @staticmethod
    def date_after_months(first: date = date.today(), number_of_months: int = 0) -> date:
        day = first.day
        month = (first.month + number_of_months - 1) % 12
        year = first.year + int((first.month + number_of_months - 1) / 12)
        return date(year, month, day)

    @staticmethod
    def period_name(period: str):
        months = {'1': 'Ocak', '2': 'Şubat', '3': 'Mart', '4': 'Nisan', '5': 'Mayıs', '6': 'Haziran', '7': 'Temmuz',
                  '8': 'Ağustos', '9': 'Eylül', '10': 'Ekim', '11': 'Kasım', '12': 'Aralık'}
        return "%s %s" % (months[period[5:]], period[:4])

    @staticmethod
    def compare(after, before):
        a_year = int(after[:4])
        a_month = int(after[5:])
        b_year = int(before[:4])
        b_month = int(before[5:])
        if a_year > b_year:
            return True
        elif a_year < b_year:
            return False
        elif a_month >= b_month:
            return True
        else:
            return False


def name_surname(share: Share=None, member: Member=None, webuser: WebUser=None):
    if share:
        member = share.member_ref
    if member:
       webuser = member.webuser_ref
    if webuser:
        return webuser.name +  " " + webuser.surname
