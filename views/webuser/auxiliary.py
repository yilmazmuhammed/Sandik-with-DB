from flask_login import UserMixin
from pony.orm import db_session

from database.dbinit import WebUser, Share, select


class FlaskUser(UserMixin):
    def __init__(self, username):
        self.username = username
        with db_session:
            self.username = username
            self.webuser = WebUser[username]
            self.is_admin = self.webuser.is_admin

    def get_id(self):
        return self.webuser.username

    @property
    def is_active(self):
        return self.webuser.is_active


class SandikInfo:
    def __init__(self, sandik):
        self.dbTable = sandik

        self.sandik_id = sandik.id

        self.members = []
        for member in sandik.members_index.sort_by(lambda m: m.webuser_ref.name):
            self.members.append(MemberInfo(member))

        self.paid_contributions = sum(m.paid_contributions for m in self.members)
        self.debts_received = sum(m.debts_received for m in self.members)
        self.paid_installments = sum(m.paid_installments for m in self.members)
        self.others = sum(m.others for m in self.members)
        self.remaining_debts = self.debts_received - self.paid_installments
        self.total = self.paid_contributions + self.others - self.remaining_debts

        self.debt_types = sandik.debt_types_index


class MemberInfo:
    def __init__(self, member):
        self.dbTable = member
        self.is_active = member.is_active

        self.shares = []
        for share in member.shares_index.sort_by(Share.share_order_of_member):
            self.shares.append(ShareInfo(share))

        self.paid_contributions = sum(s.paid_contributions for s in self.shares)
        self.debts_received = sum(s.debts_received for s in self.shares)
        self.paid_installments = sum(s.paid_installments for s in self.shares)
        self.others = sum(s.others for s in self.shares)
        self.remaining_debts = self.debts_received - self.paid_installments
        self.remaining_debts_with_types = {}
        for debt_type in share.member_ref.sandik_ref.debt_types_index:
            self.remaining_debts_with_types[debt_type.id] = sum(
                s.remaining_debts_with_types[debt_type.id] for s in self.shares
            )


class ShareInfo:
    def __init__(self, share):
        self.dbTable = share
        self.is_active = share.is_active
        self.share_order_of_member = share.share_order_of_member

        self.paid_contributions = select(t.amount for t in share.transactions_index
                                         if t.contribution_index and t.confirmed_by and not t.deleted_by).sum()
        self.debts_received = select(t.amount for t in share.transactions_index
                                     if t.debt_ref and t.confirmed_by and not t.deleted_by).sum()
        self.paid_installments = select(t.amount for t in share.transactions_index
                                        if t.payment_ref and t.confirmed_by and not t.deleted_by).sum()
        self.others = select(t.amount for t in share.transactions_index
                             if not t.contribution_index and not t.debt_ref and not t.payment_ref
                             and t.confirmed_by and not t.deleted_by).sum()
        self.remaining_debts = 0
        self.remaining_debts_with_types = {}
        for debt_type in share.member_ref.sandik_ref.debt_types_index:
            self.remaining_debts_with_types[debt_type.id] = select(t.debt_ref.remaining_debt
                                                                   for t in share.transactions_index
                                                                   if t.debt_ref
                                                                   and t.debt_ref.debt_type_ref == debt_type
                                                                   and t.confirmed_by and not t.deleted_by
                                                                   ).sum()
            self.remaining_debts += self.remaining_debts_with_types[debt_type.id]


def get_chat_ids_of_site_admins():
    chat_ids = []
    if WebUser['admin'].telegram_chat_id:
        chat_ids.append(WebUser['admin'].telegram_chat_id)
    return chat_ids
