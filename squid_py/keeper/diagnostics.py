#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import os

from squid_py import OceanKeeperContractsNotFound
from squid_py.config_provider import ConfigProvider
from squid_py.keeper import Keeper
from squid_py.keeper.contract_handler import ContractHandler

logger = logging.getLogger(__name__)


class Diagnostics:
    TEST_CONTRACT_NAME = 'AgreementStoreManager'

    # @staticmethod
    # def check_approved_agreement_templates():
    #     publisher_acc = get_publisher_account()
    #     keeper = Keeper.get_instance()
    #     template_values = keeper.template_manager.get_template(
    #     keeper.escrow_access_secretstore_template.address)
    #     if not template_values:
    #         print(f'agreement template does not seem to exist in the current keeper-contracts.')
    #
    #     state = template_values.state
    #     if state == 0:
    #         print(f'agreement template is uninitialized')
    #         try:
    #             keeper.template_manager.propose_template(
    #             keeper.escrow_access_secretstore_template.address, publisher_acc)
    #             state = keeper.template_manager.get_template(
    #                 keeper.escrow_access_secretstore_template.address).state
    #         except ValueError as err:
    #             print(f'propose template failed, maybe it is already proposed {err}')
    #             return None
    #
    #     if state == 1:
    #         print(f'agreement template is in proposed state.')
    #         owner_acc = publisher_acc
    #         try:
    #             approved = keeper.template_manager.approve_template(
    #             keeper.escrow_access_secretstore_template.address, owner_acc)
    #             state = keeper.template_manager.get_template(
    #                 keeper.escrow_access_secretstore_template.address).state
    #
    #             print('template approve: ', approved)
    #         except ValueError as err:
    #             print(f'approve template from account {owner_acc.address} failed: {err}')
    #
    #     assert state == 2, 'Template is not approved.'
    #
    #     print(f'agreement template is already approved, good.')

    @staticmethod
    def verify_contracts():
        """
        Verify that the contracts are deployed correctly in the network.

        :raise Exception: raise exception if the contracts are not deployed correctly.
        """
        artifacts_path = ConfigProvider.get_config().keeper_path
        logger.info(f'Keeper contract artifacts (JSON abi files) at: {artifacts_path}')

        if os.environ.get('KEEPER_NETWORK_NAME'):
            logger.warning(f'The `KEEPER_NETWORK_NAME` env var is set to '
                           f'{os.environ.get("KEEPER_NETWORK_NAME")}. '
                           f'This enables the user to override the method of how the network name '
                           f'is inferred from network id.')

        # try to find contract with this network name
        contract_name = Diagnostics.TEST_CONTRACT_NAME
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
                     keeper.agreement_manager, keeper.template_manager, keeper.condition_manager,
                     keeper.access_secret_store_condition, keeper.sign_condition,
                     keeper.lock_reward_condition, keeper.escrow_access_secretstore_template,
                     keeper.escrow_reward_condition, keeper.hash_lock_condition
                     ]
        addresses = '\n'.join([f'\t{c.name}: {c.address}' for c in contracts])
        logging.info('Finished loading keeper contracts:\n'
                     '%s', addresses)
