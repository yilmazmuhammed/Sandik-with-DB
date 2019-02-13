from datetime import date

from pony.orm import select

from database.auxiliary import Contribution, Share, DebtType


# Return the dictionary that key is share_id and value is list of unpaid_dueses
from database.dbinit import Member


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
        ret_list[share.share_id] = share_list
    return ret_list


def unpaid_dues_choices(member: Member, only_active_shares=True, is_there_old=False):
    # TODO dil seçimine göre ay listesi
    month_names = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim',
                   'Kasım', 'Aralık']

    ret_list = {}
    for share in member.shares_index.filter(lambda s: s.is_active == only_active_shares):
        if is_there_old:
            share_list = Period.all_months_from_date(member.sandik_ref.date_of_opening)
        else:
            share_list = Period.all_months_from_date(share.date_of_opening)

        for period in select(c.contribution_period for c in Contribution if c.transaction_ref.share_ref == share):
            if period in share_list:
                share_list.remove(period)

        ret_list[share.share_id] = [(l, '%s %s' % (month_names[int(l[5:])], l[:4]),) for l in share_list]
    return ret_list


def share_choices(member, only_active_shares=True):
    return [(share.share_id, "Share %s" % (share.share_order_of_member,))
            for share in member.shares_index.filter(lambda share: share.is_active == only_active_shares).sort_by(
            Share.share_order_of_member)]


def debt_type_choices(sandik):
    return [(debt_type.id, debt_type.name) for debt_type in sandik.debt_types_index.sort_by(DebtType.name)]


def member_choices(sandik, only_active_member=True):
    return [(member.member_id, "%s %s" % (member.webuser_ref.name, member.webuser_ref.surname))
            for member in sandik.members_index.filter(lambda member: member.is_active == only_active_member).sort_by(
            lambda m: m.webuser_ref.name)]


def debt_choices(member):
    debts = select(transaction.debt_ref for transaction in
                   select(share.transactions_index for share in Share if share.member_ref == member)
                   if transaction.debt_ref)[:]
    ret = [(debt.id, "Share %s - %s - %stl - kalan:%stl Görünen ad" % (
        debt.transaction_ref.share_ref.share_order_of_member, debt.transaction_ref.transaction_date,
        debt.transaction_ref.amount, debt.remaining_debt)) for debt in debts if debt.remaining_debt > 0]
    return ret if len(ret) > 0 else [("", "Ödenmemiş borcunuz bulunmamaktadır...")]


class Period:
    @staticmethod
    def last_period(first, times):
        month = first.month
        year = first.year

        for i in range(times):
            if month < 12:
                month += 1
            else:
                year += 1
                month = 1
        return "%s-%s" % (year, month)

    @staticmethod
    def months_between_two_date(first: date, second: date):
        if first > second:
            first, second = second, first

        month = first.month
        year = first.year

        month_list = []
        while date(year, month, 1) < second:
            month_list.append("%s-%s" % (year, month,))
            if month < 12:
                month += 1
            else:
                year += 1
                month = 1
        return month_list

    @staticmethod
    def all_months_of_sandik(sandik):
        months = Period.months_between_two_date(sandik.date_of_opening, date.today())
        return months

    @staticmethod
    def all_months_from_date(in_date):
        months = Period.months_between_two_date(in_date, date.today())
        return months
