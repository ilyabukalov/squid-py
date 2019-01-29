"""Keeper module to call keeper-contracts."""
import logging
from urllib.parse import urlparse

from web3 import Web3

from squid_py.exceptions import OceanDIDNotFound
from squid_py.did import did_to_id_bytes
from squid_py.did_resolver.did_resolver import DID_REGISTRY_EVENT_NAME
from squid_py.did_resolver.resolver_value_type import ResolverValueType
from squid_py.keeper.contract_base import ContractBase

logger = logging.getLogger(__name__)


class DIDRegistry(ContractBase):
    """Class to register and update Ocean DID's."""

    @staticmethod
    def get_instance():
        """Returns a ContractBase instance of the DIDRegistry contract."""
        return DIDRegistry('DIDRegistry')

    def register(self, did_source, url=None, key=None, account=None):
        """
        Register or update a DID on the block chain using the DIDRegistry smart contract.

        :param did_source: DID to register/update, can be a 32 byte or hexstring
        :param url: URL of the resolved DID
        :param key: Optional 32 byte key ( 64 char hex )
        :param account: instance of Account to use to register/update the DID
        :return: Receipt
        """

        value_type = ResolverValueType.URL
        value = None

        did_source_id = did_to_id_bytes(did_source)

        if not did_source_id:
            raise ValueError(f'{did_source} must be a valid DID to register')

        if url:
            value = url
            if not urlparse(url):
                raise ValueError(f'Invalid URL {url} to register for DID {did_source}')

        if isinstance(key, str):
            key = Web3.sha3(text=key)

        if key is None:
            key = Web3.toBytes(0)

        if not isinstance(key, bytes):
            raise ValueError(f'Invalid key value {key}, must be bytes or string')

        if account is None:
            raise ValueError('You must provide an account to use to register a DID')

        account.unlock()
        transaction = self.register_attribute(did_source_id, value_type, key, value,
                                              account.address)
        receipt = self.get_tx_receipt(transaction)
        return receipt

    def register_attribute(self, did_hash, value_type, key, value, account_address):
        """Register an DID attribute as an event on the block chain.

            did_hash: 32 byte string/hex of the DID
            value_type: 0 = DID, 1 = DIDREf, 2 = URL, 3 = DDO
            key: 32 byte string/hex free format
            value: string can be anything, probably DDO or URL
            account_address: owner of this DID registration record
        """
        return self.contract_concise.registerAttribute(
            did_hash,
            value_type,
            key,
            value,
            transact={'from': account_address}
        )

    def get_update_at(self, did):
        """Return the block number the last did was updated on the block chain."""
        return self.contract_concise.getUpdateAt(did)

    def get_owner(self, did):
        """
        Return the owner of the did.

        :param did: Asset did, did
        :return:
        """
        return self.contract_concise.getOwner(did)

    def get_registered_attribute(self, did_bytes):
        """

        Example of event logs from event_filter.get_all_entries():
        [AttributeDict(
            {'args': AttributeDict(
                {'did': b'\x02n\xfc\xfb\xfdNM\xe9\xb8\xe0\xba\xc2\xb2\xc7\xbeg\xc9/\x95\xc3\x16\
                           x98G^\xb9\xe1\xf0T\xce\x83\xcf\xab',
                 'owner': '0xAd12CFbff2Cb3E558303334e7e6f0d25D5791fc2',
                 'key': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
                          \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                 'value': 'http://localhost:5000',
                 'valueType': 2,
                 'updatedAt': 1947}),
             'event': 'DIDAttributeRegistered',
             'logIndex': 0,
             'transactionIndex': 1,
             'transactionHash': HexBytes('0xea9ca5748d54766fb43fe9660dd04b2e3bb29a0fbe18414457cca3dd488d359d'),
             'address': '0x86DF95937ec3761588e6DEbAB6E3508e271cC4dc',
             'blockHash': HexBytes('0xbbbe1046b737f33b2076cb0bb5ba85a840c836cf1ffe88891afd71193d677ba2'),
             'blockNumber': 1947})]

        """
        result = None
        did = Web3.toHex(did_bytes)
        block_number = self.get_update_at(did_bytes)
        logger.debug(f'got blockNumber {block_number} for did {did}')
        if block_number == 0:
            raise OceanDIDNotFound(
                f'DID "{did}" is not found on-chain in the current did registry. '
                f'Please ensure assets are registered in the correct keeper contracts. '
                f'The keeper-contracts DIDRegistry address is {self.address}')

        event = getattr(self.events, DID_REGISTRY_EVENT_NAME)
        block_filter = event().createFilter(
            fromBlock=block_number, toBlock=block_number, argument_filters={'did': did_bytes}
        )
        log_items = block_filter.get_all_entries()
        if log_items:
            log_item = log_items[-1].args
            value = log_item.value
            value_type = log_item.valueType
            block_number = log_item.updatedAt
            result = {
                'value_type': value_type,
                'value': value,
                'block_number': block_number,
                'did_bytes': log_item.did,
                'owner': Web3.toChecksumAddress(log_item.owner),
                'key': Web3.toBytes(log_item.key)
            }
        else:
            logger.warning(f'Could not find {DID_REGISTRY_EVENT_NAME} event logs for '
                           f'did {did} at blockNumber {block_number}')
        return result
