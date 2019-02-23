from datetime import date

from pony.orm import db_session

from database.auxiliary import insert_member, insert_share
from database.dbinit import Member, Share, Sandik

from forms import MemberForm


def add_share(member_id, date_of_opening=date.today()):
    with db_session:
        member = Member[member_id]
        last_order = max(s.share_order_of_member for s in Share if s.member_ref == member)
        new_order = last_order + 1
        Share(member_ref=member, share_order_of_member=new_order, date_of_opening=date_of_opening)


# TODO exception kullan, son kullanıcıya çıktıyı exception kullanarak ver
def add_member_to_sandik(form: MemberForm, sandik_id):
    username = form.username.data
    sandik = Sandik[sandik_id]
    if sandik.members_index.select(lambda m: m.webuser_ref.username == username).count() > 0:
        return False

    f_date = form.date_of_membership.data
    new_member = insert_member(webuser_id=username, sandik_id=sandik_id, authority_id=form.authority.data,
                               date_of_membership=f_date)
    insert_share(member_id=new_member.member_id, date_of_opening=f_date)
    return True
