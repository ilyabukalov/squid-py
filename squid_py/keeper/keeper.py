"""Keeper module to call keeper-contracts."""

import logging
import os

from squid_py.exceptions import OceanKeeperContractsNotFound
from squid_py.keeper.auth import Auth
from squid_py.keeper.conditions.access_conditions import AccessConditions
from squid_py.keeper.conditions.payment_conditions import PaymentConditions
from squid_py.keeper.didregistry import DIDRegistry
from squid_py.keeper.market import Market
from squid_py.keeper.service_agreement import ServiceAgreement
from squid_py.keeper.token import Token
from squid_py.keeper.utils import get_contract_by_name, get_network_id, get_network_name
from squid_py.service_agreement.service_types import ACCESS_SERVICE_TEMPLATE_ID


class Keeper(object):
    """Class that load all the keeper-contracts."""

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
            logging.warning(
                f'The `KEEPER_NETWORK_NAME` env var is set to '
                f'{os.environ.get("KEEPER_NETWORK_NAME")}. This enables the user to '
                f'override the method of how the network name is inferred from network id.')

        # try to find contract with this network name
        contract_name = 'ServiceAgreement'
        network_name = get_network_name(self.web3)
        logging.info(f'Using keeper contracts from network {network_name}, '
                     f'network id is {get_network_id(self.web3)}')
        logging.info(f'Looking for keeper contracts ending with ".{network_name}.json", '
                     f'e.g. "{contract_name}.{network_name}.json"')
        existing_contract_names = os.listdir(contract_path)
        try:
            get_contract_by_name(contract_path, network_name, contract_name)
        except Exception as e:
            logging.error(e)
            logging.error(f'Cannot find the keeper contracts. \n'
                          f'\tCurrent network id is {get_network_id(self.web3)} and network name '
                          f'is {network_name}\n\tExpected to find contracts ending with '
                          f'".{network_name}.json", e.g. "{contract_name}.{network_name}.json"')
            raise OceanKeeperContractsNotFound(
                f'Keeper contracts for keeper network {network_name} were not found '
                f'in {contract_path}. \n'
                f'Found the following contracts: \n\t{existing_contract_names}')

        self.network_name = network_name

        # The contract objects
        self.market = Market(web3, contract_path)
        self.auth = Auth(web3, contract_path)
        self.token = Token(web3, contract_path)
        self.did_registry = DIDRegistry(web3, contract_path)
        self.service_agreement = ServiceAgreement(web3, contract_path)
        self.payment_conditions = PaymentConditions(web3, contract_path)
        self.access_conditions = AccessConditions(web3, contract_path)

        contracts = [self.market, self.auth, self.token, self.did_registry,
                     self.service_agreement, self.payment_conditions, self.access_conditions]
        addresses = '\n'.join([f'\t{c.name}: {c.address}' for c in contracts])
        logging.info(f'Finished loading keeper contracts:\n{addresses}')

        # Check for known service agreement templates
        template_owner = self.service_agreement.get_template_owner(ACCESS_SERVICE_TEMPLATE_ID)
        if not template_owner or template_owner == 0:
            logging.info(f'The `Access` Service agreement template {ACCESS_SERVICE_TEMPLATE_ID} '
                         f'is not deployed to the current keeper network.')
        else:
            logging.info(f'Found service agreement template {ACCESS_SERVICE_TEMPLATE_ID} of type'
                         f' `Access` deployed in the current keeper network '
                         f'published by {template_owner}.')
