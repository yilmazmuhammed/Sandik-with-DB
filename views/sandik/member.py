from pony.orm import db_session
from datetime import date
from pony.orm.core import ObjectNotFound
from flask import redirect, render_template, url_for, flash

from database.dbinit import WebUser, Member, Sandik, Share, MemberAuthorityType, DbTypes
from forms import MemberForm, FormPageInfo
from views import PageInfo


def members_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]
        members = sandik.members_index.sort_by(Member.member_id)
        # TODO bilgileri tek info ile gönder
        return render_template("sandik/members.html", info=MembersPageInfo(title='Members', sandik=sandik, members=members, db_types=DbTypes), sandik_id=sandik_id)


def add_member_to_sandik_page(sandik_id):
    form = MemberForm()

    with db_session:
        sandik = Sandik[sandik_id]
        authorities = sandik.member_authority_types_index
        for authority in authorities:
            form.authority.choices.append((authority.id, authority.name))

    if form.validate_on_submit():
        try:
            with db_session:
                user = WebUser[form.username.data]  # user = WebUser[form.data['username']]
                authority = MemberAuthorityType[form.data['authority']]
                f_date = form.data['date_of_membership']
                # TODO authory_id mi gelmeli, direk authority mi?
                add_member_to_sandik2(sandik_id, user.username, authority.id, f_date)
                # TODO redirect üyeler sayfası ya da yeni eklenen üyenin sayfası
                return redirect(url_for('sandik_management_page', sandik_id=sandik_id))
        # TODO Authority ve User bulunamamasına karşın iki farklı sorgu yap
        except ObjectNotFound:
            flash(u"User not found.", 'danger')

    info = FormPageInfo(form=form, title='Add member to sandik')
    return render_template("form.html", info=info)


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
        new_member = Member(webuser_ref=webuser, sandik_ref=sandik, member_authority_type_ref=authority_type, date_of_membership=date_of_membership)
        Share(member_ref=new_member, share_order_of_member=1, date_of_opening=date_of_membership)


def add_share(member_id, date_of_opening=date.today()):
    with db_session:
        member = Member[member_id]
        last_order = max(s.share_order_of_member for s in Share if s.member_ref == member)
        new_order = last_order + 1
        Share(member_ref=member, share_order_of_member=new_order, date_of_opening=date_of_opening)


class MembersPageInfo(PageInfo):
    def __init__(self, title, sandik, members, db_types):
        super().__init__(title)
        self.sandik = sandik
        self.members = members
        self.db_types = db_types
