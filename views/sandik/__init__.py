from flask import url_for, redirect, render_template, abort
from flask_login import login_required, current_user
from pony.orm import db_session
from pony.orm.core import ObjectNotFound

from database.dbinit import Sandik, MemberAuthorityType, Member, WebUser
from forms import SandikForm, FormPageInfo


@login_required
def new_sandik_page():
    form = SandikForm()

    if form.validate_on_submit():
        with db_session:
            # Formdan alınan bilgilere göre sandık oluştur
            new_sandik = Sandik(name=form.data['name'], explanation=form.data['explanation'])

            # Varsayılan olarak sandık başkanı ve normal üye yetkisi oluştur
            admin_user = MemberAuthorityType(name='Sandık başkanı', max_number_of_members=1, sandik_ref=new_sandik, is_admin=True)
            normal_user = MemberAuthorityType(name='Normal üye', max_number_of_members=-1, sandik_ref=new_sandik)

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
        with db_session:
            sandik = Sandik[sandik_id]
        info = SandikPageInfo(title='Sandık Management Panel', sandik=sandik)
        return render_template('sandik/management_panel.html', info=info)
    except ObjectNotFound:
        return abort(404)


class SandikPageInfo:
    def __init__(self, title, sandik):
        self.title = title
        self.sandik = sandik
