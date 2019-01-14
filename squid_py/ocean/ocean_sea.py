import json
import logging
import os
import os.path

from squid_py.brizo.brizo_provider import BrizoProvider
from squid_py.did import DID, did_to_id
from squid_py.exceptions import (
    OceanInvalidServiceAgreementSignature,
    OceanServiceAgreementExists,
)
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.secret_store.secret_store_provider import SecretStoreProvider
from squid_py.service_agreement.register_service_agreement import register_service_agreement
from squid_py.service_agreement.service_agreement import ServiceAgreement
from squid_py.service_agreement.service_types import ServiceTypes
from squid_py.utils.utilities import (get_metadata_url, prepare_prefixed_hash)

logger = logging.getLogger('ocean')


class OceanSea:
    def __init__(self, ocean):
        self._ocean = ocean

    def purchase_asset_service(self, did, service_definition_id, consumer_account):
        """
        Sign service agreement.

        Sign the service agreement defined in the service section identified
        by `service_definition_id` in the ddo and send the signed agreement to the purchase endpoint
        associated with this service.

        :param did: str starting with the prefix `did:op:` and followed by the asset id which is
        a hex str
        :param service_definition_id: str the service definition id identifying a specific
        service in the DDO (DID document)
        :param consumer_account: ethereum address of consumer signing the agreement and
        initiating a purchase/access transaction
        :return: tuple(agreement_id, signature) the service agreement id (can be used to query
            the keeper-contracts for the status of the service agreement) and signed agreement hash
        """
        assert consumer_account.address in self._ocean._accounts, f'Unrecognized consumer address ' \
            f'consumer_account'

        agreement_id = ServiceAgreement.create_new_agreement_id()
        ddo = self._ocean.assets.resolve_did(did)
        service_agreement = ServiceAgreement.from_ddo(service_definition_id, ddo)
        try:
            service_agreement.validate_conditions()
        except AssertionError:
            self._ocean._log_conditions_data(service_agreement)
            raise

        if not consumer_account.unlock():
            logger.warning(f'Unlock of consumer account failed {consumer_account.address}')

        agreement_hash = service_agreement.get_service_agreement_hash(agreement_id)
        signature = consumer_account.sign_hash(agreement_hash)

        service_def = ddo.find_service_by_id(service_definition_id).as_dictionary()
        # Must approve token transfer for this purchase
        self._approve_token_transfer(service_agreement.get_price(), consumer_account)
        # subscribe to events related to this service_agreement_id before sending the request.
        logger.debug(f'Registering service agreement with id: {agreement_id}')
        register_service_agreement(self._ocean.config.storage_path,
                                   consumer_account,
                                   agreement_id,
                                   did,
                                   service_def,
                                   'consumer',
                                   service_definition_id,
                                   service_agreement.get_price(),
                                   get_metadata_url(ddo),
                                   self.consume_service, 0)

        BrizoProvider.get_brizo().initialize_service_agreement(
            did, agreement_id, service_definition_id, signature, consumer_account.address,
            service_agreement.purchase_endpoint
        )
        return agreement_id

    def execute_service_agreement(self, did, service_definition_id, service_agreement_id,
                                  service_agreement_signature, consumer_address, publisher_account):
        """
        Execute the service agreement on-chain using keeper's ServiceAgreement contract.

        The on-chain executeAgreement method requires the following arguments:
        templateId, signature, consumer, hashes, timeouts, serviceAgreementId, did.
        `agreement_message_hash` is necessary to verify the signature.
        The consumer `signature` includes the conditions timeouts and parameters values which
        is usedon-chain to verify that the values actually match the signed hashes.

        :param did: str representation fo the asset DID. Use this to retrieve the asset DDO.
        :param service_definition_id: int identifies the specific service in
         the ddo to use in this agreement.
        :param service_agreement_id: 32 bytes identifier created by the consumer and will be used
         on-chain for the executed agreement.
        :param service_agreement_signature: str the signed agreement message hash which includes
         conditions and their parameters values and other details of the agreement.
        :param consumer_address: ethereum account address of consumer
        :param publisher_account: ethereum account address of publisher
        :return: dict the `executeAgreement` transaction receipt
        """
        assert consumer_address and Web3Provider.get_web3().isChecksumAddress(
            consumer_address), f'Invalid consumer address {consumer_address}'
        assert publisher_account.address in self._ocean._accounts, \
            f'Unrecognized publisher address {publisher_account.address}'
        asset_id = did_to_id(did)
        ddo = self._ocean.resolve_asset_did(did)
        service_agreement = ServiceAgreement.from_ddo(service_definition_id, ddo)
        try:
            service_agreement.validate_conditions()
        except AssertionError:
            self._ocean._log_conditions_data(service_agreement)
            raise

        service_def = ddo.find_service_by_id(service_definition_id).as_dictionary()

        content_urls = get_metadata_url(ddo)
        # Raise error if agreement is already executed
        if self._ocean._keeper.service_agreement.get_service_agreement_consumer(
                service_agreement_id) is not None:
            raise OceanServiceAgreementExists(
                f'Service agreement {service_agreement_id} is already executed.')

        if not self._verify_service_agreement_signature(
                did, service_agreement_id, service_definition_id,
                consumer_address, service_agreement_signature, ddo=ddo
        ):
            raise OceanInvalidServiceAgreementSignature(
                f'Verifying consumer signature failed: '
                f'signature {service_agreement_signature}, '
                f'consumerAddress {consumer_address}'
            )

        # subscribe to events related to this service_agreement_id
        register_service_agreement(self._ocean.config.storage_path,
                                   publisher_account,
                                   service_agreement_id, did, service_def, 'publisher',
                                   service_definition_id,
                                   service_agreement.get_price(), content_urls, None, 0)

        receipt = self._ocean._keeper.service_agreement.execute_service_agreement(
            service_agreement.template_id,
            service_agreement_signature,
            consumer_address,
            service_agreement.conditions_params_value_hashes,
            service_agreement.conditions_timeouts,
            service_agreement_id,
            asset_id,
            publisher_account
        )
        logger.info(f'Service agreement {service_agreement_id} executed successfully.')
        return receipt

    def is_access_granted(self, service_agreement_id, did, consumer_address):
        """
        Check permission for the agreement.

        Verify on-chain that the `consumer_address` has permission to access the given asset `did`
        according to the `service_agreement_id`.

        :param service_agreement_id: str
        :param did: DID, str
        :param consumer_address: Account address, str
        :return: bool True if user has permission
        """
        agreement_consumer = self._ocean._keeper.service_agreement.get_service_agreement_consumer(
            service_agreement_id)
        if agreement_consumer != consumer_address:
            logger.warning(f'Invalid consumer address {consumer_address} and/or '
                           f'service agreement id {service_agreement_id} (did {did})')
            return False

        document_id = did_to_id(did)
        return self._ocean._keeper.access_conditions.check_permissions(consumer_address, document_id)

    def _verify_service_agreement_signature(self, did, service_agreement_id, service_definition_id,
                                            consumer_address, signature,
                                            ddo=None):
        """
        Verify service agreement signature.

        Verify that the given signature is truly signed by the `consumer_address`
        and represents this did's service agreement..

        :param did: DID, str
        :param service_agreement_id: str
        :param service_definition_id: int
        :param consumer_address: Account address, str
        :param signature: Signature, str
        :param ddo: DDO
        :return: True if signature is legitimate, False otherwise
        :raises: ValueError if service is not found in the ddo
        :raises: AssertionError if conditions keys do not match the on-chain conditions keys
        """
        if not ddo:
            ddo = self._ocean.resolve_asset_did(did)

        service_agreement = ServiceAgreement.from_ddo(service_definition_id, ddo)
        try:
            service_agreement.validate_conditions()
        except AssertionError:
            self._ocean._log_conditions_data(service_agreement)
            raise

        agreement_hash = service_agreement.get_service_agreement_hash(service_agreement_id)
        prefixed_hash = prepare_prefixed_hash(agreement_hash)
        recovered_address = Web3Provider.get_web3().eth.account.recoverHash(
            prefixed_hash, signature=signature
        )
        is_valid = (recovered_address == consumer_address)
        if not is_valid:
            logger.warning(f'Agreement signature failed: agreement hash is {agreement_hash.hex()}')

        return is_valid

    def consume_service(self, service_agreement_id, did, service_definition_id, consumer_account):
        """
        Consume the asset data.

        Using the service endpoint defined in the ddo's service pointed to by service_definition_id.
        Consumer's permissions is checked implicitly by the secret-store during decryption
        of the contentUrls.
        The service endpoint is expected to also verify the consumer's permissions to consume this
        asset.
        This method downloads and saves the asset datafiles to disk.

        :param service_agreement_id: str
        :param did: DID, str
        :param service_definition_id: int
        :param consumer_account: Account address, str
        :return: None
        """
        ddo = self._ocean.resolve_asset_did(did)

        metadata_service = ddo.get_service(service_type=ServiceTypes.METADATA)
        content_urls = metadata_service.get_values()['metadata']['base']['contentUrls']
        content_urls = content_urls if isinstance(content_urls, str) else content_urls[0]
        sa = ServiceAgreement.from_ddo(service_definition_id, ddo)
        service_url = sa.service_endpoint
        if not service_url:
            logger.error(
                'Consume asset failed, service definition is missing the "serviceEndpoint".')
            raise AssertionError(
                'Consume asset failed, service definition is missing the "serviceEndpoint".')

        # decrypt the contentUrls
        decrypted_content_urls = json.loads(
            SecretStoreProvider.get_secret_store().decrypt_document(did_to_id(did), content_urls)
        )
        if isinstance(decrypted_content_urls, str):
            decrypted_content_urls = [decrypted_content_urls]
        logger.debug(f'got decrypted contentUrls: {decrypted_content_urls}')

        asset_folder = self._ocean._get_asset_folder_path(did, service_definition_id)
        if not os.path.exists(self._ocean._downloads_path):
            os.mkdir(self._ocean._downloads_path)
        if not os.path.exists(asset_folder):
            os.mkdir(asset_folder)

        BrizoProvider.get_brizo().consume_service(
            service_agreement_id, service_url, consumer_account.address, decrypted_content_urls,
            asset_folder)

    def _get_asset_folder_path(self, did, service_definition_id):
        """

        :param did:
        :param service_definition_id:
        :return:
        """
        return os.path.join(self._ocean._downloads_path,
                            f'datafile.{did_to_id(did)}.{service_definition_id}')