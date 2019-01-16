import json
import logging
import os

from web3.contract import ConciseContract

from squid_py.keeper import Keeper
from squid_py.keeper.web3_provider import Web3Provider

logger = logging.getLogger(__name__)


class ContractHandler(object):
    """
    Manages loading contracts and also keeps a cache of loaded contracts.

    Retrieval of deployed keeper contracts must use this `ContractHandler`.
    Example:
        contract = ContractHandler.get('ServiceAgreement')
        concise_contract = ContractHandler.get_concise_contract('ServiceAgreement')

    """
    _contracts = dict()

    @staticmethod
    def get(name):
        return (ContractHandler._contracts.get(name) or ContractHandler._load(name))[0]

    @staticmethod
    def get_concise_contract(name):
        return (ContractHandler._contracts.get(name) or ContractHandler._load(name))[1]

    @staticmethod
    def set(name, contract):
        ContractHandler._contracts[name] = (contract, ConciseContract(contract))

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
        ContractHandler._contracts[contract_name] = (contract, ConciseContract(contract))
        return ContractHandler._contracts[contract_name]

    @staticmethod
    def get_contract_dict_by_name(contract_name):
        """

        :param contract_name:
        :return: dict -- the smart contract's definition from the json abi file
        """
        keeper = Keeper.get_instance()
        network_name = keeper.get_network_name(keeper.get_network_id()).lower()

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
            raise FileNotFoundError(
                'Keeper contract {} file not found: {}'.format(contract_name, path))

        with open(path) as f:
            contract_dict = json.loads(f.read())
            return contract_dict
