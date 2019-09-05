from pony.orm import commit

from database.auxiliary import insert_member, insert_share, insert_member_authority_type, insert_debt_type, \
    remove_member

from forms import MemberForm, DebtTypeForm


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


def add_member_authority_type_to_sandik(form, sandik_id):
    return insert_member_authority_type(form.name.data, form.capacity.data, sandik_id,
                                        form.is_admin.data if form.is_admin else False,
                                        form.reading_transaction.data, form.writing_transaction.data,
                                        form.adding_member.data, form.throwing_member.data)


def add_debt_type_to_sandik(form: DebtTypeForm, sandik_id):
    return insert_debt_type(sandik_id, form.name.data, form.explanation.data, form.max_number_of_installments.data,
                            form.max_amount.data, form.min_installment_amount.data)


def remove_member_from_sandik(member_id):
    return remove_member(member_id)