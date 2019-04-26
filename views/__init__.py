from flask_login import current_user
from pony.orm import select, db_session


class LayoutPageInfo:
    def __init__(self, title):
        self.title = title
        if current_user.is_authenticated:
            self.my_sandiks = []
            with db_session:
                for sandik in select(member.sandik_ref for member in current_user.webuser.members_index):
                    self.my_sandiks.append((sandik.id, sandik.name,))
