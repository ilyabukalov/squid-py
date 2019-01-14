import json
import logging

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
from squid_py.service_agreement.utils import (make_public_key_and_authentication)

logger = logging.getLogger('ocean')


class OceanAssets:
    def __init__(self, ocean):
        self._ocean = ocean

    def search_by_text(self, text, sort=None, offset=100, page=0, aquarius_url=None):
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
                    self._ocean._metadata_store.text_search(text, sort, offset, page)]

    def search_by_query(self, query):
        """
        Search an asset in oceanDB using search query.

        :param query: dict with query parameters
            (e.g.) {"offset": 100, "page": 0, "sort": {"value": 1},
                    query: {"service:{$elemMatch:{"metadata": {$exists : true}}}}}
                    Here, OceanDB instance of mongodb can leverage power of mongo queries in
                    'query' attribute.
                    For more info -
                    https://docs.mongodb.com/manual/reference/method/db.collection.find
        :return: List of assets that match with the query.
        """
        aquarius_url = self._ocean.config.aquarius_url
        logger.info(f'Searching asset query: {query}')
        if aquarius_url is not None:
            aquarius = AquariusProvider.get_aquarius(aquarius_url)
            return [DDO(dictionary=ddo_dict) for ddo_dict in aquarius.query_search(query)]
        else:
            return [DDO(dictionary=ddo_dict) for ddo_dict in
                    self._ocean._metadata_store.query_search(query)]

    def register(self, metadata, publisher_account, service_descriptors=None):
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
        if did in self._ocean._metadata_store.list_assets():
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
        ddo_service_endpoint = self._ocean._metadata_store.get_service_endpoint(did)
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
                                                     self._ocean._keeper.artifacts_path, did,
                                                     _service_descriptors):
            ddo.add_service(service)

        logger.debug(
            f'Generated ddo and services, DID is {ddo.did},'
            f' metadata service @{ddo_service_endpoint}, '
            f'`Access` service purchase @{ddo.services[0].get_values()["purchaseEndpoint"]}.')
        response = None
        try:
            # publish the new ddo in ocean-db/Aquarius
            response = self._ocean._metadata_store.publish_asset_ddo(ddo)
            logger.debug('Asset/ddo published successfully in aquarius.')
        except ValueError as ve:
            raise ValueError(f'Invalid value to publish in the metadata: {str(ve)}')
        except Exception as e:
            logger.error(f'Publish asset in aquarius failed: {str(e)}')

        if not response:
            return None

        # register on-chain
        self._ocean._keeper.did_registry.register(
            did,
            key=Web3Provider.get_web3().sha3(text='Metadata'),
            url=ddo_service_endpoint,
            account=publisher_account
        )
        logger.info(f'DDO with DID {did} successfully registered on chain.')
        return ddo

    def resolve_did(self, did):
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
