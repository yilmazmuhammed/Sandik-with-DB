class RemoveShareError(Exception):
    pass


class OutstandingDebt(RemoveShareError):
    pass


class RemoveTransactionError(Exception):
    pass


class RemovePaymentError(RemoveTransactionError):
    pass


class RemoveDebtError(RemoveTransactionError):
    pass


class NotLastPayment(RemovePaymentError):
    pass


class ThereIsPayment(RemoveDebtError):
    pass


class DeletedTransaction(RemoveTransactionError):
    pass


class ConfirmTransactionError(Exception):
    pass


class NegativeTransaction(ConfirmTransactionError):
    pass


class DuplicateContributionPeriod(ConfirmTransactionError):
    pass


class Overpayment(ConfirmTransactionError):
    pass


class ThereIsNotSandik(Exception):
    pass


class ThereIsNotMember(Exception):
    pass


class ThereIsNotShare(Exception):
    pass
