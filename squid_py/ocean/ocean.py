"""Ocean module."""

import json
import logging
import os
import os.path

from web3 import Web3

from squid_py.config_provider import ConfigProvider
from squid_py.keeper.diagnostics import Diagnostics
from squid_py.ocean.account import Account
from squid_py.ocean.asset import Asset
from squid_py.aquarius import Aquarius
from squid_py.ddo import DDO
from squid_py.ddo.metadata import Metadata
from squid_py.ddo.public_key_rsa import PUBLIC_KEY_TYPE_RSA
from squid_py.keeper import Keeper
from squid_py.log import setup_logging
from squid_py.did_resolver import DIDResolver
from squid_py.exceptions import (
    OceanDIDAlreadyExist,
    OceanInvalidMetadata,
    OceanInvalidServiceAgreementSignature,
    OceanServiceAgreementExists,
)
from squid_py.ocean.brizo import Brizo
from squid_py.ocean.secret_store import SecretStore
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.service_agreement.register_service_agreement import register_service_agreement
from squid_py.service_agreement.service_agreement import ServiceAgreement
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate
from squid_py.service_agreement.service_factory import ServiceFactory, ServiceDescriptor
from squid_py.service_agreement.service_types import ServiceTypes
from squid_py.service_agreement.utils import (
    make_public_key_and_authentication,
    register_service_agreement_template,
    get_conditions_data_from_keeper_contracts,
)
from squid_py.utils.utilities import (
    generate_prefixed_id,
    prepare_prefixed_hash,
    get_metadata_url,
)
from squid_py.did import did_to_id, DID

CONFIG_FILE_ENVIRONMENT_NAME = 'CONFIG_FILE'

setup_logging()
logger = logging.getLogger('ocean')


