from datetime import date

from flask import flash
from pony.orm import db_session, count, select

from database.dbinit import (Debt, Transaction, Share, DebtType, Payment, Contribution, WebUser, Sandik,
                             MemberAuthorityType, Member, )
from database.exceptions import OutstandingDebt, ThereIsPayment, NotLastPayment, DeletedTransaction, \
    NegativeTransaction, DuplicateContributionPeriod, Overpayment
from views import get_translation
from views.transaction.auxiliary import Period


@db_session
def insert_debt(in_date: date, amount, share_id, explanation, type_id, num_of_inst,
                created_by_username, confirmed_by_username=None, deleted_by_username=None, id=None):
    id = id if id is not None else select(t.id for t in Transaction).max() + 1
    created_by = WebUser[created_by_username]
    if confirmed_by_username is not "" and confirmed_by_username is not None:
        confirmed_by = WebUser[confirmed_by_username]
    else:
        confirmed_by = None
    if deleted_by_username is not "" and deleted_by_username is not None:
        deleted_by = WebUser[deleted_by_username]
    else:
        deleted_by = None

    num_of_inst = int(num_of_inst)
    ia = int(amount) / num_of_inst
    ia = int(ia) if ia % 1 == 0 else int(ia) + 1
    return Debt(
        transaction_ref=Transaction(
            id=id, share_ref=Share[share_id], transaction_date=in_date, amount=amount, type='Debt',
            explanation=explanation,
            created_by=created_by, confirmed_by=confirmed_by, deleted_by=deleted_by),
        debt_type_ref=DebtType[type_id], number_of_installment=num_of_inst, installment_amount=ia,
        paid_debt=0, paid_installment=0, remaining_debt=amount, remaining_installment=num_of_inst,
        starting_period=Period.last_period(in_date, 1), due_period=Period.last_period(in_date, num_of_inst))


@db_session
def insert_payment(in_date, amount, explanation,
                   created_by_username, confirmed_by_username=None, deleted_by_username=None,
                   debt_id=None, transaction_id=None, id=None):
    id = id if id is not None else select(t.id for t in Transaction).max() + 1
    debt = Debt[debt_id] if debt_id else Debt.get(transaction_ref=Transaction[transaction_id])
    share = debt.transaction_ref.share_ref

    created_by = WebUser[created_by_username]
    if confirmed_by_username is not "" and confirmed_by_username is not None:
        confirmed_by = WebUser[confirmed_by_username]
    else:
        confirmed_by = None
    if deleted_by_username is not "" and deleted_by_username is not None:
        deleted_by = WebUser[deleted_by_username]
    else:
        deleted_by = None

    amount = int(amount)

    # Final controls
    # TODO Kontrolleri excception ile yap, hata mesajını fonksiyonun kullanıldığı yerde ver
    if amount > debt.remaining_debt:  # If new paid amount is bigger than remaining amount of the debt
        flash(u"Paid amount cannot be more than the remaining debt", 'danger')
        return None
    else:  # There is no problem
        # TODO pnod = p.debt_ref.payment_index
        pnod = count(select(p for p in Payment if p.debt_ref == debt
                            and p.transaction_ref.confirmed_by and not p.transaction_ref.deleted_by))
        pdsf = debt.paid_debt + amount
        pisf = int(pdsf / debt.installment_amount)
        rdsf = debt.remaining_debt - amount
        risf = debt.number_of_installment - pisf
        p = Payment(debt_ref=debt, payment_number_of_debt=pnod, paid_debt_so_far=pdsf, paid_installment_so_far=pisf,
                    remaining_debt_so_far=rdsf, remaining_installment_so_far=risf,
                    transaction_ref=Transaction(id=id, share_ref=share, transaction_date=in_date, amount=amount,
                                                type='Payment', explanation=explanation, created_by=created_by,
                                                confirmed_by=confirmed_by, deleted_by=deleted_by
                                                )
                    )
        if confirmed_by:
            debt.paid_debt = pdsf
            debt.paid_installment = pisf
            debt.remaining_debt = rdsf
            debt.remaining_installment = risf
        return p


