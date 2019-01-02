"""
    Keeper module to call keeper-contracts.
"""

import logging
import os

from squid_py.config_provider import ConfigProvider
from squid_py.keeper.conditions.access_conditions import AccessConditions
from squid_py.keeper.conditions.payment_conditions import PaymentConditions
from squid_py.keeper.service_agreement import ServiceAgreement
from squid_py.keeper.didregistry import DIDRegistry
from squid_py.keeper.market import Market
from squid_py.keeper.token import Token
from squid_py.keeper.web3_provider import Web3Provider


class Keeper(object):
    """
    The Keeper class aggregates all contracts in the Ocean Protocol node
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
    market = None
    auth = None
    token = None
    did_registry = None
    service_agreement = None
    payment_conditions = None
    access_conditions = None

    @staticmethod
    def get_instance():
        if Keeper._instance is None:
            Keeper._instance = Keeper()

            Keeper.network_name = Keeper.get_network_name()
            Keeper.artifacts_path = ConfigProvider.get_config().keeper_path
            Keeper.accounts = Web3Provider.get_web3().eth.accounts

            # The contract objects
            Keeper.market = Market.get_instance()
            Keeper.token = Token.get_instance()
            Keeper.did_registry = DIDRegistry.get_instance()
            Keeper.service_agreement = ServiceAgreement.get_instance()
            Keeper.payment_conditions = PaymentConditions.get_instance()
            Keeper.access_conditions = AccessConditions.get_instance()

        return Keeper._instance

    @staticmethod
    def get_network_name():
        """
        Return the keeper network name based on the current ethereum network id.

        :return: Network name, str
        """
        if os.environ.get('KEEPER_NETWORK_NAME'):
            logging.debug('keeper network name overridden by an environment variable: {}'.format(
                os.environ.get('KEEPER_NETWORK_NAME')))
            return os.environ.get('KEEPER_NETWORK_NAME')

        web3 = Web3Provider.get_web3()
        return Keeper._network_name_map.get(int(web3.version.network), Keeper.DEFAULT_NETWORK_NAME)
