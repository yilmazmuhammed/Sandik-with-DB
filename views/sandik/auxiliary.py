from pony.orm import select, db_session

from database.dbinit import Transaction, Sandik
from views import PageInfo


class MembersPageInfo(PageInfo):
    def __init__(self, title, sandik, members, db_types):
        super().__init__(title)
        self.sandik = sandik
        self.members = members
        self.db_types = db_types


class SandikManagementPanel:
    def __init__(self, sandik_id):
        with db_session:
            sandik = Sandik[sandik_id]
            self.id = sandik_id
            self.number_of_transactions = select(t for t in Transaction
                                                 if t.share_ref.member_ref.sandik_ref == sandik).count()
            self.number_of_members = sandik.members_index.count()
