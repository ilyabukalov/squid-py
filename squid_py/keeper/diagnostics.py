import logging
import os

from squid_py import OceanKeeperContractsNotFound
from squid_py.config_provider import ConfigProvider
from squid_py.keeper.contract_handler import ContractHandler
from squid_py.service_agreement import ACCESS_SERVICE_TEMPLATE_ID
from squid_py.keeper import Keeper

logger = logging.getLogger(__name__)


class Diagnostics:
    @staticmethod
    def check_deployed_agreement_templates():
        keeper = Keeper.get_instance()
        # Check for known service agreement templates
        template_owner = keeper.service_agreement.get_template_owner(ACCESS_SERVICE_TEMPLATE_ID)
        if not template_owner or template_owner == 0:
            logging.info('The `Access` Service agreement template "%s" is not deployed to '
                         'the current keeper network.', ACCESS_SERVICE_TEMPLATE_ID)
        else:
            logging.info('Found service agreement template "%s" of type `Access` deployed in '
                         'the current keeper network published by "%s".',
                         ACCESS_SERVICE_TEMPLATE_ID, template_owner)

    @staticmethod
    def verify_contracts():
        artifacts_path = ConfigProvider.get_config().keeper_path
        logger.info("Keeper contract artifacts (JSON abi files) at: %s", artifacts_path)

        if os.environ.get('KEEPER_NETWORK_NAME'):
            logger.warning(
                'The `KEEPER_NETWORK_NAME` env var is set to %s. This enables the user to '
                'override the method of how the network name is inferred from network id.',
                os.environ.get('KEEPER_NETWORK_NAME'))

        # try to find contract with this network name
        contract_name = 'ServiceAgreement'
        network_id = Keeper.get_network_id()
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
        contracts = [keeper.market, keeper.token, keeper.did_registry,
                     keeper.service_agreement, keeper.payment_conditions, keeper.access_conditions]
        addresses = '\n'.join(['\t{}: {}'.format(c.name, c.address) for c in contracts])
        logging.info('Finished loading keeper contracts:\n'
                     '%s', addresses)

