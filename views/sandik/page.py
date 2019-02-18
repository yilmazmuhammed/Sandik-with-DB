from flask import redirect, url_for, render_template, abort, flash
from flask_login import login_required, current_user
from pony.orm import db_session, ObjectNotFound, select

from database.dbinit import Sandik, MemberAuthorityType, Member, WebUser, DbTypes, Transaction
from forms import SandikForm, FormPageInfo, MemberForm
from views import PageInfo
from views.sandik.auxiliary import MembersPageInfo, SandikManagementPanel
from views.sandik.db import add_member_to_sandik2
from views.webuser.auxiliary import MemberInfo


@login_required
def new_sandik_page():
    form = SandikForm()

    if form.validate_on_submit():
        with db_session:
            # Formdan alınan bilgilere göre sandık oluştur
            new_sandik = Sandik(name=form.data['name'], explanation=form.data['explanation'])

            # Varsayılan olarak sandık başkanı ve normal üye yetkisi oluştur
            admin_user = MemberAuthorityType(name='Sandık başkanı', max_number_of_members=1, sandik_ref=new_sandik,
                                             is_admin=True)
            MemberAuthorityType(name='Normal üye', max_number_of_members=-1, sandik_ref=new_sandik)

            # Varsayılan olarak sandığı oluşturan kişiye sandık başkanı olarak üyelik oluşturulur.
            Member(webuser_ref=WebUser[current_user.webuser.username], sandik_ref=new_sandik,
                   member_authority_type_ref=admin_user)

            # TODO yeni sandık oluşturulunca sandıklarım/(yeni sandık ayarları) gibi bir sayfaya yönlendir
            return redirect(url_for('sandik_management_page', sandik_id=new_sandik.id))

    info = FormPageInfo(form=form, title='Add new sandık')
    return render_template('form.html', info=info)


@login_required
def sandik_management_page(sandik_id):
    try:
        sandik = SandikManagementPanel(sandik_id)
        info = PageInfo(title='Sandık Management Panel')
        return render_template('sandik/management_panel.html', info=info, sandik=sandik)
    except ObjectNotFound:
        return abort(404)


@login_required
def members_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]
        members = []
        for m in sandik.members_index.sort_by(Member.member_id):
            members.append(MemberInfo(m))
        # TODO bilgileri tek info ile gönder
        info = MembersPageInfo(title='Members', sandik=sandik, members=members, db_types=DbTypes)
        return render_template("sandik/members.html", members=members, sandik_id=sandik_id, info=info)


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


@login_required
def transactions_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]

        transactions = select(transaction for transaction in Transaction
                              if transaction.share_ref.member_ref.sandik_ref == sandik)[:]
        return render_template("transactions.html", transactions=transactions)
