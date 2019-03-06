from flask import redirect, url_for, render_template, abort, flash
from flask_login import login_required, current_user
from pony.orm import db_session, ObjectNotFound

from database.dbinit import Sandik, MemberAuthorityType, Member, WebUser
from forms import SandikForm, FormPageInfo, MemberForm, AddingShareForm
from views import PageInfo
from views.authorizations import authorization_to_the_sandik_required
from views.sandik.auxiliary import SandikManagementPanel
from views.sandik.db import add_member_to_sandik, add_share_to_member
from views.transaction.auxiliary import member_choices
from views.webuser.auxiliary import SandikInfo


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


@authorization_to_the_sandik_required(reading_transaction=True)
def sandik_management_page(sandik_id):
    try:
        sandik = SandikManagementPanel(sandik_id)
        info = PageInfo(title='Sandık Management Panel')
        return render_template('sandik/management_panel.html', info=info, sandik=sandik)
    except ObjectNotFound:
        return abort(404)


@authorization_to_the_sandik_required(reading_transaction=True)
def members_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]
        sandik_info = SandikInfo(sandik)
        page_info = PageInfo(title='Members')
        return render_template("sandik/members.html", page_info=page_info, sandik=sandik_info)


@authorization_to_the_sandik_required(adding_member=True)
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
                # user = WebUser[form.username.data]
                # authority = MemberAuthorityType[form.data['authority']]
                # f_date = form.data['date_of_membership']
                #
                # # TODO authory_id mi gelmeli, direk authority mi?
                # add_member_to_sandik2(sandik_id, user.username, authority.id, f_date)
                # # TODO redirect üyeler sayfası ya da yeni eklenen üyenin sayfası

                if add_member_to_sandik(form, sandik_id):
                    return redirect(url_for('sandik_management_page', sandik_id=sandik_id))
                else:
                    flash(u"Bu kullanıcının bu sandıkta üyeliği zaten var.\n"
                          u"ya da\n"
                          u"Bu üyenin kayıt tarihi sandığın kuruluş tarihinden daha eski.", 'danger')
        # TODO Authority ve User bulunamamasına karşın iki farklı sorgu yap
        except ObjectNotFound:
            flash(u"User not found.", 'danger')

    info = FormPageInfo(form=form, title='Add member to sandik')
    return render_template("form.html", info=info)


@authorization_to_the_sandik_required(adding_member=True)
def add_share_to_member_page(sandik_id):
    form = AddingShareForm()

    form.member.choices = member_choices(sandik_id)

    if form.validate_on_submit():
        try:
            with db_session:
                if add_share_to_member(form.member.data, form.date_of_opening.data):
                    return redirect(url_for('sandik_management_page', sandik_id=sandik_id))
                else:
                    flash(u"Hisse eklenemedi.", 'danger')
        # Member bulunamadıysa
        except ObjectNotFound:
            flash(u"Member not found.", 'danger')

    info = FormPageInfo(form=form, title='Add share to member')
    return render_template("form.html", info=info)

