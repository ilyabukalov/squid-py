#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import secrets

import pytest
from web3 import Web3

from squid_py.ddo.ddo import DDO
from squid_py.did import DID, did_to_id
from squid_py.did_resolver.did_resolver import (
    DIDResolver,
)
from squid_py.exceptions import (
    OceanDIDNotFound,
)
from squid_py.keeper import Keeper
from tests.resources.helper_functions import get_resource_path
from tests.resources.tiers import e2e_test

logger = logging.getLogger()


def keeper():
    return Keeper.get_instance()


@e2e_test
def test_did_registry_register(publisher_ocean_instance):
    ocean = publisher_ocean_instance

    register_account = ocean.main_account
    did_registry = keeper().did_registry
    did_id = secrets.token_hex(32)
    did_test = 'did:op:' + did_id
    checksum_test = Web3.sha3(text='checksum')
    value_test = 'http://localhost:5000'

    # register DID-> URL
    assert did_registry.register(did_test, checksum_test, url=value_test, account=register_account)


@e2e_test
def test_did_registry_no_account_provided():
    did_registry = keeper().did_registry
    did_id = secrets.token_hex(32)
    did_test = 'did:op:' + did_id
    checksum_test = Web3.sha3(text='checksum')
    value_test = 'http://localhost:5000'
    # No checksum provided
    with pytest.raises(TypeError):
        did_registry.register(did_test, url=value_test)
    # No account provided
    with pytest.raises(ValueError):
        did_registry.register(did_test, did_test, url=value_test, account=None)

    # Invalide key field provided
    with pytest.raises(ValueError):
        did_registry.register(did_test, checksum_test, url=value_test, account=None)


@e2e_test
def test_did_resolver_library(publisher_ocean_instance):
    ocean = publisher_ocean_instance
    register_account = ocean.main_account
    did_registry = keeper().did_registry
    checksum_test = Web3.sha3(text='checksum')
    value_test = 'http://localhost:5000'

    did_resolver = DIDResolver(keeper().did_registry)

    sample_ddo_path = get_resource_path('ddo', 'ddo_sample1.json')
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)
    asset1 = DDO(json_filename=sample_ddo_path)

    did_registry.register(asset1.did, checksum_test, url=value_test, account=register_account)
    ocean.assets._get_aquarius().publish_asset_ddo(asset1)

    did_resolved = did_resolver.resolve(asset1.did)
    assert did_resolved
    assert did_resolved.did == asset1.did

    with pytest.raises(ValueError):
        did_resolver.resolve(asset1.asset_id)
    ocean.assets._get_aquarius().retire_asset_ddo(asset1.did)


@e2e_test
def test_did_not_found(publisher_ocean_instance):
    did_resolver = DIDResolver(keeper().did_registry)
    did_id = secrets.token_hex(32)
    did_id_bytes = Web3.toBytes(hexstr=did_id)
    with pytest.raises(OceanDIDNotFound):
        did_resolver.resolve(did_id_bytes)


@e2e_test
def test_get_resolve_url(publisher_ocean_instance):
    ocean = publisher_ocean_instance
    register_account = ocean.main_account
    did_registry = keeper().did_registry
    did = DID.did()
    value_test = 'http://localhost:5000'
    did_resolver = DIDResolver(keeper().did_registry)
    did_registry.register(did, b'test', url=value_test, account=register_account)
    did_id = did_to_id(did)
    url = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id))
    assert url == value_test


@e2e_test
def test_get_did_not_valid(publisher_ocean_instance):
    did_resolver = DIDResolver(keeper().did_registry)
    with pytest.raises(TypeError):
        did_resolver.get_resolve_url('not valid')
