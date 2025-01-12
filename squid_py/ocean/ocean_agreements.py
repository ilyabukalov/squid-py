"""Ocean module."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from ocean_keeper.utils import add_ethereum_prefix_and_hash_msg
from ocean_keeper.web3_provider import Web3Provider
from ocean_utils.agreements.service_agreement import ServiceAgreement
from ocean_utils.agreements.service_types import ServiceTypes
from ocean_utils.did import did_to_id
from ocean_utils.exceptions import (
    OceanInvalidAgreementTemplate,
    OceanInvalidServiceAgreementSignature,
    OceanServiceAgreementExists,
)

from squid_py.agreement_events.accessSecretStore import consume_asset, refund_reward
from squid_py.agreement_events.computeExecution import execute_computation
from squid_py.agreement_events.escrowAccessSecretStoreTemplate import fulfillLockRewardCondition
from squid_py.brizo.brizo_provider import BrizoProvider
from squid_py.ocean.ocean_conditions import OceanConditions

logger = logging.getLogger('ocean')


class OceanAgreements:
    """Ocean agreements class."""

    def __init__(self, keeper, asset_resolver, asset_consumer, asset_executor, config):
        self._keeper = keeper
        self._asset_resolver = asset_resolver
        self._asset_consumer = asset_consumer
        self._asset_executor = asset_executor
        self._config = config
        self.conditions = OceanConditions(self._keeper)

    def get(self, agreement_id):
        """
        Retrieve the agreement data of agreement_id.

        :param agreement_id: id of the agreement, hex str
        :return: AgreementValues instance -- a namedtuple with the following attributes:

            did,
            owner,
            template_id,
            condition_ids,
            updated_by,
            block_number_updated

        """
        return self._keeper.agreement_manager.get_agreement(agreement_id)

    @staticmethod
    def new():
        return ServiceAgreement.create_new_agreement_id()

    def sign(self, agreement_id, did, consumer_account, service_index):
        """
        Sign a service agreement.

        :param agreement_id: 32 bytes identifier created by the consumer and will be used
         on-chain for the executed agreement.
        :param did: str representation fo the asset DID. Use this to retrieve the asset DDO.
        :param consumer_account: Account instance of the consumer
        :param service_index: int identifies the specific service in
         the ddo to use in this agreement.
        :return: signature
        """
        asset = self._asset_resolver.resolve(did)
        service_agreement = asset.get_service_by_index(service_index)

        publisher_address = self._keeper.did_registry.get_did_owner(asset.asset_id)
        agreement_hash = service_agreement.get_service_agreement_hash(
            agreement_id, asset.asset_id, consumer_account.address, publisher_address, self._keeper
        )
        signature = self._keeper.sign_hash(add_ethereum_prefix_and_hash_msg(agreement_hash),
                                           consumer_account)
        address = self._keeper.personal_ec_recover(agreement_hash, signature)
        assert address == consumer_account.address
        logger.debug(f'agreement-signature={signature}, agreement-hash={agreement_hash}')
        return signature

    def prepare(self, did, consumer_account, service_index):
        """

        :param did: str representation fo the asset DID. Use this to retrieve the asset DDO.
        :param consumer_account: Account instance of the consumer
        :param service_index: int identifies the specific service in
         the ddo to use in this agreement.
        :return: tuple (agreement_id: str, signature: hex str)
        """
        agreement_id = self.new()
        signature = self.sign(agreement_id, did, consumer_account, service_index)
        return agreement_id, signature

    def send(self, did, agreement_id, service_index, signature,
             consumer_account, auto_consume=False):
        """
        Send a signed service agreement to the publisher Brizo instance to
        consume/access the service.

        :param did: str representation fo the asset DID. Use this to retrieve the asset DDO.
        :param agreement_id: 32 bytes identifier created by the consumer and will be used
         on-chain for the executed agreement.
        :param service_index: int identifies the specific service in
         the ddo to use in this agreement.
        :param signature: str the signed agreement message hash which includes
         conditions and their parameters values and other details of the agreement.
        :param consumer_account: Account instance of the consumer
        :param auto_consume: boolean tells this function wether to automatically trigger
            consuming the asset upon receiving access permission
        :raises OceanInitializeServiceAgreementError: on failure
        :return: bool
        """
        asset = self._asset_resolver.resolve(did)
        service_agreement = asset.get_service_by_index(service_index)
        # subscribe to events related to this agreement_id before sending the request.
        logger.debug(
            f'Registering service agreement with id: {agreement_id}, auto-consume {auto_consume}')
        # TODO: refactor this to use same code in `create`

        publisher_address = self._keeper.did_registry.get_did_owner(asset.asset_id)
        condition_ids = service_agreement.generate_agreement_condition_ids(
            agreement_id, asset.asset_id, consumer_account.address, publisher_address, self._keeper)
        from_block = Web3Provider.get_web3().eth.blockNumber
        self._process_consumer_agreement_events(
            agreement_id, did, service_agreement, consumer_account,
            condition_ids, publisher_address,
            from_block, auto_consume
        )

        return BrizoProvider.get_brizo().initialize_service_agreement(
            did,
            agreement_id,
            service_index,
            signature,
            consumer_account.address,
            service_agreement.endpoints.purchase
        )

    def create(self, did, index, agreement_id,
               service_agreement_signature, consumer_address,
               account, auto_consume=False):
        """
        Execute the service agreement on-chain using keeper's ServiceAgreement contract.

        The on-chain executeAgreement method requires the following arguments:
        templateId, signature, consumer, hashes, timeouts, serviceAgreementId, did.
        `agreement_message_hash` is necessary to verify the signature.
        The consumer `signature` includes the conditions timeouts and parameters values which
        is usedon-chain to verify that the values actually match the signed hashes.

        :param did: str representation fo the asset DID. Use this to retrieve the asset DDO.
        :param index: str identifies the specific service in
         the ddo to use in this agreement.
        :param agreement_id: 32 bytes identifier created by the consumer and will be used
         on-chain for the executed agreement.
        :param service_agreement_signature: str the signed agreement message hash which includes
         conditions and their parameters values and other details of the agreement.
        :param consumer_address: ethereum account address of consumer, hex str
        :param account: Account instance creating the agreement. Can be either the
            consumer, publisher or provider
        :param auto_consume: bool
        :return: dict the `executeAgreement` transaction receipt
        """
        assert consumer_address and Web3Provider.get_web3().isChecksumAddress(
            consumer_address), f'Invalid consumer address {consumer_address}'
        assert account.address in self._keeper.accounts, \
            f'Unrecognized account address {account.address}'

        agreement_template_approved = self._keeper.template_manager.is_template_approved(
            self._keeper.escrow_access_secretstore_template.address)
        agreement_exec_template_approved = self._keeper.template_manager.is_template_approved(
            self._keeper.escrow_compute_execution_template.address)
        if not agreement_template_approved:
            msg = (f'The EscrowAccessSecretStoreTemplate contract at address '
                   f'{self._keeper.escrow_access_secretstore_template.address} is not '
                   f'approved and cannot be used for creating service agreements.')
            logger.warning(msg)
            raise OceanInvalidAgreementTemplate(msg)
        if not agreement_exec_template_approved:
            msg = (f'The EscroComputeExecutionTemplate contract at address '
                   f'{self._keeper.agreement_exec_template_approved.address} is not '
                   f'approved and cannot be used for creating service agreements.')
            logger.warning(msg)
            raise OceanInvalidAgreementTemplate(msg)

        asset = self._asset_resolver.resolve(did)
        asset_id = asset.asset_id
        service_agreement = asset.get_service_by_index(index)
        if service_agreement.type == ServiceTypes.ASSET_ACCESS:
            agreement_template = self._keeper.escrow_access_secretstore_template
        elif service_agreement.type == ServiceTypes.CLOUD_COMPUTE:
            agreement_template = self._keeper.escrow_compute_execution_template
        else:
            raise Exception('The agreement could not be created. Review the index of your service.')

        if agreement_template.get_agreement_consumer(agreement_id) is not None:
            raise OceanServiceAgreementExists(
                f'Service agreement {agreement_id} already exists, cannot reuse '
                f'the same agreement id.')

        if consumer_address != account.address:
            if not self._verify_service_agreement_signature(
                    did, agreement_id, index,
                    consumer_address, service_agreement_signature,
                    ddo=asset
            ):
                raise OceanInvalidServiceAgreementSignature(
                    f'Verifying consumer signature failed: '
                    f'signature {service_agreement_signature}, '
                    f'consumerAddress {consumer_address}'
                )

        publisher_address = Web3Provider.get_web3().toChecksumAddress(asset.publisher)
        condition_ids = service_agreement.generate_agreement_condition_ids(
            agreement_id, asset_id, consumer_address, publisher_address, self._keeper)

        time_locks = service_agreement.conditions_timelocks
        time_outs = service_agreement.conditions_timeouts
        success = agreement_template.create_agreement(
            agreement_id,
            asset_id,
            condition_ids,
            time_locks,
            time_outs,
            consumer_address,
            account
        )
        ## TODO CHECK THIS FOR THE OTHER TEMPLATE
        if not success:
            # success is based on tx receipt which is not reliable.
            # So we check on-chain directly to see if agreement_id is there
            consumer = self._keeper.escrow_access_secretstore_template.get_agreement_consumer(
                agreement_id)
            if consumer:
                success = True
            else:
                event_log = self._keeper.escrow_access_secretstore_template \
                    .subscribe_agreement_created(
                    agreement_id, 15, None, (), wait=True
                )
                success = event_log is not None

        if success:
            logger.info(f'Service agreement {agreement_id} created successfully.')
        else:
            logger.info(f'Create agreement "{agreement_id}" failed.')
            self._log_agreement_info(
                asset, service_agreement, agreement_id, service_agreement_signature,
                consumer_address, account, condition_ids
            )

        if success:
            # subscribe to events related to this agreement_id
            if consumer_address == account.address:
                from_block = Web3Provider.get_web3().eth.blockNumber - 10
                self._process_consumer_agreement_events(
                    agreement_id, did, service_agreement, account,
                    condition_ids, publisher_address,
                    from_block, auto_consume, service_agreement.type
                )

        return success

    def _process_consumer_agreement_events(
            self, agreement_id, did, service_agreement, account,
            condition_ids, publisher_address, from_block, auto_consume, agreement_type):
        logger.debug(
            f'process consumer events for agreement {agreement_id}, blockNumber {from_block + 10}')
        if agreement_type == ServiceTypes.ASSET_ACCESS:
            self._keeper.escrow_access_secretstore_template.subscribe_agreement_created(
                agreement_id,
                300,
                fulfillLockRewardCondition,
                (agreement_id, service_agreement.get_price(), account, condition_ids[1]),
                from_block=from_block
            )
        else:
            self._keeper.escrow_compute_execution_template.subscribe_agreement_created(
                agreement_id,
                300,
                fulfillLockRewardCondition,
                (agreement_id, service_agreement.get_price(), account, condition_ids[1]),
                from_block=from_block
            )

        if auto_consume:
            def _refund_callback(_price, _publisher_address, _condition_ids):
                def do_refund(_event, _agreement_id, _did, _service_agreement, _consumer_account,
                              *_):
                    refund_reward(
                        _event, _agreement_id, _did, _service_agreement, _price,
                        _consumer_account, _publisher_address, _condition_ids, _condition_ids[2]
                    )

                return do_refund

            conditions_dict = service_agreement.condition_by_name
            if agreement_type == ServiceTypes.ASSET_ACCESS:
                self._keeper.access_secret_store_condition.subscribe_condition_fulfilled(
                    agreement_id,
                    max(conditions_dict['accessSecretStore'].timeout, 300),
                    consume_asset,
                    (agreement_id, did, service_agreement, account, self._asset_consumer.download,
                     self._config.secret_store_url, self._config.parity_url,
                     self._config.downloads_path),
                    timeout_callback=_refund_callback(
                        service_agreement.get_price(), publisher_address, condition_ids
                    ),
                    from_block=from_block
                )
            else:
                self._keeper.compute_execution_condition.subscribe_condition_fulfilled(
                    agreement_id,
                    max(conditions_dict['execCompute'].timeout, 300),
                    execute_computation,
                    (agreement_id, did, service_agreement, account, self._asset_executor.execute),
                    timeout_callback=_refund_callback(
                        service_agreement.get_price(), publisher_address, condition_ids
                    ),
                    from_block=from_block
                )

    def _log_agreement_info(self, asset, service_agreement, agreement_id, agreement_signature,
                            consumer_address, publisher_account, condition_ids):
        agreement_hash = service_agreement.get_service_agreement_hash(
            agreement_id, asset.asset_id, consumer_address, publisher_account.address, self._keeper)
        publisher_ether_balance = self._keeper.get_ether_balance(publisher_account.address)
        logger.debug(
            f'Agreement parameters:'
            f'\n  agreement id: {agreement_id}'
            f'\n  consumer address: {consumer_address}'
            f'\n  publisher address: {publisher_account.address}'
            f'\n  conditions ids: {condition_ids}'
            f'\n  asset did: {asset.did}'
            f'\n  agreement signature: {agreement_signature}'
            f'\n  agreement hash: {agreement_hash}'
            f'\n  EscrowAccessSecretStoreTemplate: '
            f'{self._keeper.escrow_access_secretstore_template.address}'
            f'\n  publisher ether balance: {publisher_ether_balance}'
        )

    def is_access_granted(self, agreement_id, did, consumer_address):
        """
        Check permission for the agreement.

        Verify on-chain that the `consumer_address` has permission to access the given asset `did`
        according to the `agreement_id`.

        :param agreement_id: id of the agreement, hex str
        :param did: DID, str
        :param consumer_address: ethereum account address of consumer, hex str
        :return: bool True if user has permission
        """
        agreement_consumer = self._keeper.escrow_access_secretstore_template.get_agreement_consumer(
            agreement_id)

        if agreement_consumer is None:
            return False

        if agreement_consumer != consumer_address:
            logger.warning(f'Invalid consumer address {consumer_address} and/or '
                           f'service agreement id {agreement_id} (did {did})'
                           f', agreement consumer is {agreement_consumer}')
            return False

        document_id = did_to_id(did)
        return self._keeper.access_secret_store_condition.check_permissions(
            document_id, consumer_address
        )

    def _verify_service_agreement_signature(self, did, agreement_id, service_index,
                                            consumer_address, signature, ddo=None):
        """
        Verify service agreement signature.

        Verify that the given signature is truly signed by the `consumer_address`
        and represents this did's service agreement..

        :param did: DID, str
        :param agreement_id: id of the agreement, hex str
        :param service_index: identifier of the service inside the asset DDO, str
        :param consumer_address: ethereum account address of consumer, hex str
        :param signature: Signature, str
        :param ddo: DDO instance
        :return: True if signature is legitimate, False otherwise
        :raises: ValueError if service is not found in the ddo
        :raises: AssertionError if conditions keys do not match the on-chain conditions keys
        """
        if not ddo:
            ddo = self._asset_resolver.resolve(did)

        service_agreement = ddo.get_service_by_index(service_index)
        agreement_hash = service_agreement.get_service_agreement_hash(
            agreement_id, ddo.asset_id, consumer_address,
            Web3Provider.get_web3().toChecksumAddress(ddo.proof['creator']), self._keeper)

        recovered_address = self._keeper.personal_ec_recover(agreement_hash, signature)
        is_valid = (recovered_address == consumer_address)
        if not is_valid:
            logger.warning(f'Agreement signature failed: agreement hash is {agreement_hash.hex()}')

        return is_valid

    def _approve_token_transfer(self, amount, consumer_account):
        if self._keeper.token.get_token_balance(consumer_account.address) < amount:
            raise ValueError(
                f'Account {consumer_account.address} does not have sufficient tokens '
                f'to approve for transfer.')

        self._keeper.token.token_approve(self._keeper.payment_conditions.address, amount,
                                         consumer_account)

    def status(self, agreement_id):
        """
        Get the status of a service agreement.

        :param agreement_id: id of the agreement, hex str
        :return: dict with condition status of each of the agreement's conditions or None if the
        agreement is invalid.
        """
        condition_ids = self._keeper.agreement_manager.get_agreement(agreement_id).condition_ids
        result = {"agreementId": agreement_id}
        conditions = dict()
        for i in condition_ids:
            conditions[self._keeper.get_condition_name_by_address(
                self._keeper.condition_manager.get_condition(
                    i).type_ref)] = self._keeper.condition_manager.get_condition_state(i)
        result["conditions"] = conditions
        return result
