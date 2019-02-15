import copy
import json
import logging
import os

from squid_py.agreements.service_factory import ServiceDescriptor, ServiceFactory
from squid_py.agreements.service_types import ACCESS_SERVICE_TEMPLATE_ID, ServiceTypes
from squid_py.agreements.utils import (
    make_public_key_and_authentication,
)
from squid_py.aquarius.aquarius_provider import AquariusProvider
from squid_py.aquarius.exceptions import AquariusGenericError
from squid_py.brizo.brizo_provider import BrizoProvider
from squid_py.ddo.ddo import DDO
from squid_py.ddo.metadata import Metadata, MetadataBase
from squid_py.ddo.public_key_rsa import PUBLIC_KEY_TYPE_RSA
from squid_py.did import DID, did_to_id
from squid_py.exceptions import (
    OceanDIDAlreadyExist,
    OceanInvalidMetadata,
)
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.secret_store.secret_store_provider import SecretStoreProvider

logger = logging.getLogger('ocean')


class OceanAssets:
    def __init__(self, keeper, did_resolver, agreements, asset_consumer, config):
        self._keeper = keeper
        self._did_resolver = did_resolver
        self._agreements = agreements
        self._asset_consumer = asset_consumer
        self._config = config
        self._aquarius_url = config.aquarius_url

        downloads_path = os.path.join(os.getcwd(), 'downloads')
        if self._config.has_option('resources', 'downloads.path'):
            downloads_path = self._config.get('resources', 'downloads.path') or downloads_path
        self._downloads_path = downloads_path

    def _get_aquarius(self, url=None):
        return AquariusProvider.get_aquarius(url or self._aquarius_url)

    def _get_secret_store(self, account):
        return SecretStoreProvider.get_secret_store(
            self._config.secret_store_url, self._config.parity_url, account
        )

    def create(self, metadata, publisher_account, service_descriptors=None):
        """
        Register an asset in both the keeper's DIDRegistry (on-chain) and in the Metadata store (
        Aquarius).

        :param metadata: dict conforming to the Metadata accepted by Ocean Protocol.
        :param publisher_account: Account of the publisher registering this asset
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
        metadata_copy = copy.deepcopy(metadata)

        # Create a DDO object
        did = DID.did()
        logger.debug(f'Generating new did: {did}')
        # Check if it's already registered first!
        if did in self._get_aquarius().list_assets():
            raise OceanDIDAlreadyExist(
                f'Asset id {did} is already registered to another asset.')

        ddo = DDO(did)

        # Add public key and authentication
        self._keeper.unlock_account(publisher_account)
        pub_key, auth = make_public_key_and_authentication(did, publisher_account.address,
                                                           Web3Provider.get_web3())
        ddo.add_public_key(pub_key)
        ddo.add_authentication(auth, PUBLIC_KEY_TYPE_RSA)

        priv_key = ddo.add_signature()
        ddo.add_proof(1, priv_key)

        # Setup metadata service
        # First replace `files` with encrypted `files`
        assert metadata_copy['base'][
            'files'], 'files is required in the metadata base attributes.'
        assert Metadata.validate(metadata), 'metadata seems invalid.'
        logger.debug('Encrypting content urls in the metadata.')
        files_encrypted = self._get_secret_store(publisher_account) \
            .encrypt_document(
            did_to_id(did),
            json.dumps(metadata_copy['base']['files']),
        )

        metadata_copy['base']['checksum'] = ddo.generate_checksum(did, metadata)

        # only assign if the encryption worked
        if files_encrypted:
            logger.info(f'Content urls encrypted successfully {files_encrypted}')
            del metadata_copy['base']['files']
            metadata_copy['base']['encryptedFiles'] = files_encrypted
        else:
            raise AssertionError('Encrypting the files failed. Make sure the secret store is'
                                 ' setup properly in your config file.')

        # DDO url and `Metadata` service
        ddo_service_endpoint = self._get_aquarius().get_service_endpoint(did)
        metadata_service_desc = ServiceDescriptor.metadata_service_descriptor(metadata_copy,
                                                                              ddo_service_endpoint)
        if not service_descriptors:
            service_descriptors = [ServiceDescriptor.authorization_service_descriptor(
                self._config.secret_store_url)]
            brizo = BrizoProvider.get_brizo()
            service_descriptors += [ServiceDescriptor.access_service_descriptor(
                metadata[MetadataBase.KEY]['price'],
                brizo.get_purchase_endpoint(self._config),
                brizo.get_service_endpoint(self._config),
                3600,
                ACCESS_SERVICE_TEMPLATE_ID
            )]
        else:
            service_types = set(map(lambda x: x[0], service_descriptors))
            if ServiceTypes.AUTHORIZATION not in service_types:
                service_descriptors += [ServiceDescriptor.authorization_service_descriptor(
                    self._config.secret_store_url)]
            else:
                brizo = BrizoProvider.get_brizo()
                service_descriptors += [ServiceDescriptor.access_service_descriptor(
                    metadata[MetadataBase.KEY]['price'],
                    brizo.get_purchase_endpoint(self._config),
                    brizo.get_service_endpoint(self._config),
                    3600,
                    ACCESS_SERVICE_TEMPLATE_ID
                )]

        # Add all services to ddo
        service_descriptors = service_descriptors + [metadata_service_desc]
        for service in ServiceFactory.build_services(did, service_descriptors):
            ddo.add_service(service)

        logger.debug(
            f'Generated ddo and services, DID is {ddo.did},'
            f' metadata service @{ddo_service_endpoint}, '
            f'`Access` service purchase @{ddo.services[0].endpoints.service}.')
        response = None
        try:
            # publish the new ddo in ocean-db/Aquarius
            response = self._get_aquarius().publish_asset_ddo(ddo)
            logger.debug('Asset/ddo published successfully in aquarius.')
        except ValueError as ve:
            raise ValueError(f'Invalid value to publish in the metadata: {str(ve)}')
        except Exception as e:
            logger.error(f'Publish asset in aquarius failed: {str(e)}')

        if not response:
            return None

        # register on-chain
        self._keeper.unlock_account(publisher_account)
        self._keeper.did_registry.register(
            did,
            checksum=Web3Provider.get_web3().sha3(text=metadata_copy['base']['checksum']),
            url=ddo_service_endpoint,
            account=publisher_account
        )
        logger.info(f'DDO with DID {did} successfully registered on chain.')
        return ddo

    def retire(self, did):
        try:
            ddo = self.resolve(did)
            metadata_service = ddo.find_service_by_type(ServiceTypes.METADATA)
            self._get_aquarius(metadata_service.endpoints.service).retire_asset_ddo(did)
            return True
        except AquariusGenericError as err:
            logger.error(err)
            return False

    def resolve(self, did):
        """
        When you pass a did retrieve the ddo associated.

        :param did: DID, str
        :return: DDO instance
        """
        return self._did_resolver.resolve(did)

    def search(self, text, sort=None, offset=100, page=0, aquarius_url=None):
        """
        Search an asset in oceanDB using aquarius.

        :param text: String with the value that you are searching
        :param sort: Dictionary to choose order base in some value
        :param offset: Number of elements shows by page
        :param page: Page number
        :param aquarius_url: Url of the aquarius where you want to search. If there is not
            provided take the default
        :return: List of assets that match with the query
        """
        logger.info(f'Searching asset containing: {text}')
        return [DDO(dictionary=ddo_dict) for ddo_dict in
                self._get_aquarius(aquarius_url).text_search(text, sort, offset, page)]

    def query(self, query, aquarius_url=None):
        """
        Search an asset in oceanDB using search query.

        :param query: dict with query parameters
            (e.g.) {"offset": 100, "page": 0, "sort": {"value": 1},
                    query: {"service:{$elemMatch:{"metadata": {$exists : true}}}}}
                    Here, OceanDB instance of mongodb can leverage power of mongo queries in
                    'query' attribute.
                    For more info -
                    https://docs.mongodb.com/manual/reference/method/db.collection.find
        :param aquarius_url: Url of the aquarius where you want to search. If there is not
            provided take the default
        :return: List of assets that match with the query.
        """
        logger.info(f'Searching asset query: {query}')
        aquarius = self._get_aquarius(aquarius_url)
        return [DDO(dictionary=ddo_dict) for ddo_dict in aquarius.query_search(query)]

    def order(self, did, service_definition_id, consumer_account):
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
        assert consumer_account.address in self._keeper.accounts, f'Unrecognized consumer ' \
            f'address `consumer_account`'

        agreement_id, signature = self._agreements.prepare(
            did, service_definition_id, consumer_account
        )
        self._agreements.send(did, agreement_id, service_definition_id, signature, consumer_account)
        return agreement_id

    def consume(
            self,
            service_agreement_id,
            did,
            service_definition_id,
            consumer_account,
            destination
    ):
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
        :param service_definition_id: str
        :param consumer_account: Account address, str
        :param destination: str path
        :return: str path to saved files
        """
        ddo = self.resolve(did)
        return self._asset_consumer.download(
            service_agreement_id,
            service_definition_id,
            ddo,
            consumer_account,
            destination,
            BrizoProvider.get_brizo(),
            self._get_secret_store(consumer_account)
        )
