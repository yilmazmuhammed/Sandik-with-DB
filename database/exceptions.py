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