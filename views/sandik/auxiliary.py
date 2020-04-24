from pony.orm import select, db_session

from database.dbinit import Sandik, Transaction, Member, Share
from views import get_translation
from views.sandik.db import get_sandik


class SandikManagementPanel:
    def __init__(self, sandik_id):
        with db_session:
            sandik = Sandik[sandik_id]
            self.id = sandik_id
            self.number_of_transactions = select(t for t in Transaction
                                                 if t.share_ref.member_ref.sandik_ref == sandik
                                                 and t.confirmed_by and not t.deleted_by).count()
            self.number_of_unconfirmed_transactions = select(t for t in Transaction
                                                             if t.share_ref.member_ref.sandik_ref == sandik
                                                             and not t.confirmed_by and not t.deleted_by).count()
            self.number_of_members = select(member for member in sandik.members_index if member.is_active).count()


def get_chat_ids_of_sandik_admins(sandik: Sandik = None, sandik_id=None):
    sandik: Sandik = sandik if sandik else Sandik[sandik_id]
    return select(member.webuser_ref.telegram_chat_id for member in sandik.members_index
                  if member.member_authority_type_ref.is_admin and member.webuser_ref.telegram_chat_id)[:]


@db_session
def member_choices(sandik_id, only_active_member=True):
    sandik = get_sandik(sandik_id)
    members = sandik.members_index.filter(lambda member: member.is_active >= only_active_member)
    return select((member.id, member.webuser_ref.name_surname()) for member in members).order_by(
        lambda m_id, name_surname: name_surname)[:]


@db_session
def all_share_choices(sandik_id, only_active_member=True, only_active_shares=True):
    return select((share.id, share.name_surname_share()) for share in Share
                  if share.member_ref.sandik_ref.id == sandik_id and share.is_active >= only_active_shares
                  and share.member_ref.is_active >= only_active_member).order_by(lambda s_id, nss: nss)[:]


@db_session
def share_choices(member_id, only_active_shares=True):
    t = get_translation()['views']['sandik']['auxiliary']['member_choices']
    member = Member.get(id=member_id)
    shares = member.shares_index.filter(lambda share: share.is_active >= only_active_shares)
    return select((share.id, t['share'] + " - " + str(share.share_order_of_member)) for share in shares).order_by(
        lambda s_id, share_order: share_order)[:]
