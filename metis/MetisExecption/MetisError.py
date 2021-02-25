# _*_ coding: utf-8 _*_

"""
@author: E.T
@file: MetisError.py
@time: 2020/5/19 3:12 下午
@desc:
"""


class BaseMetisError(Exception):
    """
    Root Exception for metis
    """


class ValidationError(BaseMetisError):
    """
        validation errors for things such as verification, registration, etc.
    """

    def __init__(self, attribute, reason):
        self.attribute = attribute
        self.reason = reason
        super(ValidationError, self).__init__((attribute, reason))


class StopValidation(BaseMetisError):
    """
        validation should end immediately and no further processing should be done
    """

    def __init__(self, reasons):
        self.reasons = reasons
        super(StopValidation, self).__init__(reasons)


class PersistenceError(BaseMetisError):
    """
    To catch down errors when persisting models to the database
    this should be raised from exceptions
    Example:
            try:
                db.session.add(user)
                db.session.commit()
            except Exception:
                error_log()
                raise PersistenceError("Could not save user account")
    """


class EthError(BaseMetisError):
    """
    catch web3 error
    """
    def __init__(self, reason):
        self.reason = reason
        super(EthError, self).__init__(reason)


class FirstClaimPromiseError(BaseMetisError):
    """
    catch first claim promise contract error  raise special mark
    """
    def __init__(self, reason):
        self.reason = reason
        super(FirstClaimPromiseError, self).__init__(reason)


