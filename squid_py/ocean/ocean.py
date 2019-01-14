"""Ocean module."""

import json
import logging
import os
import os.path

from squid_py.aquarius.aquarius_provider import AquariusProvider
from squid_py.brizo.brizo_provider import BrizoProvider
from squid_py.config_provider import ConfigProvider
from squid_py.ddo import DDO
from squid_py.ddo.metadata import Metadata, MetadataBase
from squid_py.ddo.public_key_rsa import PUBLIC_KEY_TYPE_RSA
from squid_py.did import DID, did_to_id
from squid_py.did_resolver.did_resolver import DIDResolver
from squid_py.exceptions import (
    OceanDIDAlreadyExist,
    OceanInvalidMetadata,
    OceanInvalidServiceAgreementSignature,
    OceanServiceAgreementExists,
)
from squid_py.keeper import Keeper
from squid_py.keeper.diagnostics import Diagnostics
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.log import setup_logging
from squid_py.ocean.account import Account
from squid_py.ocean.ocean_sea import OceanSea
from squid_py.secret_store.secret_store_provider import SecretStoreProvider
from squid_py.service_agreement.register_service_agreement import register_service_agreement
from squid_py.service_agreement.service_agreement import ServiceAgreement
from squid_py.service_agreement.service_factory import ServiceDescriptor, ServiceFactory
from squid_py.service_agreement.service_types import ACCESS_SERVICE_TEMPLATE_ID, ServiceTypes
from squid_py.service_agreement.utils import (get_conditions_data_from_keeper_contracts,
                                              make_public_key_and_authentication)
from squid_py.utils.utilities import (get_metadata_url, prepare_prefixed_hash)
from .ocean_accounts import OceanAccounts
from .ocean_assets import OceanAssets

CONFIG_FILE_ENVIRONMENT_NAME = 'CONFIG_FILE'

setup_logging()
logger = logging.getLogger('ocean')


class Ocean:
    """The Ocean class is the entry point into Ocean Protocol."""

    def __init__(self, config=None):
        """
        Initialize Ocean class.

        This class provides the main top-level functions in ocean protocol:
         * Publish assets metadata and associated services
            * Each asset is assigned a unique DID and a DID Document (DDO)
            * The DDO contains the asset's services including the metadata
            * The DID is registered on-chain with a URL of the metadata store
              to retrieve the DDO from
         * Discover/Search assets via the current configured metadata store
         * Purchase asset services by choosing a service agreement from the
           asset's DDO. Purchase goes through the service agreements interface
           and starts by signing a service agreement then sending the signature
           to the publisher's Brizo via the `purchaseEndpoint` in the service
           definition:
           >> service_agreement_id = Ocean.purchase_asset_service(did, consumer_account)

        An instance of Ocean is parameterized by a `Config` instance.

        :param config: Config instance
        """
        # Configuration information for the market is stored in the Config class
        # config = Config(filename=config_file, options_dict=config_dict)
        if config:
            ConfigProvider.set_config(config)

        self.config = ConfigProvider.get_config()

        # With the interface loaded, the Keeper node is connected with all contracts
        self._keeper = Keeper.get_instance()

        # Add the Metadata store to the interface
        self._metadata_store = AquariusProvider.get_aquarius()

        downloads_path = os.path.join(os.getcwd(), 'downloads')
        if self.config.has_option('resources', 'downloads.path'):
            downloads_path = self.config.get('resources', 'downloads.path') or downloads_path
        self._downloads_path = downloads_path

        # Collect the accounts
        self.accounts = OceanAccounts(self)
        self._accounts = self.get_accounts()
        assert self._accounts

        self._did_resolver = DIDResolver(Web3Provider.get_web3(), self._keeper.did_registry)

        # Verify keeper contracts
        Diagnostics.verify_contracts()
        Diagnostics.check_deployed_agreement_templates()
        logger.info('Squid Ocean instance initialized: ')
        logger.info(f'\tOther accounts: {sorted(self._accounts)}')
        logger.info(f'\taquarius: {self._metadata_store.url}')
        logger.info(f'\tDIDRegistry @ {self._keeper.did_registry.address}')

        self.assets = OceanAssets(self)
        self.sea = OceanSea(self)

        if self.config.secret_store_url and self.config.parity_url and self.config.parity_address:
            logger.info(f'\tSecretStore: url {self.config.secret_store_url}, '
                        f'parity-client {self.config.parity_url}, '
                        f'account {self.config.parity_address}')

    def get_accounts(self):
        """
        Returns all available accounts loaded via a wallet, or by Web3.

        :return: dict of account-address: Account instance
        """
        return self.accounts.list()

    def search_assets_by_text(self, *args, **kwargs):
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
        return self.assets.search_by_text(*args, **kwargs)

    def search_assets(self, *args, **kwargs):
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
        return self.assets.search_by_query(*args, **kwargs)

    def register_asset(self, *args, **kwargs):
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
        return self.assets.register(*args, **kwargs)

    def _approve_token_transfer(self, amount, consumer_account):
        if self._keeper.token.get_token_balance(consumer_account.address) < amount:
            raise ValueError(
                f'Account {consumer_account.address} does not have sufficient tokens '
                f'to approve for transfer.')

        self._keeper.token.token_approve(self._keeper.payment_conditions.address, amount,
                                        consumer_account)

    def purchase_asset_service(self, *args, **kwargs):
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
        return self.sea.purchase_asset_service(*args, **kwargs)

    def execute_service_agreement(self, *args, **kwargs):
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
        return self.sea.execute_service_agreement(*args, **kwargs)

    def is_access_granted(self, *args, **kwargs):
        """
        Check permission for the agreement.

        Verify on-chain that the `consumer_address` has permission to access the given asset `did`
        according to the `service_agreement_id`.

        :param service_agreement_id: str
        :param did: DID, str
        :param consumer_address: Account address, str
        :return: bool True if user has permission
        """
        return self.sea.is_access_granted(*args, **kwargs)

    def resolve_asset_did(self, did):
        """
        When you pass a did retrieve the ddo associated.

        :param did: DID, str
        :return: DDO
        """
        return self.assets.resolve_did(did)

    def consume_service(self, *args, **kwargs):
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
        return self.sea.consume_service(*args, **kwargs)

    def _get_asset_folder_path(self, did, service_definition_id):
        """

        :param did:
        :param service_definition_id:
        :return:
        """
        return os.path.join(self._downloads_path,
                            f'datafile.{did_to_id(did)}.{service_definition_id}')

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
