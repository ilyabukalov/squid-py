"""Keeper module to call keeper-contracts."""
import logging

from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.exceptions import OceanInvalidTransaction
from squid_py.keeper.contract_base import ContractBase
from squid_py.keeper.web3_provider import Web3Provider


class Dispenser(ContractBase):
    """Class representing the Dispenser contract."""

    @staticmethod
    def get_instance():
        """Returns a ContractBase instance of the Dispenser contract."""
        return Dispenser('Dispenser')

    def request_tokens(self, amount, address):
        """
        Request an amount of tokens for a particular address.
        This transaction has gas cost

        :param amount: Amount of tokens, int
        :param address: Account address, str
        :raise OceanInvalidTransaction: Transaction failed
        :return: bool
        """
        try:
            tx_hash = self.contract_concise.requestTokens(amount, transact={'from': address,
                                                                            'gas':
                                                                                DEFAULT_GAS_LIMIT})
            logging.debug(f'{address} requests {amount} tokens, returning receipt')
            receipt = Web3Provider.get_web3().eth.waitForTransactionReceipt(tx_hash)
            logging.debug(f'requestTokens receipt: {receipt}')
            if not receipt:
                return False

            if receipt.status == 0:
                logging.warning(f'request tokens failed: Tx-receipt={receipt}')
                logging.warning(f'request tokens failed: account {address}')
                return False

            # check for emitted events:
            rfe = self.events.RequestFrequencyExceeded().createFilter(
                fromBlock='latest', toBlock='latest', argument_filters={'requester': address}
            )
            logs = rfe.get_all_entries()
            if logs:
                logging.warning(f'request tokens failed RequestFrequencyExceeded')
                logging.info(f'RequestFrequencyExceeded event logs: {logs}')
                return False

            rle = self.events.RequestLimitExceeded().createFilter(
                fromBlock='latest', toBlock='latest', argument_filters={'requester': address}
            )
            logs = rle.get_all_entries()
            if logs:
                logging.warning(f'request tokens failed RequestLimitExceeded')
                logging.info(f'RequestLimitExceeded event logs: {logs}')
                return False

            return True

        except ValueError as err:
            raise OceanInvalidTransaction(
                f'Requesting {amount} tokens'
                f' to {address} failed with error: {err}'
            )
