"""
    Keeper Contract Base

    All keeper contract inherit from this base class
"""

import logging

from squid_py.keeper.web3_provider import Web3Provider

logger = logging.getLogger('keeper')


class ContractBase(object):
    """Base class for all contract objects."""

    def __init__(self, contract_name, dependencies={}):

        self.name = contract_name

        if 'ContractHandler' not in dependencies:
            from squid_py.keeper.contract_handler import ContractHandler
            dependencies['ContractHandler'] = ContractHandler
        self.contract_concise = dependencies['ContractHandler'].get_concise_contract(contract_name)
        self.contract = dependencies['ContractHandler'].get(contract_name)

        logger.debug(f'Loaded {self}')

    @property
    def _contract_concise(self):
        return self.contract_concise

    @property
    def _contract(self):
        return self.contract

    @property
    def address(self):
        """Return the ethereum address of the solidity contract deployed
        in current keeper network.
        """
        return self._contract.address

    @property
    def events(self):
        """Expose the underlying contract's events.

        :return:
        """
        return self.contract.events

    def to_checksum_address(self, address):
        """
        Validate the address provided.

        :param address:
        :return:
        """
        return Web3Provider.get_web3().toChecksumAddress(address)

    def get_tx_receipt(self, tx_hash):
        """
        Get the receipt of a tx.

        :param tx_hash:
        :return:
        """
        Web3Provider.get_web3().eth.waitForTransactionReceipt(tx_hash)
        return Web3Provider.get_web3().eth.getTransactionReceipt(tx_hash)

    def get_event_signature(self, name):
        """
        Return the event signature from a named event.

        :param name:
        :return:
        """
        signature = None
        for item in self.contract.abi:
            if item.get('type') == 'event' and item.get('name') == name:
                signature = item['signature']
                break

        return signature

    def __str__(self):
        return f'{self.name} at {self.address}'
