from flask import flash
from pony.orm import db_session, count, select

from database.dbinit import Debt, Transaction, Share, DebtType, Payment, Contribution
from views.transaction import Period


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


@db_session
def insert_contribution(in_date, amount, share_id, explanation, periods):
    transaction_ref = Transaction(share_ref=Share[share_id], transaction_date=in_date,
                                  amount=amount, type='Contribution', explanation=explanation)
    period_list = periods.split(" ")
    for period in period_list:
        Contribution(transaction_ref=transaction_ref, contribution_period=period)


@db_session
def insert_transaction(in_date, amount, share_id, explanation):
    Transaction(share_ref=Share[share_id], transaction_date=in_date, amount=amount,
                type='Other', explanation=explanation)
