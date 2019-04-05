from datetime import date

from flask import flash
from pony.orm import db_session, count, select

from database.dbinit import (Debt, Transaction, Share, DebtType, Payment, Contribution, WebUser, Sandik,
                             MemberAuthorityType, Member,)
from views.transaction.auxiliary import Period


@db_session
def insert_debt(in_date, amount, share_id, type_id, explanation, num_of_inst):
    ia = amount / num_of_inst
    ia = int(ia) if ia % 1 == 0 else int(ia) + 1
    Debt(
        transaction_ref=Transaction(
            share_ref=Share[share_id], transaction_date=in_date, amount=amount, type='Debt',
            explanation=explanation),
        debt_type_ref=DebtType[type_id], number_of_installment=num_of_inst, installment_amount=ia,
        paid_debt=0, paid_installment=0, remaining_debt=amount, remaining_installment=num_of_inst,
        starting_period=Period.last_period(in_date, 1), due_period=Period.last_period(in_date, num_of_inst + 1))


@db_session
def insert_payment(in_date, amount, explanation, debt_id=None, transaction_id=None):
    debt = Debt[debt_id] if debt_id else Debt.get(transaction_ref=Transaction[transaction_id])
    share = debt.transaction_ref.share_ref

    # Final controls
    # TODO Kontrolleri excception ile yap, hata mesajını fonksiyonun kullanıldığı yerde ver
    if amount > debt.remaining_debt:  # If new paid amount is bigger than remaining amount of the debt
        flash(u"Paid amount cannot be more than the remaining debt", 'danger')
        return False
    else:  # There is no problem
        pnod = count(select(p for p in Payment if p.debt_ref == debt))
        pdsf = debt.paid_debt + amount
        pisf = int(pdsf / debt.installment_amount)
        rdsf = debt.remaining_debt - amount
        risf = debt.number_of_installment - pisf
        Payment(debt_ref=debt, payment_number_of_debt=pnod, paid_debt_so_far=pdsf, paid_installment_so_far=pisf,
                remaining_debt_so_far=rdsf, remaining_installment_so_far=risf,
                transaction_ref=Transaction(share_ref=share, transaction_date=in_date, amount=amount,
                                            type='Payment', explanation=explanation
                                            )
                )
        debt.paid_debt = pdsf
        debt.paid_installment = pisf
        debt.remaining_debt = rdsf
        debt.remaining_installment = risf
        return True


# TODO flash yerine exception kullan, fonksiyonun kullanıdığı yerlerde exceptionları yakalayarak flash ile gerekli
#  mesajı yazdır
@db_session
def insert_contribution(in_date: date, amount, share_id, explanation, periods: list, is_from_import_data=False):
    share = Share[share_id]
    # TODO Conribution_amount değerini sandık kurallarından al
    contribution_amount = 25

    # TODO bu geçici çözümü kaldırıp import-data daki satırları düzenle ya da hatalı veri tablosu için yeni fonksiyon ekle
    if not is_from_import_data:
        if amount % contribution_amount:
            flash(u"Paid amount must be divided by 25.", 'danger')
            return False
        elif amount/contribution_amount != len(periods):
            flash(u"Paid amount must be 25 * <number_of_months>.", 'danger')
            flash(u"Fakat başlangıç aidatı sistemi yapılana kadar işlem eklendi.", 'danger')
            # return False

    transaction_ref = Transaction(share_ref=share, transaction_date=in_date,
                                  amount=amount, type='Contribution', explanation=explanation)

    contributions = []
    for period in periods:
        contributions.append(Contribution(transaction_ref=transaction_ref, contribution_period=period))
    return contributions


@db_session
def insert_transaction(in_date, amount, share_id, explanation):
    Transaction(share_ref=Share[share_id], transaction_date=in_date, amount=amount,
                type='Other', explanation=explanation)


@db_session
def insert_webuser(username, password_hash, date_of_registration: date=date.today(), name=None, surname=None,
                   is_admin=False,  is_active=True):
    return WebUser(username=username, password_hash=password_hash, date_of_registration=date_of_registration, name=name,
                   surname=surname, is_active=is_active, is_admin=is_admin)


@db_session
def insert_member(username, sandik_id, authority_id, date_of_membership: date=date.today(), is_active=True):
    sandik = Sandik[sandik_id]

    # TODO Use exception
    if sandik.members_index.select(lambda m: m.webuser_ref.username == username).count() > 0:
        return None
    elif date_of_membership < sandik.date_of_opening:
        return None

    return Member(webuser_ref=WebUser[username], sandik_ref=Sandik[sandik_id],
                  member_authority_type_ref=MemberAuthorityType[authority_id], date_of_membership=date_of_membership,
                  is_active=is_active)


@db_session
def insert_share(member_id, date_of_opening: date=date.today(), is_active=True, share_order_of_member=None):
    member = Member[member_id]

    # TODO Use exception
    if date_of_opening < member.date_of_membership:
        return None

    if not share_order_of_member:
        if member.shares_index:
            share_order_of_member = max(select(s.share_order_of_member for s in member.shares_index)) + 1
        else:
            share_order_of_member = 1

    return Share(member_ref=member, share_order_of_member=share_order_of_member, date_of_opening=date_of_opening,
                 is_active=is_active)