# TODO flash yerine exception kullan, fonksiyonun kullanıdığı yerlerde exceptionları yakalayarak flash ile gerekli
#  mesajı yazdır
@db_session
def insert_contribution(in_date: date, amount, share_id, explanation, new_periods: list,
                        created_by_username, confirmed_by_username=None, deleted_by_username=None,
                        is_from_import_data=False, id=None):
    id = id if id is not None else select(t.id for t in Transaction).max() + 1
    # ..._by_username'ler None mı olsun yoksa "" mı?
    share = Share[share_id]
    sandik = share.member_ref.sandik_ref
    created_by = WebUser[created_by_username]
    if confirmed_by_username is not "" and confirmed_by_username is not None:
        confirmed_by = WebUser[confirmed_by_username]
    else:
        confirmed_by = None
    if deleted_by_username is not "" and deleted_by_username is not None:
        deleted_by = WebUser[deleted_by_username]
    else:
        deleted_by = None

    # TODO Conribution_amount değerini sandık kurallarından al
    contribution_amount = sandik.contribution_amount

    # TODO bu geçici çözümü kaldırıp import-data daki satırları düzenle ya da hatalı veri tablosu için yeni fonksiyon ekle
    if not is_from_import_data:
        if amount % contribution_amount:
            flash(u"Paid amount must be divided by contribution amount (%s)." % contribution_amount, 'danger')
            return False
        elif amount / contribution_amount != len(new_periods):
            flash(u"Paid amount must be contribution amount (%s) * <number_of_months>." % contribution_amount, 'danger')
            flash(u"Fakat başlangıç aidatı sistemi yapılana kadar işlem eklendi.", 'danger')
            # return False

        old_periods = select(c.contribution_period for c in Contribution
                             if c.transaction_ref.share_ref == share
                             and c.transaction_ref.confirmed_by and not c.transaction_ref.deleted_by)[:]
        for new_period in new_periods:
            if new_period in old_periods:
                raise DuplicateContributionPeriod(get_translation()['exceptions']['duplicate_contribution_period'])

    transaction_ref = Transaction(id=id, share_ref=share, transaction_date=in_date,
                                  amount=amount, type='Contribution', explanation=explanation,
                                  created_by=created_by, confirmed_by=confirmed_by, deleted_by=deleted_by)

    contributions = []
    for new_period in new_periods:
        contributions.append(Contribution(transaction_ref=transaction_ref, contribution_period=new_period))
    return contributions


@db_session
def insert_transaction(in_date, amount, share_id, explanation,
                       created_by_username, confirmed_by_username=None, deleted_by_username=None, id=None):
    id = id if id is not None else select(t.id for t in Transaction).max() + 1
    created_by = WebUser[created_by_username]
    if confirmed_by_username is not "" and confirmed_by_username is not None:
        confirmed_by = WebUser[confirmed_by_username]
    else:
        confirmed_by = None
    if deleted_by_username is not "" and deleted_by_username is not None:
        deleted_by = WebUser[deleted_by_username]
    else:
        deleted_by = None

    return Transaction(id=id, share_ref=Share[share_id], transaction_date=in_date, amount=amount,
                       type='Other', explanation=explanation,
                       created_by=created_by, confirmed_by=confirmed_by, deleted_by=deleted_by)


@db_session
def insert_webuser(username, password_hash, date_of_registration: date = date.today(), name=None, surname=None,
                   is_admin: bool = False, is_active: bool = True):
    return WebUser(username=username, password_hash=password_hash, date_of_registration=date_of_registration, name=name,
                   surname=surname, is_active=is_active, is_admin=is_admin)


@db_session
def insert_member(username, sandik_id, authority_id, date_of_membership: date = date.today(), is_active: bool = True,
                  id=None):
    sandik = Sandik[sandik_id]

    # TODO Use exception
    if sandik.members_index.select(lambda m: m.webuser_ref.username == username).count() > 0:
        return None
    elif date_of_membership < sandik.date_of_opening:
        return None

    return Member(id=id, webuser_ref=WebUser[username], sandik_ref=Sandik[sandik_id],
                  member_authority_type_ref=MemberAuthorityType[authority_id], date_of_membership=date_of_membership,
                  is_active=is_active)


@db_session
def insert_share(member_id, date_of_opening: date = date.today(), is_active: bool = True, share_order_of_member=None,
                 id=None):
    member = Member[member_id]

    # TODO Use exception
    if date_of_opening < member.date_of_membership:
        return None

    if not share_order_of_member:
        if member.shares_index:
            share_order_of_member = max(select(s.share_order_of_member for s in member.shares_index)) + 1
        else:
            share_order_of_member = 1

    return Share(id=id, member_ref=member, share_order_of_member=share_order_of_member, date_of_opening=date_of_opening,
                 is_active=is_active)


@db_session
def insert_sandik(name, contribution_amount, explanation, date_of_opening: date = date.today(), is_active: bool = True,
                  id=None):
    return Sandik(id=id, name=name, contribution_amount=contribution_amount, explanation=explanation,
                  date_of_opening=date_of_opening, is_active=is_active)


@db_session
def insert_member_authority_type(name, capacity, sandik_id, is_admin=False, reading_transaction=False,
                                 writing_transaction: bool = False, adding_member: bool = False,
                                 throwing_member: bool = False, id=None):
    sandik = Sandik[sandik_id]
    return MemberAuthorityType(id=id, name=name, max_number_of_members=capacity, sandik_ref=sandik, is_admin=is_admin,
                               reading_transaction=reading_transaction, writing_transaction=writing_transaction,
                               adding_member=adding_member, throwing_member=throwing_member)


@db_session
def insert_debt_type(sandik_id, name, explanation, max_number_of_instalments=0, max_amount=0, min_installment_amount=0,
                     id=None):
    sandik = Sandik[sandik_id]
    return DebtType(id=id, sandik_ref=sandik, name=name, explanation=explanation,
                    max_number_of_installments=max_number_of_instalments, max_amount=max_amount,
                    min_installment_amount=min_installment_amount)


