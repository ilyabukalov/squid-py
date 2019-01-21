"""Keeper module to call keeper-contracts."""
import logging

from web3 import Web3

from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.exceptions import OceanDIDNotFound, OceanInvalidTransaction
from squid_py.keeper.contract_base import ContractBase


class Dispenser(ContractBase):
    """Class representing the Dispenser contract."""

    @staticmethod
    def get_instance():
        """Returns a ContractBase instance of the Dispenser contract."""
        return Dispenser('Dispenser')

    def request_tokens(self, amount, address):
        """
        Request an amount of tokens for a particular address.
        This transanction has gas cost

        :param amount: Amount of tokens, int
        :param address: Account address, str
        :raise OceanInvalidTransaction: Transaction failed
        :return: Tx receipt
        """
        try:
            receipt = self.contract_concise.requestTokens(amount, transact={'from': address})
            logging.debug(f'{address} requests {amount} tokens, returning receipt')
            return receipt
        except ValueError:
            raise OceanInvalidTransaction(f'Transaction on chain requesting {amount} tokens'
                                          f' to {address} failed.')
