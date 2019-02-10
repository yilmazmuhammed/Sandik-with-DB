from flask import flash
from pony.orm import count, select

from database.dbinit import Transaction, Share, Contribution, Debt, Payment, DebtType
from forms import ContributionForm
from views.transaction.auxiliary import Period


def add_transaction(form):
    # Add the transaction to database
    Transaction(share_ref=Share[form.share.data], transaction_date=form.transaction_date.data,
                amount=form.amount.data, type='other', explanation=form.explanation.data)


def add_contribution(form: ContributionForm):
    # TODO kontrolleri yap
    # TODO Çoklu aidat ödemesi için ayrı bir ekleme yap
    # Add the transaction of contribution to database
    Contribution(
        transaction_ref=Transaction(
            share_ref=Share[form.share.data], transaction_date=form.transaction_date.data, amount=25,
            type='contribution', explanation=form.explanation.data),
        contribution_period=form.contribution_period.data)


def add_debt(form):
    # TODO kontrolleri yap, (borcu varsa bir daha alamaz[sayfaya giriş de engellenebilir], en fazla taksit,
    #  parasına göre en fazla borç)

    # Add the transaction of debt to database
    t_date = form.transaction_date.data
    t_amount = form.amount.data
    d_inst = form.number_of_installment.data
    ia = t_amount / d_inst
    ia = int(ia) if ia % 1 == 0 else int(ia)+1
    Debt(
        transaction_ref=Transaction(
            share_ref=Share[form.share.data], transaction_date=t_date, amount=t_amount, type='debt',
            explanation=form.explanation.data),
        debt_type_ref=DebtType[form.debt_type.data], number_of_installment=d_inst, installment_amount=ia,
        paid_debt=0, paid_installment=0, remaining_debt=t_amount, remaining_installment=d_inst,
        starting_period=Period.last_period(t_date, 1), due_period=Period.last_period(t_date, d_inst + 1))


def add_payment(form):
    # Get values
    amount = form.amount.data
    debt = Debt[form.debt.data]
    print(debt.installment_amount, debt.number_of_installment)
    share = debt.transaction_ref.share_ref
    t_date = form.transaction_date.data
    expl = form.explanation.data

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
                transaction_ref=Transaction(share_ref=share, transaction_date=t_date, amount=amount,
                                            type='payment', explanation=expl
                                            )
                )
        debt.paid_debt = pdsf
        debt.paid_installment = pisf
        debt.remaining_debt = rdsf
        debt.remaining_installment = risf
        return True