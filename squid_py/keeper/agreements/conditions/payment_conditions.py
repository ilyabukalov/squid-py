"""
    Keeper module to transact/call `PaymentConditions` keeper contract methods.
"""

from squid_py.keeper.contract_base import ContractBase


class PaymentConditions(ContractBase):
    """
    Class representing the PaymentConditions contract.
    """

    @staticmethod
    def get_instance():
        """Returns a ContractBase instance of the PaymentConditions contract."""
        return PaymentConditions('PaymentConditions')
