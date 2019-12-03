from flask_login import current_user
from pony.orm import select, db_session

from views.others.auxiliary import get_translation


class LayoutPageInfo:
    def __init__(self, title):
        self.title = title
        self.translation = get_translation()
        if current_user.is_authenticated:
            self.my_sandiks = []
            with db_session:
                for member, sandik in select((member, member.sandik_ref,)
                                             for member in current_user.webuser.members_index):
                    mat = member.member_authority_type_ref
                    is_there_authorizations = mat.is_admin or mat.reading_transaction or mat.writing_transaction or mat.adding_member or mat.throwing_member
                    self.my_sandiks.append({"id": sandik.id, "name": sandik.name,
                                            "is_there_authorizations": is_there_authorizations, 'mat': mat})
