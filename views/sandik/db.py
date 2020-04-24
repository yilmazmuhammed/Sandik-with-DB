from pony.orm import commit, db_session

from database.auxiliary import insert_member, insert_share, insert_member_authority_type, insert_debt_type, \
    remove_member, remove_share
from database.dbinit import Share, Member, Sandik
from database.exceptions import ThereIsNotMember, ThereIsNotShare, ThereIsNotSandik

from views import get_translation


# TODO exception kullan, son kullanıcıya çıktıyı exception kullanarak ver
def add_member_to_sandik(form, sandik_id):
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


def add_member_authority_type_to_sandik(form, sandik_id):
    return insert_member_authority_type(form.name.data, sandik_id, form.capacity.data,
                                        form.is_admin.data if form.is_admin else False,
                                        form.reading_transaction.data, form.writing_transaction.data,
                                        form.adding_member.data, form.throwing_member.data)


def add_debt_type_to_sandik(form, sandik_id):
    return insert_debt_type(sandik_id, form.name.data, form.explanation.data, form.max_number_of_installments.data,
                            form.max_amount.data, form.min_installment_amount.data)


def remove_member_from_sandik(member_id, remover_username):
    return remove_member(member_id, remover_username)


@db_session
def remove_share_of_member_from_sandik(share_id, member_id, sandik_id, remover_username):
    t = get_translation()['exceptions']
    share = get_share(share_id)
    member = get_member(member_id)
    sandik = get_sandik(sandik_id)
    if member not in sandik.members_index:
        raise ThereIsNotMember(t['there_is_not_member'])
    if share not in member.shares_index:
        raise ThereIsNotShare(t['there_is_not_share'])
    return remove_share(share_id, remover_username)


def get_sandik(sandik_id):
    sandik = Sandik.get(id=sandik_id)
    if not sandik:
        raise ThereIsNotSandik(get_translation()['exceptions']['there_is_not_sandik'])
    return sandik


def get_member(member_id):
    member = Member.get(id=member_id)
    if not member:
        raise ThereIsNotMember(get_translation()['exceptions']['there_is_not_member'])
    return member


def get_share(share_id):
    share = Share.get(id=share_id)
    if not share:
        raise ThereIsNotShare(get_translation()['exceptions']['there_is_not_share'])
    return share