"""
    Collection of Keeper contracts

"""

import logging
import os

from squid_py.exceptions import OceanKeeperContractsNotFound
from squid_py.keeper.conditions.access_conditions import AccessConditions
from squid_py.keeper.conditions.payment_conditions import PaymentConditions
from squid_py.keeper.service_agreement import ServiceAgreement
from squid_py.keeper.auth import Auth
from squid_py.keeper.didregistry import DIDRegistry
from squid_py.keeper.market import Market
from squid_py.keeper.token import Token
from squid_py.keeper.utils import get_contract_by_name, get_network_id, get_network_name
from squid_py.service_agreement.service_types import ACCESS_SERVICE_TEMPLATE_ID


class Keeper(object):

    def __init__(self, web3, contract_path):
        """
        The Keeper class aggregates all contracts in the Ocean Protocol node

        :param web3: The common web3 object
        :param contract_path: Path for
        :param address_list:
        """

        self.web3 = web3
        self.contract_path = contract_path

        logging.info("Keeper contract artifacts (JSON abi files) at: %s", self.contract_path)

        if os.environ.get('KEEPER_NETWORK_NAME'):
            logging.warning('The `KEEPER_NETWORK_NAME` env var is set to %s. This enables the user to '
                            'override the method of how the network name is inferred from network id.',
                            os.environ.get('KEEPER_NETWORK_NAME'))

        # try to find contract with this network name
        contract_name = 'ServiceAgreement'
        network_name = get_network_name(self.web3)
        logging.info('Using keeper contracts from network `%s`, network id is %s',
                     network_name, get_network_id(self.web3))
        logging.info('Looking for keeper contracts ending with ".%s.json", e.g. "%s.%s.json"',
                     network_name, contract_name, network_name)
        existing_contract_names = os.listdir(contract_path)
        try:
            get_contract_by_name(contract_path, network_name, contract_name)
        except Exception as e:
            logging.error('Cannot find the keeper contracts. \n'
                          '\tCurrent network id is "%s" and network name is "%s"\n'
                          '\tExpected to find contracts ending with ".%s.json", e.g. "%s.%s.json"',
                          get_network_id(self.web3), network_name, network_name, contract_name, network_name)
            raise OceanKeeperContractsNotFound(
                'Keeper contracts for keeper network "%s" were not found in "%s". \n'
                'Found the following contracts: \n\t%s' % (network_name, contract_path, existing_contract_names)
            )

        self.network_name = network_name

        # The contract objects
        self.market = Market(web3, contract_path)
        self.auth = Auth(web3, contract_path)
        self.token = Token(web3, contract_path)
        self.didregistry = DIDRegistry(web3, contract_path)
        self.service_agreement = ServiceAgreement(web3, contract_path)
        self.payment_conditions = PaymentConditions(web3, contract_path)
        self.access_conditions = AccessConditions(web3, contract_path)

        contracts = [self.market, self.auth, self.token, self.didregistry,
                     self.service_agreement, self.payment_conditions, self.access_conditions]
        addresses = '\n'.join(['\t{}: {}'.format(c.name, c.address) for c in contracts])
        logging.info('Finished loading keeper contracts:\n'
                     '%s', addresses)

        # Check for known service agreement templates
        template_owner = self.service_agreement.get_template_owner(ACCESS_SERVICE_TEMPLATE_ID)
        if not template_owner or template_owner == 0:
            logging.info('The `Access` Service agreement template "%s" is not deployed to '
                         'the current keeper network.', ACCESS_SERVICE_TEMPLATE_ID)
        else:
            logging.info('Found service agreement template "%s" of type `Access` deployed in '
                         'the current keeper network published by "%s".', ACCESS_SERVICE_TEMPLATE_ID, template_owner)