@db_session
def name_surname(webuser_id=None, member_id=None, share_id=None, share: Share = None, member: Member = None,
                 webuser: WebUser = None):
    if share_id:
        share = Share[share_id]

    if share:
        member = share.member_ref
    elif member_id:
        member = Member[member_id]

    if member:
        webuser = member.webuser_ref
    elif webuser_id:
        webuser = WebUser[webuser_id]

    if webuser:
        return webuser.name + " " + webuser.surname


@db_session
def remove_share(share_id, remover_username):
    share = Share[share_id]
    remaining_debts = sum(t.debt_ref.remaining_debt for t in share.transactions_index
                          if t.debt_ref and t.confirmed_by and not t.deleted_by)
    if remaining_debts > 0:
        raise OutstandingDebt("Hissenin ödenmemiş borcu var.")
    paid_contributions = sum(t.amount for t in share.transactions_index
                             if t.contribution_index and t.confirmed_by and not t.deleted_by)
    contributions = insert_contribution(date.today(), -paid_contributions, share_id, "Üye ayrılması", ['0-0'],
                                        remover_username, is_from_import_data=True)
    return contributions[0]


@db_session
def remove_member(member_id, remover_username):
    member = Member[member_id]
    try:
        for share in member.shares_index.select(lambda s: s.is_active):
            remove_share(share.id, remover_username)
        member.is_active = False
        return member
    except OutstandingDebt:
        raise OutstandingDebt("Üyenin ödenmemiş borcu var.")


@db_session
def remove_transaction(transaction_id, deleted_by_username):
    t = Transaction[transaction_id]

    if t.confirmed_by:
        # if t.debt_ref.payment_index
        if t.deleted_by:
            raise DeletedTransaction(get_translation()["exceptions"]["deleted_transaction"])

        if t.contribution_index:
            pass
        elif t.debt_ref:
            if t.debt_ref.payments_index.select(lambda p: not p.transaction_ref.deleted_by):
                raise ThereIsPayment(get_translation()["exceptions"]["there_is_payment"])
            pass
        elif t.payment_ref:
            if t.payment_ref.payment_number_of_debt != int((select(
                    p.payment_number_of_debt for p in t.payment_ref.debt_ref.payments_index if
                    not bool(t.deleted_by) and bool(t.confirmed_by))).max() or 0):
                raise NotLastPayment(get_translation()["exceptions"]["not_last_payment"])

            debt = t.payment_ref.debt_ref
            debt.paid_debt = debt.paid_debt - t.amount
            debt.paid_installment = int(debt.paid_debt / debt.installment_amount)
            debt.remaining_debt = debt.transaction_ref.amount - debt.paid_debt
            debt.remaining_installment = debt.number_of_installment - debt.paid_installment
            pass
        else:
            pass

    t.deleted_by = WebUser[deleted_by_username]


def confirm_other_transaction(t_id, confirmed_by_username):
    t = Transaction[t_id]
    share = t.share_ref
    sum_of_other = select(t.amount for t in share.transactions_index
                          if not t.contribution_index and not t.debt_ref and not t.payment_ref
                          and t.confirmed_by and not t.deleted_by).sum()

    if sum_of_other + t.amount < 0:
        raise NegativeTransaction(get_translation()['exceptions']['negative_other'])

    t.confirmed_by = WebUser[confirmed_by_username]

    return True


def confirm_debt(t_id, confirmed_by_username):
    t = Transaction[t_id]

    t.confirmed_by = WebUser[confirmed_by_username]

    return True


def confirm_contributions(t_id, confirmed_by_username):
    t = Transaction[t_id]
    share = t.share_ref
    periods = select(c.contribution_period for c in t.contribution_index)[:]

    for period in periods:
        if period in select(c.contribution_period for c in Contribution
                            if c.transaction_ref.share_ref == share
                               and c.transaction_ref.confirmed_by and not c.transaction_ref.deleted_by)[:]:
            raise DuplicateContributionPeriod(get_translation()['exceptions']['duplicate_contribution_period'])

    t.confirmed_by = WebUser[confirmed_by_username]

    return True


def confirm_payment(t_id, confirmed_by_username):
    t = Transaction[t_id]
    p = t.payment_ref
    d = p.debt_ref

    if t.amount > d.remaining_debt:  # If new paid amount is bigger than remaining amount of the debt
        raise Overpayment(get_translation()['exceptions']['overpayment'])

    # update_values_to_confirm_payment
    p.payment_number_of_debt = count(select(p for p in Payment if p.debt_ref == d and
                                            p.transaction_ref.confirmed_by and not p.transaction_ref.deleted_by))
    p.paid_debt_so_far = d.paid_debt + t.amount
    p.paid_installment_so_far = int(p.paid_debt_so_far / d.installment_amount)
    p.remaining_debt_so_far = d.remaining_debt - t.amount
    p.remaining_installment_so_far = d.number_of_installment - p.paid_installment_so_far

    d.paid_debt = p.paid_debt_so_far
    d.paid_installment = p.paid_installment_so_far
    d.remaining_debt = p.remaining_debt_so_far
    d.remaining_installment = p.remaining_installment_so_far

    # Confirm
    t.confirmed_by = WebUser[confirmed_by_username]

    return True
