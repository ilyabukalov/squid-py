"""
    Keeper module to call keeper-contracts.
"""

import logging
import os

from squid_py.config_provider import ConfigProvider
from squid_py.keeper.conditions.access_conditions import AccessConditions
from squid_py.keeper.conditions.payment_conditions import PaymentConditions
from squid_py.keeper.didregistry import DIDRegistry
from squid_py.keeper.dispenser import Dispenser
from squid_py.keeper.service_execution_agreement import ServiceExecutionAgreement
from squid_py.keeper.token import Token
from squid_py.keeper.web3_provider import Web3Provider


class Keeper(object):
    """
    The Keeper class aggregates all contracts in the Ocean Protocol node.
    Currently this is implemented as a singleton.

    """

    DEFAULT_NETWORK_NAME = 'development'
    _network_name_map = {
        1: 'Main',
        2: 'Morden',
        3: 'Ropsten',
        4: 'Rinkeby',
        42: 'Kovan',
        77: 'POA_Sokol',
        99: 'POA_Core',
        8995: 'nile',
        8996: 'spree',
    }
    _instance = None
    artifacts_path = None
    accounts = []
    dispenser = None
    auth = None
    token = None
    did_registry = None
    service_agreement = None
    payment_conditions = None
    access_conditions = None

    @staticmethod
    def get_instance():
        """Return the Keeper instance (singleton)."""
        if Keeper._instance is None:
            Keeper._instance = Keeper()

            Keeper.network_name = Keeper.get_network_name(Keeper.get_network_id())
            Keeper.artifacts_path = ConfigProvider.get_config().keeper_path
            Keeper.accounts = Web3Provider.get_web3().eth.accounts

            # The contract objects
            Keeper.dispenser = Dispenser.get_instance()
            Keeper.token = Token.get_instance()
            Keeper.did_registry = DIDRegistry.get_instance()
            Keeper.service_agreement = ServiceExecutionAgreement.get_instance()
            Keeper.payment_conditions = PaymentConditions.get_instance()
            Keeper.access_conditions = AccessConditions.get_instance()

        return Keeper._instance

    @staticmethod
    def get_network_name(network_id):
        """
        Return the keeper network name based on the current ethereum network id.
        Return `development` for every network id that is not mapped.

        :return: Network name, str
        """
        if os.environ.get('KEEPER_NETWORK_NAME'):
            logging.debug('keeper network name overridden by an environment variable: {}'.format(
                os.environ.get('KEEPER_NETWORK_NAME')))
            return os.environ.get('KEEPER_NETWORK_NAME')

        return Keeper._network_name_map.get(network_id, Keeper.DEFAULT_NETWORK_NAME)

    @staticmethod
    def get_network_id():
        """
        Return the ethereum network id calling the `web3.version.network` method.

        :return: Network id, int
        """
        return int(Web3Provider.get_web3().version.network)

    @staticmethod
    def sign_hash(msg_hash, account):
        return Web3Provider.get_web3().eth.sign(account.address, msg_hash).hex()

    @staticmethod
    def unlock_account(account):
        return Web3Provider.get_web3().personal.unlockAccount(account.address, account.password)

    @staticmethod
    def get_ether_balance(address):
        return Web3Provider.get_web3().eth.getBalance(address, block_identifier='latest')

    @staticmethod
    def get_token_balance(address):
        return Keeper.token.get_token_balance(address)
