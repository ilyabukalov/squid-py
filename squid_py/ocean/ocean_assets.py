"""Ocean module."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import copy
import json
import logging
import os

from eth_utils import add_0x_prefix
from ocean_keeper.utils import add_ethereum_prefix_and_hash_msg
from ocean_keeper.web3_provider import Web3Provider
from ocean_utils.agreements.service_factory import ServiceDescriptor, ServiceFactory
from ocean_utils.agreements.service_types import ServiceTypes
from ocean_utils.aquarius.aquarius_provider import AquariusProvider
from ocean_utils.aquarius.exceptions import AquariusGenericError
from ocean_utils.ddo.ddo import DDO
from ocean_utils.ddo.metadata import MetadataMain
from ocean_utils.ddo.public_key_rsa import PUBLIC_KEY_TYPE_RSA
from ocean_utils.did import DID, did_to_id, did_to_id_bytes
from ocean_utils.exceptions import (
    OceanDIDAlreadyExist,
)
from ocean_utils.utils.utilities import checksum

from squid_py.brizo.brizo_provider import BrizoProvider
from squid_py.secret_store.secret_store_provider import SecretStoreProvider

logger = logging.getLogger('ocean')


class OceanAssets:
    """Ocean assets class."""

    def __init__(self, keeper, did_resolver, agreements, asset_consumer, asset_executor, config):
        self._keeper = keeper
        self._did_resolver = did_resolver
        self._agreements = agreements
        self._asset_consumer = asset_consumer
        self._asset_executor = asset_executor
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

    def _process_service_descriptors(self, service_descriptors, metadata, account):
        brizo = BrizoProvider.get_brizo()
        ddo_service_endpoint = self._get_aquarius().get_service_endpoint()

        service_type_to_descriptor = {sd[0]: sd for sd in service_descriptors}
        _service_descriptors = []
        metadata_service_desc = service_type_to_descriptor.pop(
            ServiceTypes.METADATA,
            ServiceDescriptor.metadata_service_descriptor(
                    metadata, ddo_service_endpoint
            )
        )
        auth_service_desc = service_type_to_descriptor.pop(
            ServiceTypes.AUTHORIZATION,
            ServiceDescriptor.authorization_service_descriptor(self._config.secret_store_url)
        )
        _service_descriptors = [metadata_service_desc, auth_service_desc]

        # Always dafault to creating a ServiceTypes.ASSET_ACCESS service if no services are specified
        access_service_descriptor = service_type_to_descriptor.pop(
            ServiceTypes.ASSET_ACCESS,
            ServiceDescriptor.access_service_descriptor(
                self._build_access_service(metadata, account),
                brizo.get_consume_endpoint(self._config),
                self._keeper.escrow_access_secretstore_template.address
            )

        )
        compute_service_descriptor = service_type_to_descriptor.pop(
            ServiceTypes.CLOUD_COMPUTE,
            None
        )

        if access_service_descriptor:
            _service_descriptors.append(access_service_descriptor)
        if compute_service_descriptor:
            _service_descriptors.append(compute_service_descriptor)

        _service_descriptors.extend(service_type_to_descriptor.values())
        return ServiceFactory.build_services(_service_descriptors)

    def create(self, metadata, publisher_account,
               service_descriptors=None, providers=None,
               use_secret_store=True):
        """
        Register an asset in both the keeper's DIDRegistry (on-chain) and in the Metadata store (
        Aquarius).

        :param metadata: dict conforming to the Metadata accepted by Ocean Protocol.
        :param publisher_account: Account of the publisher registering this asset
        :param service_descriptors: list of ServiceDescriptor tuples of length 2.
            The first item must be one of ServiceTypes and the second
            item is a dict of parameters and values required by the service
        :param providers: list of addresses of providers of this asset (a provider is
            an ethereum account that is authorized to provide asset services)
        :param use_secret_store: bool indicate whether to use the secret store directly for
            encrypting urls (Uses Brizo provider service if set to False)
        :return: DDO instance
        """
        assert isinstance(metadata, dict), f'Expected metadata of type dict, got {type(metadata)}'
        assert service_descriptors is None or isinstance(service_descriptors, list), \
            f'bad type of `service_descriptors` {type(service_descriptors)}'
        # if not metadata or not Metadata.validate(metadata):
        #     raise OceanInvalidMetadata('Metadata seems invalid. Please make sure'
        #                                ' the required metadata values are filled in.')

        # copy metadata so we don't change the original
        metadata_copy = copy.deepcopy(metadata)
        asset_type = metadata_copy['main']['type']
        assert asset_type in ('dataset', 'algorithm'), f'Invalid/unsupported asset type {asset_type}'

        service_descriptors = service_descriptors or []
        brizo = BrizoProvider.get_brizo()

        services = self._process_service_descriptors(service_descriptors, metadata_copy, publisher_account)
        stype_to_service = {s.type: s for s in services}
        checksum_dict = dict()
        for service in services:
            checksum_dict[str(service.index)] = checksum(service.main)

        # Create a DDO object
        ddo = DDO()
        # Adding proof to the ddo.
        ddo.add_proof(checksum_dict, publisher_account)

        # Generating the did and adding to the ddo.
        did = ddo.assign_did(DID.did(ddo.proof['checksum']))
        logger.debug(f'Generating new did: {did}')
        # Check if it's already registered first!
        if did in self._get_aquarius().list_assets():
            raise OceanDIDAlreadyExist(
                f'Asset id {did} is already registered to another asset.')

        md_service = stype_to_service[ServiceTypes.METADATA]
        ddo_service_endpoint = md_service.service_endpoint
        if '{did}' in ddo_service_endpoint:
            ddo_service_endpoint = ddo_service_endpoint.replace('{did}', did)
            md_service.set_service_endpoint(ddo_service_endpoint)

        # Populate the ddo services
        ddo.add_service(md_service)
        ddo.add_service(stype_to_service[ServiceTypes.AUTHORIZATION])
        access_service = stype_to_service.get(ServiceTypes.ASSET_ACCESS, None)
        compute_service = stype_to_service.get(ServiceTypes.CLOUD_COMPUTE, None)

        if access_service:
            access_service.init_conditions_values(
                did,
                {cname: c.address for cname, c in self._keeper.contract_name_to_instance.items()}
            )
            ddo.add_service(access_service)
        if compute_service:
            compute_service.init_conditions_values(
                did,
                {cname: c.address for cname, c in self._keeper.contract_name_to_instance.items()}
            )
            ddo.add_service(compute_service)

        ddo.proof['signatureValue'] = self._keeper.sign_hash(
            add_ethereum_prefix_and_hash_msg(did_to_id_bytes(did)),
            publisher_account)

        # Add public key and authentication
        ddo.add_public_key(did, publisher_account.address)

        ddo.add_authentication(did, PUBLIC_KEY_TYPE_RSA)

        # Setup metadata service
        # First compute files_encrypted
        if metadata_copy['main']['type'] == 'dataset':
            assert metadata_copy['main']['files'], \
                'files is required in the metadata main attributes.'
            logger.debug('Encrypting content urls in the metadata.')
            if not use_secret_store:
                encrypt_endpoint = brizo.get_encrypt_endpoint(self._config)
                files_encrypted = brizo.encrypt_files_dict(
                    metadata_copy['main']['files'],
                    encrypt_endpoint,
                    ddo.asset_id,
                    publisher_account.address,
                    self._keeper.sign_hash(add_ethereum_prefix_and_hash_msg(ddo.asset_id),
                                           publisher_account)
                )
            else:
                files_encrypted = self._get_secret_store(publisher_account) \
                    .encrypt_document(
                    did_to_id(did),
                    json.dumps(metadata_copy['main']['files']),
                )

            # only assign if the encryption worked
            if files_encrypted:
                logger.debug(f'Content urls encrypted successfully {files_encrypted}')
                index = 0
                for file in metadata_copy['main']['files']:
                    file['index'] = index
                    index = index + 1
                    del file['url']
                metadata_copy['encryptedFiles'] = files_encrypted
            else:
                raise AssertionError('Encrypting the files failed.')

        # DDO url and `Metadata` service

        logger.debug(
            f'Generated ddo and services, DID is {ddo.did},'
            f' metadata service @{ddo_service_endpoint}.')
        response = None

        # register on-chain
        registered_on_chain = self._keeper.did_registry.register(
            ddo.asset_id,
            checksum=Web3Provider.get_web3().toBytes(hexstr=ddo.asset_id),
            url=ddo_service_endpoint,
            account=publisher_account,
            providers=providers
        )
        if registered_on_chain is False:
            logger.warning(f'Registering {did} on-chain failed.')
            return None
        logger.info(f'Successfully registered DDO (DID={did}) on chain.')
        try:
            # publish the new ddo in ocean-db/Aquarius
            response = self._get_aquarius().publish_asset_ddo(ddo)
            logger.info('Asset/ddo published successfully in aquarius.')
        except ValueError as ve:
            raise ValueError(f'Invalid value to publish in the metadata: {str(ve)}')
        except Exception as e:
            logger.error(f'Publish asset in aquarius failed: {str(e)}')
        if not response:
            return None
        return ddo

    def retire(self, did):
        """
        Retire this did of Aquarius

        :param did: DID, str
        :return: bool
        """
        try:
            ddo = self.resolve(did)
            metadata_service = ddo.get_service(ServiceTypes.METADATA)
            self._get_aquarius(metadata_service.service_endpoint).retire_asset_ddo(did)
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

    def search(self, text, sort=None, offset=100, page=1, aquarius_url=None):
        """
        Search an asset in oceanDB using aquarius.

        :param text: String with the value that you are searching
        :param sort: Dictionary to choose order main in some value
        :param offset: Number of elements shows by page
        :param page: Page number
        :param aquarius_url: Url of the aquarius where you want to search. If there is not
            provided take the default
        :return: List of assets that match with the query
        """
        assert page >= 1, f'Invalid page value {page}. Required page >= 1.'
        logger.info(f'Searching asset containing: {text}')
        return [DDO(dictionary=ddo_dict) for ddo_dict in
                self._get_aquarius(aquarius_url).text_search(text, sort, offset, page)['results']]

    def query(self, query, sort=None, offset=100, page=1, aquarius_url=None):
        """
        Search an asset in oceanDB using search query.

        :param query: dict with query parameters
            (e.g.) https://github.com/oceanprotocol/aquarius/blob/develop/docs/for_api_users/API.md
        :param sort: Dictionary to choose order main in some value
        :param offset: Number of elements shows by page
        :param page: Page number
        :param aquarius_url: Url of the aquarius where you want to search. If there is not
            provided take the default
        :return: List of assets that match with the query.
        """
        logger.info(f'Searching asset query: {query}')
        aquarius = self._get_aquarius(aquarius_url)
        return [DDO(dictionary=ddo_dict) for ddo_dict in
                aquarius.query_search(query, sort, offset, page)['results']]

    def order(self, did, index, consumer_account, auto_consume=False):
        """
        Place order by directly creating an SEA (agreement) on-chain.

        :param did: str starting with the prefix `did:op:` and followed by the asset id which is
        a hex str
        :param index: str the service definition id identifying a specific
        service in the DDO (DID document)
        :param consumer_account: Account instance of the consumer
        :param auto_consume: boolean
        :return: agreement_id the service agreement id (can be used to query
            the keeper-contracts for the status of the service agreement)
        """
        agreement_id = self._agreements.new()
        logger.debug(f'about to request create agreement: {agreement_id}')
        self._agreements.create(
            did,
            index,
            agreement_id,
            None,
            consumer_account.address,
            consumer_account,
            auto_consume=auto_consume
        )
        return agreement_id

    def consume(self, service_agreement_id, did, service_index, consumer_account,
                destination, index=None):
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
        :param service_index: identifier of the service inside the asset DDO, str
        :param consumer_account: Account instance of the consumer
        :param destination: str path
        :param index: Index of the document that is going to be downloaded, int
        :return: str path to saved files
        """
        ddo = self.resolve(did)
        if index is not None:
            assert isinstance(index, int), logger.error('index has to be an integer.')
            assert index >= 0, logger.error('index has to be 0 or a positive integer.')
        return self._asset_consumer.download(
            service_agreement_id,
            service_index,
            ddo,
            consumer_account,
            destination,
            BrizoProvider.get_brizo(),
            self._get_secret_store(consumer_account),
            index
        )

    def validate(self, metadata):
        """
        Validate that the metadata is ok to be stored in aquarius.

        :param metadata: dict conforming to the Metadata accepted by Ocean Protocol.
        :return: bool
        """
        return self._get_aquarius(self._aquarius_url).validate_metadata(metadata)

    def owner(self, did):
        """
        Return the owner of the asset.

        :param did: DID, str
        :return: the ethereum address of the owner/publisher of given asset did, hex-str
        """
        # return self._get_aquarius(self._aquarius_url).get_asset_ddo(did).proof['creator']
        return self._keeper.did_registry.get_did_owner(did_to_id(did))

    def owner_assets(self, owner_address):
        """
        List of Asset objects published by ownerAddress

        :param owner_address: ethereum address of owner/publisher, hex-str
        :return: list of dids
        """
        # return [k for k, v in self._get_aquarius(self._aquarius_url).list_assets_ddo().items() if
        #         v['proof']['creator'] == owner_address]
        return self._keeper.did_registry.get_owner_asset_ids(owner_address)

    def consumer_assets(self, consumer_address):
        """
        List of Asset objects purchased by consumerAddress

        :param consumer_address: ethereum address of consumer, hes-str
        :return: list of dids
        """
        return self._keeper.access_secret_store_condition.get_purchased_assets_by_address(
            consumer_address)

    def revoke_permissions(self, did, address_to_revoke, account):
        """
        Revoke access permission to an address.

        :param did: the id of an asset on-chain, hex str
        :param address_to_revoke: ethereum account address, hex str
        :param account: Account executing the action
        :return: bool
        """
        asset_id = add_0x_prefix(did_to_id(did))
        return self._keeper.did_registry.revoke_permission(asset_id, address_to_revoke, account)

    def get_permissions(self, did, address):
        """
        Gets access permission of a grantee

        :param did: the id of an asset on-chain, hex str
        :param address: ethereum account address, hex str
        :return: true if the address has access permission to a DID
        """
        asset_id = add_0x_prefix(did_to_id(did))
        return self._keeper.did_registry.get_permission(asset_id, address)

    def delegate_persmission(self, did, address_to_grant, account):
        """
        Grant access permission to an address.

        :param did: the id of an asset on-chain, hex str
        :param address_to_grant: ethereum account address, hex str
        :param account: Account executing the action
        :return: bool
        """
        asset_id = add_0x_prefix(did_to_id(did))
        return self._keeper.did_registry.grant_permission(asset_id, address_to_grant, account)

    def transfer_ownership(self, did, new_owner_address, account):
        """
        Transfer did ownership to an address.

        :param did: the id of an asset on-chain, hex str
        :param new_owner_address: ethereum account address, hex str
        :param account: Account executing the action
        :return: bool
        """
        asset_id = add_0x_prefix(did_to_id(did))
        return self._keeper.did_registry.transfer_did_ownership(asset_id, new_owner_address,
                                                                account)

    def execute(self, agreement_id, did, index, consumer_account, workflow_did):
        """

        :param agreement_id:representation of `bytes32` id, hexstr
        :param did: computing service did, str
        :param index: id of the service within the asset DDO, str
        :param consumer_account: Account instance of the consumer ordering the service
        :param workflow_did: the asset did (of `workflow` type) which consist of `did:op:` and
        the assetId hex str (without `0x` prefix), str
        :return: local path on the file system where the asset data files are downloaded, str
        """
        workflow_ddo = self.resolve(workflow_did)
        compute_ddo = self.resolve(did)
        if index is not None:
            assert isinstance(index, int), logger.error('index has to be an integer.')
            assert index >= 0, logger.error('index has to be 0 or a positive integer.')
        return self._asset_executor.execute(
            agreement_id,
            compute_ddo,
            workflow_ddo,
            consumer_account,
            BrizoProvider.get_brizo(),
            index
        )

    @staticmethod
    def _build_access_service(metadata, publisher_account):
        return {
            "main": {
                "name": "dataAssetAccessServiceAgreement",
                "creator": publisher_account.address,
                "price": metadata[MetadataMain.KEY]['price'],
                "timeout": 3600,
                "datePublished": metadata[MetadataMain.KEY]['dateCreated']
            }
        }

    def _build_compute_service(self, metadata, publisher_account):
        return {"main": {
            "name": "dataAssetComputeServiceAgreement",
            "creator": publisher_account.address,
            "datePublished": metadata[MetadataMain.KEY]['dateCreated'],
            "price": metadata[MetadataMain.KEY]['price'],
            "timeout": 86400,
            "provider": self._build_provider_config()
        }
        }

    @staticmethod
    def _build_provider_config():
        # TODO manage this as different class and get all the info for different services
        return {
            "type": "Azure",
            "description": "",
            "environment": {
                "cluster": {
                    "type": "Kubernetes",
                    "url": "http://10.0.0.17/xxx"
                },
                "supportedContainers": [
                    {
                        "image": "tensorflow/tensorflow",
                        "tag": "latest",
                        "checksum":
                            "sha256:cb57ecfa6ebbefd8ffc7f75c0f00e57a7fa739578a429b6f72a0df19315deadc"
                    },
                    {
                        "image": "tensorflow/tensorflow",
                        "tag": "latest",
                        "checksum":
                            "sha256:cb57ecfa6ebbefd8ffc7f75c0f00e57a7fa739578a429b6f72a0df19315deadc"
                    }
                ],
                "supportedServers": [
                    {
                        "serverId": "1",
                        "serverType": "xlsize",
                        "price": "50",
                        "cpu": "16",
                        "gpu": "0",
                        "memory": "128gb",
                        "disk": "160gb",
                        "maxExecutionTime": 86400
                    },
                    {
                        "serverId": "2",
                        "serverType": "medium",
                        "price": "10",
                        "cpu": "2",
                        "gpu": "0",
                        "memory": "8gb",
                        "disk": "80gb",
                        "maxExecutionTime": 86400
                    }
                ]
            }
        }
