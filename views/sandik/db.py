from pony.orm import commit

from database.auxiliary import insert_member, insert_share

from forms import MemberForm


# TODO exception kullan, son kullanıcıya çıktıyı exception kullanarak ver
def add_member_to_sandik(form: MemberForm, sandik_id):
    f_date = form.date_of_membership.data

    # TODO Eğer share eklerken sıkıntı olursa eklenen member'ı da sil/dahil etme
    new_member = insert_member(username=form.username.data, sandik_id=sandik_id, authority_id=form.authority.data,
                               date_of_membership=f_date)
    if new_member is None:
        return False

    # commit yapmayınca member.id ile member'i bulamıyor
    commit()

    if insert_share(member_id=new_member.id, date_of_opening=f_date) is None:
        return False

    return True
