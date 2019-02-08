import logging
import os

from squid_py import OceanKeeperContractsNotFound
from squid_py.agreements.service_types import ACCESS_SERVICE_TEMPLATE_ID
from squid_py.config_provider import ConfigProvider
from squid_py.keeper import Keeper
from squid_py.keeper.contract_handler import ContractHandler

logger = logging.getLogger(__name__)


class Diagnostics:
    @staticmethod
    def check_deployed_agreement_templates():
        keeper = Keeper.get_instance()
        # Check for known service agreement templates
        template_owner = keeper.service_agreement.get_template_owner(ACCESS_SERVICE_TEMPLATE_ID)
        if not template_owner or template_owner == 0:
            logging.info(f'The `Access` Service agreement template {ACCESS_SERVICE_TEMPLATE_ID} is '
                         f'not deployed to the current keeper network.')
        else:
            logging.info(f'Found service agreement template {ACCESS_SERVICE_TEMPLATE_ID} of type '
                         f'`Access` deployed in the current keeper network published by '
                         f'{template_owner}.')

    @staticmethod
    def verify_contracts():
        artifacts_path = ConfigProvider.get_config().keeper_path
        logger.info(f'Keeper contract artifacts (JSON abi files) at: {artifacts_path}')

        if os.environ.get('KEEPER_NETWORK_NAME'):
            logger.warning(f'The `KEEPER_NETWORK_NAME` env var is set to '
                           f'{os.environ.get("KEEPER_NETWORK_NAME")}. '
                           f'This enables the user to override the method of how the network name '
                           f'is inferred from network id.')
        # try to find contract with this network name
        contract_name = 'ServiceExecutionAgreement'
        network_id = Keeper.get_network_id()
        network_name = Keeper.get_network_name(network_id)
        logger.info(f'Using keeper contracts from network {network_name}, '
                    f'network id is {network_id}')
        logger.info(f'Looking for keeper contracts ending with ".{network_name}.json", '
                    f'e.g. "{contract_name}.{network_name}.json".')
        existing_contract_names = os.listdir(artifacts_path)
        try:
            ContractHandler.get(contract_name)
        except Exception as e:
            logger.error(e)
            logger.error(f'Cannot find the keeper contracts. \n'
                         f'Current network id is {network_id} and network name is {network_name}.'
                         f'Expected to find contracts ending with ".{network_name}.json",'
                         f' e.g. "{contract_name}.{network_name}.json"')
            raise OceanKeeperContractsNotFound(
                f'Keeper contracts for keeper network {network_name} were not found '
                f'in {artifacts_path}. \n'
                f'Found the following contracts: \n\t{existing_contract_names}'
            )

        keeper = Keeper.get_instance()
        contracts = [keeper.dispenser, keeper.token, keeper.did_registry,
                     keeper.service_agreement, keeper.payment_conditions, keeper.access_conditions]
        addresses = '\n'.join([f'\t{c.name}: {c.address}' for c in contracts])
        logging.info('Finished loading keeper contracts:\n'
                     '%s', addresses)