class Ocean:
    """The Ocean class is the entry point into Ocean Protocol."""

    def __init__(self, config=None):
        """
        Initialize Ocean class.

        This class is an aggregation of
         * the smart contracts via the Keeper class
         * the metadata store
         * and utilities
        Ocean is also a wrapper for the web3.py interface (https://github.com/ethereum/web3.py)
        An instance of Ocean is parameterized by a configuration file.

        :param config: Config instance
        """
        # Configuration information for the market is stored in the Config class
        # config = Config(filename=config_file, options_dict=config_dict)
        if config:
            ConfigProvider.set_config(config)

        self.config = ConfigProvider.get_config()

        # With the interface loaded, the Keeper node is connected with all contracts
        self.keeper = Keeper.get_instance()

        # Add the Metadata store to the interface
        if self.config.aquarius_url:
            self.metadata_store = Aquarius(self.config.aquarius_url)
        else:
            self.metadata_store = None

        downloads_path = os.path.join(os.getcwd(), 'downloads')
        if self.config.has_option('resources', 'downloads.path'):
            downloads_path = self.config.get('resources', 'downloads.path') or downloads_path
        self._downloads_path = downloads_path

        # Collect the accounts
        self.accounts = self.get_accounts()
        assert self.accounts

        parity_address = (
            Web3Provider.get_web3().toChecksumAddress(self.config.parity_address)
            if self.config.parity_address
            else None
        )
        if parity_address and parity_address in self.accounts:
            self.main_account = self.accounts[parity_address]
            self.main_account.password = self.config.parity_password
        else:
            self.main_account = self.accounts[Web3Provider.get_web3().eth.accounts[0]]

        self.did_resolver = DIDResolver(Web3Provider.get_web3(), self.keeper.did_registry)

        # Verify keeper contracts
        Diagnostics.verify_contracts()
        Diagnostics.check_deployed_agreement_templates()

        logger.info('Squid Ocean instance initialized: ')
        logger.info(
            f'\tmain account: {self.main_account.address} '
            f'(is password set? {bool(self.main_account.password)})'
        )
        logger.info(f'\tOther accounts: {sorted(self.accounts)}')
        logger.info(f'\taquarius: {self.metadata_store.url}')
        logger.info(f'\tDIDRegistry @ { self.keeper.did_registry.address}')

        if self.config.secret_store_url and self.config.parity_url and self.main_account:
            logger.info(f'\tSecretStore: url {self.config.secret_store_url}, '
                        f'parity-client {self.config.parity_url}, '
                        f'account {self.config.parity_address}')

    def get_accounts(self):
        """
        Returns all available accounts loaded via a wallet, or by Web3.

        :return: dict of account-address: Account instance
        """
        accounts_dict = dict()
        for account_address in self.keeper.accounts:
            accounts_dict[account_address] = Account(self.keeper, account_address)
        return accounts_dict

    def get_asset(self, asset_did):
        """
        Given an asset_did, return the Asset.

        :param asset_did: Asset did, str
        :return: Asset object
        """
        logger.debug(f'Getting asset with did: {asset_did}')
        return Asset.from_ddo_dict(self.resolve_did(asset_did))

    def search_assets_by_text(self, text, sort=None, offset=100, page=0, aquarius_url=None):
        """
        Search an asset in oceanDB using aquarius.

        :param text: String with the value that you are searching
        :param sort: Dictionary to choose order base in some value
        :param offset: Number of elements shows by page
        :param page: Page number
        :param aquarius_url: Url of the aquarius where you want to search. If there is not provided take the default
        :return: List of assets that match with the query
        """
        logger.info(f'Searching asset containing: {text}')
        if aquarius_url is not None:
            aquarius = Aquarius(aquarius_url)
            return [Asset.from_ddo_dict(i) for i in aquarius.text_search(text, sort, offset, page)]
        else:
            return [Asset.from_ddo_dict(i) for i in
                    self.metadata_store.text_search(text, sort, offset, page)]

    def search_assets(self, query):
        """
        Search an asset in oceanDB using search query.

        :param query: dict with query parameters
            (e.g.) {"offset": 100, "page": 0, "sort": {"value": 1},
                    query: {"service:{$elemMatch:{"metadata": {$exists : true}}}}}
                    Here, OceanDB instance of mongodb can leverage power of mongo queries in 'query' attribute.
                    For more info - https://docs.mongodb.com/manual/reference/method/db.collection.find
        :return: List of assets that match with the query.
        """
        aquarius_url = self.config.aquarius_url
        logger.info(f'Searching asset query: {query}')
        if aquarius_url is not None:
            aquarius = Aquarius(aquarius_url)
            return [Asset.from_ddo_dict(i) for i in aquarius.query_search(query)]
        else:
            return [Asset.from_ddo_dict(i) for i in self.metadata_store.query_search(query)]

    def register_asset(self, metadata, publisher, service_descriptors):
        """
        Register an asset in both the keeper's DIDRegistry (on-chain) and in the Metadata store (Aquarius).

        :param metadata: dict conforming to the Metadata accepted by Ocean Protocol.
        :param publisher: Account of the publisher registering this asset
        :param service_descriptors: list of ServiceDescriptor tuples of length 2.
            The first item must be one of ServiceTypes and the second
            item is a dict of parameters and values required by the service
        :return: DDO instance
        """
        assert isinstance(metadata, dict), f'Expected metadata of type dict, got {type(metadata)}'
        if not metadata or not Metadata.validate(metadata):
            raise OceanInvalidMetadata('Metadata seems invalid. Please make sure'
                                       ' the required metadata values are filled in.')

        # copy metadata so we don't change the original
        metadata_copy = metadata.copy()

        # Create a DDO object
        did = DID().did
        logger.debug(f'Generating new did: {did}')
        # Check if it's already registered first!
        if did in self.metadata_store.list_assets():
            raise OceanDIDAlreadyExist(
                f'Asset id {did} is already registered to another asset.')

        ddo = DDO(did)

        # Add public key and authentication
        publisher.unlock()
        pub_key, auth = make_public_key_and_authentication(did, publisher.address, Web3Provider.get_web3())
        ddo.add_public_key(pub_key)
        ddo.add_authentication(auth, PUBLIC_KEY_TYPE_RSA)

        # Setup metadata service
        # First replace `contentUrls` with encrypted `contentUrls`
        assert metadata_copy['base'][
            'contentUrls'], 'contentUrls is required in the metadata base attributes.'
        assert Metadata.validate(metadata), 'metadata seems invalid.'
        logger.debug('Encrypting content urls in the metadata.')
        content_urls_encrypted = self._encrypt_metadata_content_urls(did,
                                                                     json.dumps(
                                                                         metadata_copy['base'][
                                                                             'contentUrls']))
        # only assign if the encryption worked
        if content_urls_encrypted:
            logger.debug('Content urls encrypted successfully.')
            metadata_copy['base']['contentUrls'] = [content_urls_encrypted]
        else:
            raise AssertionError('Encrypting the contentUrls failed. Make sure the secret store is'
                                 ' setup properly in your config file.')

        # DDO url and `Metadata` service
        ddo_service_endpoint = self.metadata_store.get_service_endpoint(did)
        metadata_service_desc = ServiceDescriptor.metadata_service_descriptor(metadata_copy,
                                                                              ddo_service_endpoint)

        # Add all services to ddo
        _service_descriptors = service_descriptors + [metadata_service_desc]
        for service in ServiceFactory.build_services(Web3Provider.get_web3(), self.keeper.artifacts_path, did,
                                                     _service_descriptors):
            ddo.add_service(service)

        logger.debug(
            f'Generated ddo and services, DID is {ddo.did},'
            f' metadata service @{ddo_service_endpoint}, '
            f'`Access` service purchase @{ddo.services[0].get_values()["purchaseEndpoint"]}.')
        response = None
        try:
            # publish the new ddo in ocean-db/Aquarius
            response = self.metadata_store.publish_asset_ddo(ddo)
            logger.debug('Asset/ddo published successfully in aquarius.')
        except ValueError as ve:
            raise ValueError(f'Invalid value to publish in the metadata: {str(ve)}')
        except Exception as e:
            logger.error(f'Publish asset in aquarius failed: {str(e)}')

        if not response:
            return None

        # register on-chain
        self.keeper.did_registry.register(
            did,
            key=Web3.sha3(text='Metadata'),
            url=ddo_service_endpoint,
            account=publisher
        )
        logger.info(f'DDO with DID {did} successfully registered on chain.')
        return ddo

    def _approve_token_transfer(self, amount):
        if self.keeper.token.get_token_balance(self.main_account.address) < amount:
            raise ValueError(
                f'Account {self.main_account.address} does not have sufficient tokens '
                f'to approve for transfer.')

        self.keeper.token.token_approve(self.keeper.payment_conditions.address, amount,
                                        self.main_account)

    def _get_ddo_and_service_agreement(self, did, service_index):
        """

        :param did:
        :param service_index:
        :return:
        """
        ddo = self.resolve_did(did)
        # Extract all of the params necessary for execute agreement from the ddo
        service = ddo.find_service_by_key_value(ServiceAgreement.SERVICE_DEFINITION_ID_KEY,
                                                service_index)
        if not service:
            raise ValueError(
                f'Service with definition id {service_index} is not found in this DDO.')
        service = service.as_dictionary()
        sa = ServiceAgreement.from_service_dict(service)
        service[ServiceAgreement.SERVICE_CONDITIONS_KEY] = [cond.as_dictionary() for cond in
                                                            sa.conditions]
        return ddo, sa, service

    def _get_service_agreement_to_sign(self, did, service_index):
        """

        :param did:
        :param service_index:
        :return:
        """
        ddo, service_agreement, service_def = self._get_ddo_and_service_agreement(did,
                                                                                  service_index)
        return generate_prefixed_id(), service_agreement, service_def, ddo

    def sign_service_agreement(self, did, service_index, consumer_address):
        """
        Sign service agreement.

        Sign the service agreement defined in the service section identified
        by `service_index` in the ddo and send the signed agreement to the purchase endpoint
        associated with this service.

        :param did: str starting with the prefix `did:op:` and followed by the asset id which is a hex str
        :param service_index: str the service definition id identifying a specific service in the DDO (DID document)
        :param consumer_address: ethereum address of consumer signing the agreement and initiating a purchase/access transaction
        :return: hex str the service agreement id (can be used to query the keeper-contracts for the status of the service agreement)
        """
        assert consumer_address in self.accounts, f'Unrecognized consumer address consumer_address'
        assert consumer_address == self.main_account.address, \
            'consumer address must be already set as the main account in this instance of Ocean.'

        agreement_id, service_agreement, service_def, ddo = self._get_service_agreement_to_sign(did,
                                                                                                service_index)
        if not self.main_account.unlock():
            logger.warning(f'Unlock of consumer account failed {self.main_account.address}')

        signature = service_agreement.get_signed_agreement_hash(agreement_id, self.main_account)[0]

        self._validate_conditions_keys(service_agreement)

        # Must approve token transfer for this purchase
        self._approve_token_transfer(service_agreement.get_price())

        # subscribe to events related to this service_agreement_id before sending the request.
        logger.debug(f'Registering service agreement with id: {agreement_id}')
        register_service_agreement(Web3Provider.get_web3(), self.keeper.artifacts_path, self.config.storage_path,
                                   self.main_account,
                                   agreement_id, did, service_def, 'consumer', service_index,
                                   service_agreement.get_price(), get_metadata_url(ddo),
                                   self.consume_service, 0)

        Brizo.initialize_service_agreement(
            did, agreement_id, service_index, signature, consumer_address,
            service_agreement.purchase_endpoint
        )

        return agreement_id

    def execute_service_agreement(self, did, service_index, service_agreement_id,
                                  service_agreement_signature, consumer_address, publisher_address):
        """
        Execute the service agreement on-chain using keeper's ServiceAgreement contract.

        The on-chain executeAgreement method requires the following arguments:
        templateId, signature, consumer, hashes, timeouts, serviceAgreementId, did.
        `agreement_message_hash` is necessary to verify the signature.
        The consumer `signature` includes the conditions timeouts and parameters values which
        is usedon-chain to verify that the values actually match the signed hashes.

        :param did: str representation fo the asset DID. Use this to retrieve the asset DDO.
        :param service_index: int identifies the specific service in
         the ddo to use in this agreement.
        :param service_agreement_id: 32 bytes identifier created by the consumer and will be used
         on-chain for the executed agreement.
        :param service_agreement_signature: str the signed agreement message hash which includes
         conditions and their parameters values and other details of the agreement.
        :param consumer_address: ethereum account address of consumer
        :param publisher_address: ethereum account address of publisher
        :return: dict the `executeAgreement` transaction receipt
        """
        assert consumer_address and Web3Provider.get_web3().isChecksumAddress(
            consumer_address), 'Invalid consumer address "%s"' % consumer_address
        assert publisher_address and Web3Provider.get_web3().isChecksumAddress(
            publisher_address), 'Invalid publisher address "%s"' % publisher_address
        assert publisher_address in self.accounts, 'Unrecognized publisher address %s' % \
                                                   publisher_address

        asset_id = did_to_id(did)
        ddo, service_agreement, service_def = self._get_ddo_and_service_agreement(did,
                                                                                  service_index)
        content_urls = get_metadata_url(ddo)
        # Raise error if agreement is already executed
        if self.keeper.service_agreement.get_service_agreement_consumer(
                service_agreement_id) is not None:
            raise OceanServiceAgreementExists(
                f'Service agreement {service_agreement_id} is already executed.')

        if not self.verify_service_agreement_signature(
                did, service_agreement_id, service_index,
                consumer_address, service_agreement_signature, ddo=ddo
        ):
            raise OceanInvalidServiceAgreementSignature(
                "Verifying consumer signature failed: signature {}, consumerAddress {}"
                .format(service_agreement_signature, consumer_address)
            )

        # subscribe to events related to this service_agreement_id
        register_service_agreement(Web3Provider.get_web3(), self.keeper.artifacts_path, self.config.storage_path,
                                   self.main_account,
                                   service_agreement_id, did, service_def, 'publisher',
                                   service_index,
                                   service_agreement.get_price(), content_urls, None, 0)

        receipt = self.keeper.service_agreement.execute_service_agreement(
            service_agreement.template_id,
            service_agreement_signature,
            consumer_address,
            service_agreement.conditions_params_value_hashes,
            service_agreement.conditions_timeouts,
            service_agreement_id,
            asset_id,
            self.main_account
        )
        logger.info(f'Service agreement {service_agreement_id} executed successfully.')
        return receipt

    def check_permissions(self, service_agreement_id, did, consumer_address):
        """
        Check permission for the agreement.

        Verify on-chain that the `consumer_address` has permission to access the given asset `did`
        according to the `service_agreement_id`.

        :param service_agreement_id: str
        :param did: DID, str
        :param consumer_address: Account address, str
        :return: bool True if user has permission
        """
        agreement_consumer = self.keeper.service_agreement.get_service_agreement_consumer(
            service_agreement_id)
        if agreement_consumer != consumer_address:
            logger.warning(f'Invalid consumer address {consumer_address} and/or '
                           f'service agreement id {service_agreement_id} (did {did})')
            return False

        document_id = did_to_id(did)
        return self.keeper.access_conditions.check_permissions(consumer_address, document_id,
                                                               self.main_account.address)

    def verify_service_agreement_signature(self, did, service_agreement_id, service_index,
                                           consumer_address, signature,
                                           ddo=None):
        """
        Verify service agreement signature.

        Verify that the given signature is truly signed by the `consumer_address`
        and represents this did's service agreement..

        :param did: DID, str
        :param service_agreement_id: str
        :param service_index: int
        :param consumer_address: Account address, str
        :param signature: Signature, str
        :param ddo: DDO
        :return: True if signature is legitimate, False otherwise
        :raises: ValueError if service is not found in the ddo
        """
        if not ddo:
            ddo = self.resolve_did(did)

        service = ddo.find_service_by_key_value(ServiceAgreement.SERVICE_DEFINITION_ID_KEY,
                                                service_index)
        if not service:
            raise ValueError(
                f'Service with definition id {service_index} is not found in this DDO.')

        service = service.as_dictionary()
        sa = ServiceAgreement.from_service_dict(service)

        agreement_hash = sa.get_service_agreement_hash(
            service_agreement_id
        )
        prefixed_hash = prepare_prefixed_hash(agreement_hash)
        recovered_address = Web3Provider.get_web3().eth.account.recoverHash(prefixed_hash, signature=signature)
        is_valid = (recovered_address == consumer_address)
        if not is_valid:
            logger.warning(f'Agreement signature failed: agreement hash is {agreement_hash.hex()}')

        Ocean._validate_conditions_keys(sa)

        return is_valid

    def _register_service_agreement_template(self, template_dict, owner_account=None):
        if not owner_account:
            owner_account = self.main_account

        sla_template = ServiceAgreementTemplate(template_json=template_dict)
        return register_service_agreement_template(
            self.keeper.service_agreement, self.keeper.artifacts_path, owner_account, sla_template
        )

    def resolve_did(self, did):
        """
        When you pass a did retrieve the ddo associated.

        :param did: DID, str
        :return: DDO
        """
        resolver = self.did_resolver.resolve(did)
        if resolver.is_ddo:
            return self.did_resolver.resolve(did).ddo
        elif resolver.is_url:
            aquarius = Aquarius(resolver.url)
            return DDO(json_text=json.dumps(aquarius.get_asset_ddo(did)))
        else:
            return None

    def _encrypt_metadata_content_urls(self, did, data, threshold=0):
        return SecretStore(
            self.config.secret_store_url, self.config.parity_url, self.main_account
        ).encrypt_document(did_to_id(did), data, threshold)

    def _decrypt_content_urls(self, did, encrypted_data):
        return SecretStore(
            self.config.secret_store_url, self.config.parity_url, self.main_account
        ).decrypt_document(did_to_id(did), encrypted_data)

    def consume_service(self, service_agreement_id, did, service_index, consumer_account):
        """
        Consume the asset data.

        Using the service endpoint defined in the ddo's service pointed to by service_index.
        Consumer's permissions is checked implicitly by the secret-store during decryption
        of the contentUrls.
        The service endpoint is expected to also verify the consumer's permissions to consume this
        asset.
        This method downloads and saves the asset datafiles to disk.

        :param service_agreement_id: str
        :param did: DID, str
        :param service_index: int
        :param consumer_account: Account address, str
        :return: None
        """
        ddo = self.resolve_did(did)

        metadata_service = ddo.get_service(service_type=ServiceTypes.METADATA)
        content_urls = metadata_service.get_values()['metadata']['base']['contentUrls']
        content_urls = content_urls if isinstance(content_urls, str) else content_urls[0]
        service = ddo.find_service_by_key_value(ServiceAgreement.SERVICE_DEFINITION_ID_KEY,
                                                service_index)
        sa = ServiceAgreement.from_service_dict(service.as_dictionary())
        service_url = sa.service_endpoint
        if not service_url:
            logger.error(
                'Consume asset failed, service definition is missing the "serviceEndpoint".')
            raise AssertionError(
                'Consume asset failed, service definition is missing the "serviceEndpoint".')

        # decrypt the contentUrls
        decrypted_content_urls = json.loads(self._decrypt_content_urls(did, content_urls))
        if isinstance(decrypted_content_urls, str):
            decrypted_content_urls = [decrypted_content_urls]
        logger.debug(f'got decrypted contentUrls: {decrypted_content_urls}')

        asset_folder = self.get_asset_folder_path(did, service_index)
        if not os.path.exists(self._downloads_path):
            os.mkdir(self._downloads_path)
        if not os.path.exists(asset_folder):
            os.mkdir(asset_folder)

        Brizo.consume_service(
            service_agreement_id, service_url, consumer_account.address, decrypted_content_urls, asset_folder)

    def get_asset_folder_path(self, did, service_index):
        """

        :param did:
        :param service_index:
        :return:
        """
        return os.path.join(self._downloads_path, f'datafile.{did_to_id(did)}.{service_index}')

    def set_main_account(self, address, password):
        """

        :param address:
        :param password:
        :return:
        """
        self.main_account = Account(self.keeper, Web3Provider.get_web3().toChecksumAddress(address), password)
        Web3Provider.get_web3().eth.defaultAccount = self.main_account.address
        logger.debug('main account set to %s', self.main_account.address)
        if password:
            logger.debug('main account password is also set.')
        else:
            logger.info('main account password is not set,'
                        ' transactions will likely fail if the account is locked.')

    @staticmethod
    def _validate_conditions_keys(sa):
        # Debug info
        # (contract_addresses, fingerprints, fulfillment_indices, conditions_keys)
        values = get_conditions_data_from_keeper_contracts(
            sa.conditions, sa.template_id
        )
        assert values[3] == sa.conditions_keys
        logger.debug(f'conditions keys: {sa.conditions_keys}')
        logger.debug(f'conditions contracts: {values[0]}')
        logger.debug(f'conditions fingerprints: {[fn.hex() for fn in values[1]]}')
        logger.debug(f'template id: {sa.template_id}')
