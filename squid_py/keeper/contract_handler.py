import json
import logging
import os

from squid_py.config_provider import ConfigProvider
from squid_py.exceptions import OceanKeeperContractsNotFound
from squid_py.keeper import Keeper
from squid_py.keeper.web3_provider import Web3Provider

logger = logging.getLogger(__name__)


class ContractHandler(object):
    _contracts = dict()

    @staticmethod
    def verify_contracts():
        web3 = Web3Provider.get_web3()
        artifacts_path = ConfigProvider.get_config().keeper_path
        network_id = int(web3.version.network)
        logger.info("Keeper contract artifacts (JSON abi files) at: %s", artifacts_path)

        if os.environ.get('KEEPER_NETWORK_NAME'):
            logger.warning(
                'The `KEEPER_NETWORK_NAME` env var is set to %s. This enables the user to '
                'override the method of how the network name is inferred from network id.',
                os.environ.get('KEEPER_NETWORK_NAME'))

        # try to find contract with this network name
        contract_name = 'ServiceAgreement'
        network_name = Keeper.get_network_name()
        logger.info('Using keeper contracts from network `%s`, network id is %s',
                    network_name, network_id)
        logger.info('Looking for keeper contracts ending with ".%s.json", e.g. "%s.%s.json"',
                    network_name, contract_name, network_name)
        existing_contract_names = os.listdir(artifacts_path)
        try:
            ContractHandler.get(contract_name)
        except Exception as e:
            logger.error(e)
            logger.error('Cannot find the keeper contracts. \n'
                         '\tCurrent network id is "%s" and network name is "%s"\n'
                         '\tExpected to find contracts ending with ".%s.json", e.g. "%s.%s.json"',
                         network_id, network_name, network_name, contract_name,
                         network_name)
            raise OceanKeeperContractsNotFound(
                'Keeper contracts for keeper network "%s" were not found in "%s". \n'
                'Found the following contracts: \n\t%s' % (
                    network_name, artifacts_path, existing_contract_names)
            )

        keeper = Keeper.get_instance()
        contracts = [keeper.market, keeper.auth, keeper.token, keeper.did_registry,
                     keeper.service_agreement, keeper.payment_conditions, keeper.access_conditions]
        addresses = '\n'.join(['\t{}: {}'.format(c.name, c.address) for c in contracts])
        logging.info('Finished loading keeper contracts:\n'
                     '%s', addresses)

    @staticmethod
    def get(name):
        return ContractHandler._contracts.get(name) or ContractHandler._load(name)

    @staticmethod
    def set(name, contract):
        ContractHandler._contracts[name] = contract

    @staticmethod
    def has(name):
        return name in ContractHandler._contracts

    @staticmethod
    def _load(contract_name):
        """Retrieve the contract instance for `contract_name` that represent the smart
        contract in the keeper network.

        :param contract_name: str name of the solidity keeper contract without the network name.
        :return: web3.eth.Contract instance
        """
        contract_definition = ContractHandler.get_contract_dict_by_name(contract_name)
        address = Web3Provider.get_web3().toChecksumAddress(contract_definition['address'])
        abi = contract_definition['abi']
        contract = Web3Provider.get_web3().eth.contract(address=address, abi=abi)
        ContractHandler._contracts[contract_name] = contract
        return ContractHandler._contracts[contract_name]

    @staticmethod
    def get_contract_dict_by_name(contract_name):
        """

        :param contract_name:
        :return: dict -- the smart contract's definition from the json abi file
        """
        keeper = Keeper.get_instance()
        network_name = keeper.get_network_name().lower()

        file_name = '{}.{}.json'.format(contract_name, network_name)
        path = os.path.join(keeper.artifacts_path, file_name)
        if not os.path.exists(path):
            file_name = '{}.{}.json'.format(contract_name, network_name.lower())
            for name in os.listdir(keeper.artifacts_path):
                if name.lower() == file_name.lower():
                    file_name = name
                    path = os.path.join(keeper.artifacts_path, file_name)
                    break

        if not os.path.exists(path):
            raise FileNotFoundError('Keeper contract {} file not found: {}'.format(contract_name, path))

        with open(path) as f:
            contract = json.loads(f.read())
            return contract
