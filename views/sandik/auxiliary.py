from pony.orm import select, db_session

from database.dbinit import Sandik, Transaction


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
