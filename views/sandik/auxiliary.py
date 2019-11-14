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
            self.number_of_members = select(member for member in sandik.members_index if member.is_active).count()
