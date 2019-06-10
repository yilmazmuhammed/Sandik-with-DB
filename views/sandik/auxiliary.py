from pony.orm import select, db_session

from database.dbinit import Sandik, Share


class SandikManagementPanel:
    def __init__(self, sandik_id):
        with db_session:
            sandik = Sandik[sandik_id]
            self.id = sandik_id
            self.number_of_transactions = select(share.transactions_index for share in Share
                                                 if share.member_ref.sandik_ref == sandik).count()
            self.number_of_members = select(member for member in sandik.members_index if member.is_active).count()
