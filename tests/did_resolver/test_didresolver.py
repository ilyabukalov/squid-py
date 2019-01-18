import logging
import secrets

import pytest
from web3 import Web3

from squid_py.did import DID, did_to_id
from squid_py.did_resolver.did_resolver import (
    DIDResolver,
)
from squid_py.did_resolver.resolver_value_type import ResolverValueType
from squid_py.exceptions import (
    OceanDIDNotFound,
)
from squid_py.keeper.web3_provider import Web3Provider
from tests.resources.tiers import e2e_test

logger = logging.getLogger()


@e2e_test
def test_did_registry_register(publisher_ocean_instance):
    ocean = publisher_ocean_instance

    register_account = ocean.main_account
    did_registry = ocean.keeper.did_registry
    did_id = secrets.token_hex(32)
    did_test = 'did:op:' + did_id
    key_test = Web3.sha3(text='provider')
    value_test = 'http://localhost:5000'

    # register DID-> URL
    assert did_registry.register(did_test, url=value_test, key=key_test, account=register_account)


@e2e_test
def test_did_registry_no_accout_provided(publisher_ocean_instance):
    ocean = publisher_ocean_instance
    register_account = ocean.main_account
    did_registry = ocean.keeper.did_registry
    did_id = secrets.token_hex(32)
    did_test = 'did:op:' + did_id
    value_test = 'http://localhost:5000'
    # No account provided
    with pytest.raises(ValueError):
        did_registry.register(did_test, url=value_test)

    # Invalide key field provided
    with pytest.raises(ValueError):
        did_registry.register(did_test, url=value_test, account=register_account, key=42)


@e2e_test
def test_did_resolver_library(publisher_ocean_instance):
    ocean = publisher_ocean_instance
    register_account = ocean.main_account
    owner_address = register_account.address
    did_registry = ocean.keeper.did_registry
    did_id = secrets.token_hex(32)
    did_test = 'did:op:' + did_id
    value_type = ResolverValueType.URL
    key_test = Web3.sha3(text='provider')
    value_test = 'http://localhost:5000'
    key_zero = Web3.toBytes(hexstr='0x' + ('00' * 32))

    did_resolver = DIDResolver(Web3Provider.get_web3(), ocean.keeper.did_registry)

    # resolve URL from a direct DID ID value
    did_id_bytes = Web3.toBytes(hexstr=did_id)

    did_registry.register(did_test, url=value_test, account=register_account)

    did_resolved = did_resolver.resolve(did_test)
    assert did_resolved
    assert did_resolved.is_url
    assert did_resolved.url == value_test
    assert did_resolved.key == key_zero
    assert did_resolved.owner == owner_address

    with pytest.raises(ValueError):
        did_resolver.resolve(did_id)

    did_resolved = did_resolver.resolve(did_id_bytes)
    assert did_resolved
    assert did_resolved.is_url
    assert did_resolved.url == value_test
    assert did_resolved.key == key_zero
    assert did_resolved.owner == owner_address

    # resolve URL from a hash of a DID string
    did_hash = Web3.sha3(text=did_test)

    register_account.unlock()
    register_did = did_registry.register_attribute(did_hash, value_type, key_test, value_test,
                                                   owner_address)
    receipt = did_registry.get_tx_receipt(register_did)
    did_resolved = did_resolver.resolve(did_hash)
    assert did_resolved
    assert did_resolved.is_url
    assert did_resolved.url == value_test
    assert did_resolved.key == key_test
    assert did_resolved.value_type == value_type
    assert did_resolved.owner == owner_address
    assert did_resolved.block_number == receipt['blockNumber']

    # test update of an already assigned DID
    value_test_new = 'http://aquarius:5000'
    register_account.unlock()
    register_did = did_registry.register_attribute(did_hash, value_type, key_test, value_test_new,
                                                   owner_address)
    receipt = did_registry.get_tx_receipt(register_did)
    did_resolved = did_resolver.resolve(did_hash)
    assert did_resolved
    assert did_resolved.is_url
    assert did_resolved.url == value_test_new
    assert did_resolved.key == key_test
    assert did_resolved.value_type == value_type
    assert did_resolved.owner == owner_address
    assert did_resolved.block_number == receipt['blockNumber']

    value_type = ResolverValueType.URL
    # resolve chain of direct DID IDS to URL
    chain_length = 4
    ids = []
    for i in range(0, chain_length):
        ids.append(secrets.token_hex(32))

    for i in range(0, chain_length):
        did_id_bytes = Web3.toBytes(hexstr=ids[i])
        register_account.unlock()
        logger.debug('end chain {0} -> URL'.format(Web3.toHex(did_id_bytes)))
        register_did = did_registry.register_attribute(
            did_id_bytes, ResolverValueType.URL, key_test, value_test, owner_address)

        receipt = did_registry.get_tx_receipt(register_did)

    did_id_bytes = Web3.toBytes(hexstr=ids[3])
    did_resolved = did_resolver.resolve(did_id_bytes)
    assert did_resolved
    assert did_resolved.is_url
    assert did_resolved.url == value_test
    assert did_resolved.key == key_test
    assert did_resolved.value_type == value_type
    assert did_resolved.owner == owner_address
    assert did_resolved.block_number == receipt['blockNumber']


@e2e_test
def test_did_not_found(publisher_ocean_instance):
    ocean = publisher_ocean_instance
    did_resolver = DIDResolver(Web3Provider.get_web3(), ocean.keeper.did_registry)
    did_id = secrets.token_hex(32)
    did_id_bytes = Web3.toBytes(hexstr=did_id)
    with pytest.raises(OceanDIDNotFound):
        did_resolver.resolve(did_id_bytes)


@e2e_test
def test_get_did(publisher_ocean_instance):
    ocean = publisher_ocean_instance
    register_account = ocean.main_account
    did_registry = ocean.keeper.did_registry
    did = DID.did()
    value_test = 'http://localhost:5000'
    did_resolver = DIDResolver(Web3Provider.get_web3(), ocean.keeper.did_registry)
    did_registry.register(did, url=value_test, account=register_account)
    did_id = did_to_id(did)
    did_resolver.get_did(Web3.toBytes(hexstr=did_id))


@e2e_test
def test_get_did_not_valid(publisher_ocean_instance):
    ocean = publisher_ocean_instance
    did_resolver = DIDResolver(Web3Provider.get_web3(), ocean.keeper.did_registry)
    with pytest.raises(TypeError):
        did_resolver.get_did('not valid')
