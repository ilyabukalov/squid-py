"""DID Resolver Class."""
import logging

from eth_abi import decode_single
from web3 import Web3

from squid_py.did import did_to_id_bytes
from squid_py.did_resolver.resolved_did import ResolvedDID
from squid_py.did_resolver.resolver_value_type import ResolverValueType
from squid_py.exceptions import (
    OceanDIDNotFound,
    OceanDIDUnknownValueType
)

DID_REGISTRY_EVENT_NAME = 'DIDAttributeRegistered'

logger = logging.getLogger('keeper')


class DIDResolver:
    """
    DID Resolver class
    Resolve DID to a URL/DDO.
    """

    def __init__(self, web3, did_registry):
        self._web3 = web3
        self._did_registry = did_registry

        if not self._did_registry:
            raise ValueError('No DIDRegistry contract object provided')

        self._event_signature = self._did_registry.get_event_signature(DID_REGISTRY_EVENT_NAME)
        if not self._event_signature:
            raise ValueError(f'Cannot find Event {DID_REGISTRY_EVENT_NAME} signature.')

    def resolve(self, did):
        """
        Resolve a DID to an URL/DDO or later an internal/external DID.

        :param did: 32 byte value or DID string to resolver, this is part of the ocean
            DID did:op:<32 byte value>
        :param max_hop_count: max number of hops allowed to find the destination URL/DDO
        :return string: URL or DDO of the resolved DID
        :return None: if the DID cannot be resolved
        :raises TypeError: if did has invalid format
        :raises TypeError: on non 32byte value as the DID
        :raises TypeError: on any of the resolved values are not string/DID bytes.
        :raises OceanDIDCircularReference: on the chain being pointed back to itself.
        :raises OceanDIDNotFound: if no DID can be found to resolve.
        """

        did_bytes = did_to_id_bytes(did)
        if not isinstance(did_bytes, bytes):
            raise TypeError('Invalid did: a 32 Byte DID value required.')

        resolved = ResolvedDID()
        result = None
        # resolve a DID to a URL or DDO
        data = self.get_did(did_bytes)
        while data:
            if data['value_type'] == ResolverValueType.URL:
                if data['value']:
                    try:
                        logger.debug(f'found did {Web3.toHex(did_bytes)} -> {data["value"]}')
                        result = data['value'].decode('utf8')
                    except Exception:
                        raise TypeError(f'Invalid string URL data type for a DID value at'
                                        f' {Web3.toHex(did_bytes)}')
                resolved.add_data(data, result)
                break
            else:
                raise OceanDIDUnknownValueType(f'Unknown value type {data["value_type"]}')
        if resolved.is_url:
            return resolved
        return None

    def get_did(self, did_bytes):
        """Return a did value and value type from the block chain event record using 'did'."""
        result = None
        did = Web3.toHex(did_bytes)
        block_number = self._did_registry.get_update_at(did_bytes)
        logger.debug(f'got blockNumber {block_number} for did {did}')
        if block_number == 0:
            raise OceanDIDNotFound(
                f'DID "{did}" is not found on-chain in the current did registry. '
                f'Please ensure assets are registered in the correct keeper contracts. '
                f'The keeper-contracts DIDRegistry address is {self._did_registry.address}')

        block_filter = self._web3.eth.filter({
            'fromBlock': block_number,
            'toBlock': block_number,
            'topics': [self._event_signature, did]
        })
        log_items = block_filter.get_all_entries()
        if log_items:
            log_item = log_items[-1]
            value, value_type, block_number = decode_single(
                '(string,uint8,uint256)', Web3.toBytes(hexstr=log_item['data']))
            topics = log_item['topics']
            logger.debug(f'topics {topics}')
            result = {
                'value_type': value_type,
                'value': value,
                'block_number': block_number,
                'did_bytes': Web3.toBytes(topics[1]),
                'owner': Web3.toChecksumAddress(topics[2][-20:]),
                'key': Web3.toBytes(topics[3]),
            }
        else:
            logger.warning(f'Could not find {DID_REGISTRY_EVENT_NAME} event logs for '
                           f'did {did} at blockNumber {block_number}')
        return result
