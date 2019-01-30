import os
import json
import logging

from squid_py import ServiceAgreement
from squid_py.aquarius.aquarius_provider import AquariusProvider
from squid_py.brizo.brizo_provider import BrizoProvider
from squid_py.ddo import DDO
from squid_py.ddo.metadata import Metadata, MetadataBase
from squid_py.ddo.public_key_rsa import PUBLIC_KEY_TYPE_RSA
from squid_py.did import DID, did_to_id
from squid_py.exceptions import (
    OceanDIDAlreadyExist,
    OceanInvalidMetadata,
)
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.secret_store.secret_store_provider import SecretStoreProvider
from squid_py.service_agreement.service_factory import ServiceDescriptor, ServiceFactory
from squid_py.service_agreement.service_types import ACCESS_SERVICE_TEMPLATE_ID, ServiceTypes
from squid_py.service_agreement.utils import (
    make_public_key_and_authentication,
)

logger = logging.getLogger('ocean')


class OceanAssets:
    def __init__(self, keeper, aquarius, did_resolver, agreements, config):
        self._keeper = keeper
        self._aquarius = aquarius
        self._did_resolver = did_resolver
        self._agreements = agreements
        self._config = config

        downloads_path = os.path.join(os.getcwd(), 'downloads')
        if self._config.has_option('resources', 'downloads.path'):
            downloads_path = self._config.get('resources', 'downloads.path') or downloads_path
        self._downloads_path = downloads_path

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
        metadata_copy = metadata.copy()

        # Create a DDO object
        did = DID.did()
        logger.debug(f'Generating new did: {did}')
        # Check if it's already registered first!
        if did in self._aquarius.list_assets():
            raise OceanDIDAlreadyExist(
                f'Asset id {did} is already registered to another asset.')

        ddo = DDO(did)

        # Add public key and authentication
        publisher_account.unlock()
        pub_key, auth = make_public_key_and_authentication(did, publisher_account.address,
                                                           Web3Provider.get_web3())
        ddo.add_public_key(pub_key)
        ddo.add_authentication(auth, PUBLIC_KEY_TYPE_RSA)

        # Setup metadata service
        # First replace `contentUrls` with encrypted `contentUrls`
        assert metadata_copy['base'][
            'contentUrls'], 'contentUrls is required in the metadata base attributes.'
        assert Metadata.validate(metadata), 'metadata seems invalid.'
        logger.debug('Encrypting content urls in the metadata.')
        content_urls_encrypted = SecretStoreProvider.get_secret_store() \
            .encrypt_document(
            did_to_id(did),
            json.dumps(metadata_copy['base']['contentUrls']),
        )

        # only assign if the encryption worked
        if content_urls_encrypted:
            logger.debug('Content urls encrypted successfully.')
            metadata_copy['base']['contentUrls'] = [content_urls_encrypted]
        else:
            raise AssertionError('Encrypting the contentUrls failed. Make sure the secret store is'
                                 ' setup properly in your config file.')

        # DDO url and `Metadata` service
        ddo_service_endpoint = self._aquarius.get_service_endpoint(did)
        metadata_service_desc = ServiceDescriptor.metadata_service_descriptor(metadata_copy,
                                                                              ddo_service_endpoint)

        # Add all services to ddo
        if not service_descriptors:
            brizo = BrizoProvider.get_brizo()
            service_descriptors = ServiceDescriptor.access_service_descriptor(
                metadata[MetadataBase.KEY]['price'],
                brizo.get_purchase_endpoint(),
                brizo.get_service_endpoint(),
                3600,
                ACCESS_SERVICE_TEMPLATE_ID
            )
        _service_descriptors = service_descriptors + [metadata_service_desc]
        for service in ServiceFactory.build_services(Web3Provider.get_web3(),
                                                     self._keeper.artifacts_path, did,
                                                     _service_descriptors):
            ddo.add_service(service)

        logger.debug(
            f'Generated ddo and services, DID is {ddo.did},'
            f' metadata service @{ddo_service_endpoint}, '
            f'`Access` service purchase @{ddo.services[0].get_values()["purchaseEndpoint"]}.')
        response = None
        try:
            # publish the new ddo in ocean-db/Aquarius
            response = self._aquarius.publish_asset_ddo(ddo)
            logger.debug('Asset/ddo published successfully in aquarius.')
        except ValueError as ve:
            raise ValueError(f'Invalid value to publish in the metadata: {str(ve)}')
        except Exception as e:
            logger.error(f'Publish asset in aquarius failed: {str(e)}')

        if not response:
            return None

        # register on-chain
        self._keeper.did_registry.create(
            did,
            key=Web3Provider.get_web3().sha3(text='Metadata'),
            url=ddo_service_endpoint,
            account=publisher_account
        )
        logger.info(f'DDO with DID {did} successfully registered on chain.')
        return ddo

    def resolve(self, did):
        """
        When you pass a did retrieve the ddo associated.

        :param did: DID, str
        :return: DDO
        """
        resolver = self._did_resolver.resolve(did)
        if resolver.is_ddo:
            return self._did_resolver.resolve(did).ddo
        elif resolver.is_url:
            aquarius = AquariusProvider.get_aquarius(resolver.url)
            return DDO(json_text=json.dumps(aquarius.get_asset_ddo(did)))
        else:
            return None

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
        if aquarius_url is not None:
            aquarius = AquariusProvider.get_aquarius(aquarius_url)
            return [DDO(dictionary=ddo_dict) for ddo_dict in
                    aquarius.text_search(text, sort, offset, page)]
        else:
            return [DDO(dictionary=ddo_dict) for ddo_dict in
                    self._aquarius.text_search(text, sort, offset, page)]

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
        if aquarius_url is not None:
            aquarius = AquariusProvider.get_aquarius(aquarius_url)
            return [DDO(dictionary=ddo_dict) for ddo_dict in aquarius.query_search(query)]
        else:
            return [DDO(dictionary=ddo_dict) for ddo_dict in
                    self._aquarius.query_search(query)]

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

    def consume(self, service_agreement_id, did, service_definition_id, consumer_account):
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
        ddo = self.resolve(did)

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

        asset_folder = self._get_asset_folder_path(did, service_definition_id)
        if not os.path.exists(self._downloads_path):
            os.mkdir(self._downloads_path)
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
        return os.path.join(self._downloads_path,
                            f'datafile.{did_to_id(did)}.{service_definition_id}')
