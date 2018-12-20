"""Keeper module to call keeper-contracts."""

from squid_py.keeper.contract_base import ContractBase


class PaymentConditions(ContractBase):
    """Class representing the PaymentConditions contract."""

    def __init__(self, web3, contract_path):
        """
        Initialize PaymentConditions class.

        :param web3: Web3 instance
        :param contract_path: Contract path, str
        """
        super().__init__(web3, contract_path, 'PaymentConditions')
