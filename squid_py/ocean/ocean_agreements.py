import logging

from squid_py.agreements.register_service_agreement import register_service_agreement
from squid_py.agreements.service_agreement import ServiceAgreement
from squid_py.agreements.utils import get_conditions_data_from_keeper_contracts
from squid_py.brizo.brizo_provider import BrizoProvider
from squid_py.did import did_to_id
from squid_py.exceptions import (
    OceanInvalidServiceAgreementSignature,
    OceanServiceAgreementExists,
)
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.utils.utilities import prepare_prefixed_hash

logger = logging.getLogger('ocean')


class OceanAgreements:
    def __init__(self, keeper, asset_resolver, asset_consumer, config):
        self._keeper = keeper
        self._asset_resolver = asset_resolver
        self._asset_consumer = asset_consumer
        self._config = config

    def prepare(self, did, service_definition_id, consumer_account):
        """

        :param did: str representation fo the asset DID. Use this to retrieve the asset DDO.
        :param service_definition_id: str identifies the specific service in
         the ddo to use in this agreement.
        :param consumer_account: ethereum account address of publisher
        :return: tuple (agreement_id: str, signature: hex str)
        """
        agreement_id = ServiceAgreement.create_new_agreement_id()
        asset = self._asset_resolver.resolve(did)
        service_agreement = ServiceAgreement.from_ddo(service_definition_id, asset)
        try:
            service_agreement.validate_conditions()
        except AssertionError:
            OceanAgreements._log_conditions_data(service_agreement)
            raise

        if not self._keeper.unlock_account(consumer_account):
            logger.warning(f'Unlock of consumer account failed {consumer_account.address}')

        agreement_hash = service_agreement.get_service_agreement_hash(agreement_id)
        signature = self._keeper.sign_hash(agreement_hash, consumer_account)

        return agreement_id, signature

    def send(self, did, agreement_id, service_definition_id, signature, consumer_account):
        """
        Send a signed service agreement to the publisher Brizo instance to
        purchase/access the service.

        :param did: str representation fo the asset DID. Use this to retrieve the asset DDO.
        :param agreement_id: 32 bytes identifier created by the consumer and will be used
         on-chain for the executed agreement.
        :param service_definition_id: str identifies the specific service in
         the ddo to use in this agreement.
        :param signature: str the signed agreement message hash which includes
         conditions and their parameters values and other details of the agreement.
        :param consumer_account: ethereum account address of consumer
        :raises OceanInitializeServiceAgreementError: on failure
        :return: bool
        """
        asset = self._asset_resolver.resolve(did)
        service_agreement = ServiceAgreement.from_ddo(service_definition_id, asset)
        service_def = asset.find_service_by_id(service_definition_id).as_dictionary()
        # Must approve token transfer for this purchase
        self._approve_token_transfer(service_agreement.get_price(), consumer_account)
        # subscribe to events related to this agreement_id before sending the request.
        logger.debug(f'Registering service agreement with id: {agreement_id}')
        register_service_agreement(
            self._config.storage_path,
            consumer_account,
            agreement_id,
            did,
            service_def,
            'consumer',
            service_definition_id,
            service_agreement.get_price(),
            asset.encrypted_files,
            self._asset_consumer.download,
            0
        )

        return BrizoProvider.get_brizo().initialize_service_agreement(
            did,
            agreement_id,
            service_definition_id,
            signature,
            consumer_account.address,
            service_agreement.purchase_endpoint
        )

    def create(self, did, service_definition_id, agreement_id,
               service_agreement_signature, consumer_address, publisher_account):
        """
        Execute the service agreement on-chain using keeper's ServiceAgreement contract.

        The on-chain executeAgreement method requires the following arguments:
        templateId, signature, consumer, hashes, timeouts, serviceAgreementId, did.
        `agreement_message_hash` is necessary to verify the signature.
        The consumer `signature` includes the conditions timeouts and parameters values which
        is usedon-chain to verify that the values actually match the signed hashes.

        :param did: str representation fo the asset DID. Use this to retrieve the asset DDO.
        :param service_definition_id: str identifies the specific service in
         the ddo to use in this agreement.
        :param agreement_id: 32 bytes identifier created by the consumer and will be used
         on-chain for the executed agreement.
        :param service_agreement_signature: str the signed agreement message hash which includes
         conditions and their parameters values and other details of the agreement.
        :param consumer_address: ethereum account address of consumer
        :param publisher_account: ethereum account address of publisher
        :return: dict the `executeAgreement` transaction receipt
        """
        assert consumer_address and Web3Provider.get_web3().isChecksumAddress(
            consumer_address), f'Invalid consumer address {consumer_address}'
        assert publisher_account.address in self._keeper.accounts, \
            f'Unrecognized publisher address {publisher_account.address}'
        asset_id = did_to_id(did)
        asset = self._asset_resolver.resolve(did)
        service_agreement = ServiceAgreement.from_ddo(service_definition_id, asset)
        try:
            service_agreement.validate_conditions()
        except AssertionError:
            OceanAgreements._log_conditions_data(service_agreement)
            raise

        service_def = asset.find_service_by_id(service_definition_id).as_dictionary()

        encrypted_files = asset.encrypted_files
        # Raise error if agreement is already executed
        if self._keeper.service_agreement.get_service_agreement_consumer(
                agreement_id) is not None:
            raise OceanServiceAgreementExists(
                f'Service agreement {agreement_id} is already executed.')

        if not self._verify_service_agreement_signature(
                did, agreement_id, service_definition_id,
                consumer_address, service_agreement_signature, ddo=asset
        ):
            raise OceanInvalidServiceAgreementSignature(
                f'Verifying consumer signature failed: '
                f'signature {service_agreement_signature}, '
                f'consumerAddress {consumer_address}'
            )

        # subscribe to events related to this agreement_id
        register_service_agreement(
            self._config.storage_path,
            publisher_account,
            agreement_id,
            did,
            service_def,
            'publisher',
            service_definition_id,
            service_agreement.get_price(),
            encrypted_files,
            None,
            0
        )

        self._keeper.unlock_account(publisher_account)
        receipt = self._keeper.service_agreement.execute_service_agreement(
            service_agreement.template_id,
            service_agreement_signature,
            consumer_address,
            service_agreement.conditions_params_value_hashes,
            service_agreement.conditions_timeouts,
            agreement_id,
            asset_id,
            publisher_account
        )
        logger.info(f'Service agreement {agreement_id} executed successfully.')
        return receipt

    def is_access_granted(self, agreement_id, did, consumer_address):
        """
        Check permission for the agreement.

        Verify on-chain that the `consumer_address` has permission to access the given asset `did`
        according to the `agreement_id`.

        :param agreement_id: str
        :param did: DID, str
        :param consumer_address: Account address, str
        :return: bool True if user has permission
        """
        agreement_consumer = self._keeper.service_agreement.get_service_agreement_consumer(
            agreement_id
        )
        if agreement_consumer != consumer_address:
            logger.warning(f'Invalid consumer address {consumer_address} and/or '
                           f'service agreement id {agreement_id} (did {did})')
            return False

        document_id = did_to_id(did)
        return self._keeper.access_conditions.check_permissions(consumer_address, document_id)

    def _verify_service_agreement_signature(self, did, agreement_id, service_definition_id,
                                            consumer_address, signature,
                                            ddo=None):
        """
        Verify service agreement signature.

        Verify that the given signature is truly signed by the `consumer_address`
        and represents this did's service agreement..

        :param did: DID, str
        :param agreement_id: str
        :param service_definition_id: str
        :param consumer_address: Account address, str
        :param signature: Signature, str
        :param ddo: DDO instance
        :return: True if signature is legitimate, False otherwise
        :raises: ValueError if service is not found in the ddo
        :raises: AssertionError if conditions keys do not match the on-chain conditions keys
        """
        if not ddo:
            ddo = self._asset_resolver.resolve(did)

        service_agreement = ServiceAgreement.from_ddo(service_definition_id, ddo)
        try:
            service_agreement.validate_conditions()
        except AssertionError:
            OceanAgreements._log_conditions_data(service_agreement)
            raise

        agreement_hash = service_agreement.get_service_agreement_hash(agreement_id)
        prefixed_hash = prepare_prefixed_hash(agreement_hash)
        recovered_address = Web3Provider.get_web3().eth.account.recoverHash(
            prefixed_hash, signature=signature
        )
        is_valid = (recovered_address == consumer_address)
        if not is_valid:
            logger.warning(f'Agreement signature failed: agreement hash is {agreement_hash.hex()}')

        return is_valid

    def _approve_token_transfer(self, amount, consumer_account):
        if self._keeper.token.get_token_balance(consumer_account.address) < amount:
            raise ValueError(
                f'Account {consumer_account.address} does not have sufficient tokens '
                f'to approve for transfer.')

        self._keeper.unlock_account(consumer_account)
        self._keeper.token.token_approve(self._keeper.payment_conditions.address, amount,
                                         consumer_account)

    @staticmethod
    def _log_conditions_data(sa):
        # conditions_data = (contract_addresses, fingerprints, fulfillment_indices, conditions_keys)
        conditions_data = get_conditions_data_from_keeper_contracts(
            sa.conditions, sa.template_id
        )
        logger.debug(f'conditions keys: {sa.conditions_keys}')
        logger.debug(f'conditions contracts: {conditions_data[0]}')
        logger.debug(f'conditions fingerprints: {[fn.hex() for fn in conditions_data[1]]}')
        logger.debug(f'template id: {sa.template_id}')
