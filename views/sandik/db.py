from datetime import date

from pony.orm import db_session

from database.dbinit import WebUser, Sandik, MemberAuthorityType, Member, Share


# TODO authory_id mi gelmeli, direk authority mi?
def add_member_to_sandik(sandik_id, username, authority_id, date_of_membership=date.today()):
    with db_session:
        webuser = WebUser[username]
        sandik = Sandik[sandik_id]
        authority_type = MemberAuthorityType[authority_id]
        new_member = Member(webuser_ref=webuser, sandik_ref=sandik, member_authority_type_ref=authority_type,
                            date_of_membership=date_of_membership)
        Share(member_ref=new_member, share_order_of_member=1, date_of_opening=date_of_membership)


# TODO authory_id mi gelmeli, direk authority mi?
def add_member_to_sandik2(sandik, webuser, authority_type, date_of_membership=date.today()):
    with db_session:
        new_member = Member(webuser_ref=webuser, sandik_ref=sandik, member_authority_type_ref=authority_type,
                            date_of_membership=date_of_membership)
        Share(member_ref=new_member, share_order_of_member=1, date_of_opening=date_of_membership)


def add_share(member_id, date_of_opening=date.today()):
    with db_session:
        member = Member[member_id]
        last_order = max(s.share_order_of_member for s in Share if s.member_ref == member)
        new_order = last_order + 1
        Share(member_ref=member, share_order_of_member=new_order, date_of_opening=date_of_opening)
