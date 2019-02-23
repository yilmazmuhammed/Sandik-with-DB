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
    # TODO bu geçici çözümü kaldırıp import-data daki satırları düzenle ya da hatalı veri tablosu için yeni fonksiyon ekle
    if not is_from_import_data:
        if amount % 25:
            flash(u"Paid amount must be divided by 25.", 'danger')
            return False
        elif amount/25 != len(periods):
            flash(u"Paid amount must be 25 * <number_of_months>.", 'danger')
            return False

    share = Share[share_id]

    # # TODO hata dönüyor, işlemi de eklemiyor, ama bu ayları ödeme listesinden siliyor
    # for period in periods:
    #     if period in select(c.contribution_period for c in Contribution if c.transaction_ref.share_ref == share)[:]:
    #         flash(u"Daha önce ödenmiş aidat tekrar ödenemez.", 'danger')
    #         return False

    transaction_ref = Transaction(share_ref=share, transaction_date=in_date,
                                  amount=amount, type='Contribution', explanation=explanation)
    for period in periods:
        Contribution(transaction_ref=transaction_ref, contribution_period=period)
    return True


@db_session
def insert_transaction(in_date, amount, share_id, explanation):
    Transaction(share_ref=Share[share_id], transaction_date=in_date, amount=amount,
                type='Other', explanation=explanation)


@db_session
def insert_member(webuser_id, sandik_id, authority_id, date_of_membership: date):
    return Member(webuser_ref=WebUser[webuser_id], sandik_ref=Sandik[sandik_id],
                  member_authority_type_ref=MemberAuthorityType[authority_id], date_of_membership=date_of_membership)


@db_session
def insert_share(member_id, date_of_opening: date):
    member = Member[member_id]
    soom = member.shares_index.count() + 1
    Share(member_ref=member, share_order_of_member=soom, date_of_opening=date_of_opening)
