from flask import redirect, url_for, render_template, abort, flash
from flask_login import login_required, current_user
from pony.orm import db_session, ObjectNotFound

from database.auxiliary import insert_share
from database.dbinit import Sandik, MemberAuthorityType, Member, WebUser
from forms import SandikForm, FormPageInfo, MemberForm, AddingShareForm, MemberAuthorityTypeForm, DebtTypeForm
from views import LayoutPageInfo
from views.authorizations import authorization_to_the_sandik_required, is_there_authorization_to_the_sandik
from views.sandik.auxiliary import SandikManagementPanel
from views.sandik.db import add_member_to_sandik, add_member_authority_type_to_sandik, add_debt_type_to_sandik
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
            MemberAuthorityType(name='Normal üye', max_number_of_members=0, sandik_ref=new_sandik)

            # Varsayılan olarak sandığı oluşturan kişiye sandık başkanı olarak üyelik oluşturulur.
            Member(webuser_ref=WebUser[current_user.webuser.username], sandik_ref=new_sandik,
                   member_authority_type_ref=admin_user)

            # TODO yeni sandık oluşturulunca sandıklarım/(yeni sandık ayarları) gibi bir sayfaya yönlendir
            return redirect(url_for('sandik_management_page', sandik_id=new_sandik.id))

    info = FormPageInfo(form=form, title='Add new sandık')
    return render_template('form.html', layout_page=LayoutPageInfo("Add new sandık"), info=info)


@authorization_to_the_sandik_required(reading_transaction=True)
def sandik_management_page(sandik_id):
    try:
        sandik = SandikManagementPanel(sandik_id)
        info = LayoutPageInfo(title='Sandık Management Panel')
        return render_template('sandik/management_panel.html', layout_page=info, sandik=sandik)
    except ObjectNotFound:
        return abort(404)


@authorization_to_the_sandik_required()
def members_page(sandik_id):
    with db_session:
        sandik = Sandik[sandik_id]
        sandik_info = SandikInfo(sandik)
        page_info = LayoutPageInfo(title='Members')
        member_authority = is_there_authorization_to_the_sandik(sandik_id=sandik_id, reading_transaction=True)
        return render_template("sandik/members.html", layout_page=page_info, sandik=sandik_info,
                               member_authority=member_authority)


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
    return render_template("form.html", layout_page=LayoutPageInfo("Add member to sandik"), info=info)


@authorization_to_the_sandik_required(adding_member=True)
def edit_member_of_sandik_page(sandik_id, username):
    form = MemberForm()
    selected_dict=None
    selected_ids=None
    with db_session:
        sandik = Sandik[sandik_id]
        authorities = sandik.member_authority_types_index.sort_by(lambda a: a.id)
        for authority in authorities:
            form.authority.choices.append((authority.id, authority.name))

        try:
            webuser = WebUser[username]
            member = Member.get(sandik_ref=sandik, webuser_ref=webuser)
            form.username.data = webuser.username
            form.username.render_kw["readonly"] = ""
            selected_dict = {form.authority.id: str(member.member_authority_type_ref.id)}
            selected_ids = [form.authority.id]
            form.date_of_membership.render_kw["value"] = member.date_of_membership
            form.submit.label.text = "Edit member"
        except ObjectNotFound:
            flash(u"Member not found.", 'danger')
            return abort(404)

    if form.validate_on_submit():
        try:
            with db_session:
                print(form.username.data)
                if username != form.username.data:
                    flash(u"Kullanıcı adı değiştirilemez", 'danger')
                else:
                    print(member.member_authority_type_ref, member.date_of_membership)
                    print(form.authority.data, form.date_of_membership.data)
                    member = Member.get(sandik_ref=Sandik[sandik_id], webuser_ref=WebUser[username])
                    member.member_authority_type_ref = MemberAuthorityType[form.authority.data]
                    member.date_of_membership = form.date_of_membership.data
                    return redirect(url_for('sandik_management_page', sandik_id=sandik_id))
        # TODO Authority ve User bulunamamasına karşın iki farklı sorgu yap
        except Exception as exc:
            flash(u"Exception: %s." % exc, 'danger')

    info = FormPageInfo(form=form, title='Edit member of sandik')
    return render_template("form.html", layout_page=LayoutPageInfo("Edit member of sandik"), info=info, selected_dict=selected_dict, selected_ids=selected_ids)


@authorization_to_the_sandik_required(adding_member=True)
def add_share_to_member_page(sandik_id):
    form = AddingShareForm()

    form.member.choices = member_choices(sandik_id)

    if form.validate_on_submit():
        try:
            with db_session:
                if insert_share(form.member.data, form.date_of_opening.data):
                    return redirect(url_for('sandik_management_page', sandik_id=sandik_id))
                else:
                    flash(u"Hisse eklenemedi.", 'danger')
        # Member bulunamadıysa
        except ObjectNotFound:
            flash(u"Member not found.", 'danger')

    info = FormPageInfo(form=form, title='Add share to member')
    return render_template("form.html", layout_page=LayoutPageInfo("Add share to member"), info=info)


@authorization_to_the_sandik_required(is_admin=True)
def add_member_authority_type_to_sandik_page(sandik_id):
    form = MemberAuthorityTypeForm()

    if form.validate_on_submit():
        if add_member_authority_type_to_sandik(form, sandik_id):
            return redirect(url_for('sandik_management_page', sandik_id=sandik_id))
        else:
            flash(u"Üye yetki türü eklenemedi.", 'danger')

    info = FormPageInfo(form=form, title='Add member authority type to the sandik')
    return render_template("form.html", layout_page=LayoutPageInfo("Add member authority type to sandik"), info=info)


@authorization_to_the_sandik_required(is_admin=True)
def add_debt_type_to_sandik_page(sandik_id):
    form = DebtTypeForm()

    if form.validate_on_submit():
        if add_debt_type_to_sandik(form, sandik_id):
            return redirect(url_for('sandik_management_page', sandik_id=sandik_id))
        else:
            flash(u"Borç türü eklenemedi.", 'danger')

    info = FormPageInfo(form=form, title='Add debt type to the sandik')
    return render_template("form.html", layout_page=LayoutPageInfo("Add debt type to sandik"), info=info)
