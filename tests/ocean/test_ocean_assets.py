#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

import pytest
from ocean_keeper.exceptions import OceanDIDNotFound
from ocean_keeper.web3_provider import Web3Provider
from ocean_utils.agreements.service_agreement import ServiceAgreement
from ocean_utils.agreements.service_factory import ServiceDescriptor
from ocean_utils.agreements.service_types import ServiceTypes
from ocean_utils.aquarius import AquariusProvider
from ocean_utils.ddo.ddo import DDO
from ocean_utils.did import DID

from tests.resources.helper_functions import (get_algorithm_ddo, get_computing_metadata,
                                              get_resource_path, log_event)
from tests.resources.tiers import e2e_test


def create_asset(publisher_ocean_instance):
    ocn = publisher_ocean_instance
    sample_ddo_path = get_resource_path('ddo', 'ddo_sa_sample.json')
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    acct = ocn.main_account

    asset = DDO(json_filename=sample_ddo_path)
    my_secret_store = 'http://myownsecretstore.com'
    auth_service = ServiceDescriptor.authorization_service_descriptor(my_secret_store)
    return ocn.assets.create(asset.metadata, acct, [auth_service])


@e2e_test
def test_register_asset(publisher_ocean_instance):
    logging.debug("".format())
    sample_ddo_path = get_resource_path('ddo', 'ddo_sa_sample.json')
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    ##########################################################
    # Setup account
    ##########################################################
    publisher = publisher_ocean_instance.main_account

    # ensure Ocean token balance
    if publisher_ocean_instance.accounts.balance(publisher).ocn == 0:
        publisher_ocean_instance.accounts.request_tokens(publisher, 200)

    # You will need some token to make this transfer!
    assert publisher_ocean_instance.accounts.balance(publisher).ocn > 0

    ##########################################################
    # Create an asset DDO with valid metadata
    ##########################################################
    asset = DDO(json_filename=sample_ddo_path)

    ##########################################################
    # Register using high-level interface
    ##########################################################
    ddo = publisher_ocean_instance.assets.create(asset.metadata, publisher)
    publisher_ocean_instance.assets.retire(ddo.did)


@e2e_test
def test_resolve_did(publisher_ocean_instance, metadata):
    # prep ddo
    # metadata = Metadata.get_example()
    publisher = publisher_ocean_instance.main_account
    # happy path
    original_ddo = publisher_ocean_instance.assets.create(metadata, publisher)
    did = original_ddo.did
    ddo = publisher_ocean_instance.assets.resolve(did).as_dictionary()
    original = original_ddo.as_dictionary()
    assert ddo['publicKey'] == original['publicKey']
    assert ddo['authentication'] == original['authentication']
    assert ddo['service']
    assert original['service']
    metadata = ddo['service'][0]['attributes']
    if 'datePublished' in metadata['main']:
        metadata['main'].pop('datePublished')
    assert ddo['service'][0]['attributes']['main']['name'] == \
           original['service'][0]['attributes']['main']['name']
    assert ddo['service'][1] == original['service'][1]

    # Can't resolve unregistered asset
    unregistered_did = DID.did({"0": "0x00112233445566"})
    with pytest.raises(OceanDIDNotFound):
        publisher_ocean_instance.assets.resolve(unregistered_did)

    # Raise error on bad did
    invalid_did = "did:op:0123456789"
    with pytest.raises(OceanDIDNotFound):
        publisher_ocean_instance.assets.resolve(invalid_did)
    publisher_ocean_instance.assets.retire(did)


@e2e_test
def test_create_data_asset(publisher_ocean_instance, consumer_ocean_instance):
    """
    Setup accounts and asset, register this asset on Aquarius (MetaData store)
    """
    pub_ocn = publisher_ocean_instance
    cons_ocn = consumer_ocean_instance

    logging.debug("".format())
    sample_ddo_path = get_resource_path('ddo', 'ddo_sa_sample.json')
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    ##########################################################
    # Setup 2 accounts
    ##########################################################
    aquarius_acct = pub_ocn.main_account
    consumer_acct = cons_ocn.main_account

    # ensure Ocean token balance
    if pub_ocn.accounts.balance(aquarius_acct).ocn == 0:
        rcpt = pub_ocn.accounts.request_tokens(aquarius_acct, 200)
        Web3Provider.get_web3().eth.waitForTransactionReceipt(rcpt)
    if cons_ocn.accounts.balance(consumer_acct).ocn == 0:
        rcpt = cons_ocn.accounts.request_tokens(consumer_acct, 200)
        Web3Provider.get_web3().eth.waitForTransactionReceipt(rcpt)

    # You will need some token to make this transfer!
    assert pub_ocn.accounts.balance(aquarius_acct).ocn > 0
    assert cons_ocn.accounts.balance(consumer_acct).ocn > 0

    ##########################################################
    # Create an Asset with valid metadata
    ##########################################################
    asset = DDO(json_filename=sample_ddo_path)

    ##########################################################
    # List currently published assets
    ##########################################################
    meta_data_assets = pub_ocn.assets.search('')
    if meta_data_assets:
        print("Currently registered assets:")
        print(meta_data_assets)

    if asset.did in meta_data_assets:
        pub_ocn.assets.resolve(asset.did)
        pub_ocn.assets.retire(asset.did)
    # Publish the metadata
    new_asset = pub_ocn.assets.create(asset.metadata, aquarius_acct)

    # get_asset_metadata only returns 'main' key, is this correct?
    published_metadata = cons_ocn.assets.resolve(new_asset.did)

    assert published_metadata
    # only compare top level keys
    assert sorted(list(asset.metadata['main'].keys())).remove('files') == sorted(
        list(published_metadata.metadata.keys())).remove('encryptedFiles')
    publisher_ocean_instance.assets.retire(new_asset.did)


def test_create_asset_with_different_secret_store(publisher_ocean_instance):
    ocn = publisher_ocean_instance

    sample_ddo_path = get_resource_path('ddo', 'ddo_sa_sample.json')
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    acct = ocn.main_account

    aqua = AquariusProvider.get_aquarius(ocn.config.aquarius_url)
    aqua.retire_all_assets()

    asset = DDO(json_filename=sample_ddo_path)
    my_secret_store = 'http://myownsecretstore.com'
    auth_service = ServiceDescriptor.authorization_service_descriptor(my_secret_store)
    new_asset = ocn.assets.create(asset.metadata, acct, [auth_service])
    assert new_asset.get_service(ServiceTypes.AUTHORIZATION).service_endpoint == my_secret_store
    assert new_asset.get_service(ServiceTypes.ASSET_ACCESS)
    assert new_asset.get_service(ServiceTypes.METADATA)
    publisher_ocean_instance.assets.retire(new_asset.did)

    access_service = ServiceDescriptor.access_service_descriptor(
        {"main": {
            "name": "dataAssetAccessServiceAgreement",
            "creator": '0x1234',
            "price": '1',
            "timeout": 3600,
            "datePublished": '2019-08-30T12:19:54Z'
        }},
        'service/endpoint',
        '0x0011001100110011'
    )
    new_asset = ocn.assets.create(asset.metadata, acct, [access_service])
    assert new_asset.get_service(ServiceTypes.AUTHORIZATION)
    assert new_asset.get_service(ServiceTypes.ASSET_ACCESS)
    assert new_asset.get_service(ServiceTypes.METADATA)
    publisher_ocean_instance.assets.retire(new_asset.did)

    new_asset = ocn.assets.create(asset.metadata, acct)
    assert new_asset.get_service(ServiceTypes.AUTHORIZATION)
    assert new_asset.get_service(ServiceTypes.ASSET_ACCESS)
    assert new_asset.get_service(ServiceTypes.METADATA)
    publisher_ocean_instance.assets.retire(new_asset.did)


def test_asset_owner(publisher_ocean_instance):
    ocn = publisher_ocean_instance

    sample_ddo_path = get_resource_path('ddo', 'ddo_sa_sample.json')
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    acct = ocn.main_account

    asset = DDO(json_filename=sample_ddo_path)
    my_secret_store = 'http://myownsecretstore.com'
    auth_service = ServiceDescriptor.authorization_service_descriptor(my_secret_store)
    new_asset = ocn.assets.create(asset.metadata, acct, [auth_service])

    assert ocn.assets.owner(new_asset.did) == acct.address
    publisher_ocean_instance.assets.retire(new_asset.did)


def test_owner_assets(publisher_ocean_instance):
    ocn = publisher_ocean_instance
    acct = ocn.main_account
    assets_owned = len(ocn.assets.owner_assets(acct.address))
    asset = create_asset(publisher_ocean_instance)
    assert len(ocn.assets.owner_assets(acct.address)) == assets_owned + 1
    publisher_ocean_instance.assets.retire(asset.did)


def test_assets_consumed(publisher_ocean_instance, consumer_ocean_instance):
    ocn = publisher_ocean_instance
    acct = consumer_ocean_instance.main_account
    consumed_assets = len(ocn.assets.consumer_assets(acct.address))
    asset = create_asset(publisher_ocean_instance)
    service = asset.get_service(service_type=ServiceTypes.ASSET_ACCESS)
    service_dict = service.as_dictionary()
    sa = ServiceAgreement.from_json(service_dict)
    keeper = ocn.keeper

    def grant_access(event, ocn_instance, agr_id, did, cons_address, account):
        ocn_instance.agreements.conditions.grant_access(
            agr_id, did, cons_address, account)

    agreement_id = consumer_ocean_instance.assets.order(
        asset.did, sa.index, acct)
    keeper.lock_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        15,
        grant_access,
        (publisher_ocean_instance, agreement_id, asset.did,
         acct.address, publisher_ocean_instance.main_account),
        wait=True
    )

    keeper.access_secret_store_condition.subscribe_condition_fulfilled(
        agreement_id,
        15,
        log_event(keeper.access_secret_store_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert ocn.agreements.is_access_granted(agreement_id, asset.did, acct.address)

    assert len(ocn.assets.consumer_assets(acct.address)) == consumed_assets + 1
    publisher_ocean_instance.assets.retire(asset.did)


def test_ocean_assets_resolve(publisher_ocean_instance, metadata):
    publisher = publisher_ocean_instance.main_account
    ddo = publisher_ocean_instance.assets.create(metadata, publisher)
    ddo_resolved = publisher_ocean_instance.assets.resolve(ddo.did)
    assert ddo.did == ddo_resolved.did
    publisher_ocean_instance.assets.retire(ddo.did)


def test_ocean_assets_search(publisher_ocean_instance, metadata):
    publisher = publisher_ocean_instance.main_account
    ddo = publisher_ocean_instance.assets.create(metadata, publisher)
    assert len(publisher_ocean_instance.assets.search('Monkey')) > 0
    publisher_ocean_instance.assets.retire(ddo.did)


def test_ocean_assets_validate(publisher_ocean_instance, metadata):
    assert publisher_ocean_instance.assets.validate(metadata)


def test_ocean_assets_algorithm(publisher_ocean_instance):
    # Allow publish an algorithm
    publisher = publisher_ocean_instance.main_account
    metadata = get_algorithm_ddo()['service'][0]
    ddo = publisher_ocean_instance.assets.create(metadata['attributes'], publisher)
    assert ddo
    publisher_ocean_instance.assets.retire(ddo.did)


def test_ocean_assets_workflow(publisher_ocean_instance):
    # :FIXME: re-enable this test once plecos v1.0.1 is released in a new Aquarius version.
    return
    # # Allow publish an workflow
    # publisher = publisher_ocean_instance.main_account
    # metadata = get_workflow_ddo()['service'][0]
    # valid_results = plecos.validate_dict_local(metadata['attributes'])
    # print(f'validation result: {valid_results}')
    # ddo = publisher_ocean_instance.assets.create(metadata['attributes'], publisher)
    # assert ddo
    # publisher_ocean_instance.assets.retire(ddo.did)


def test_ocean_assets_compute(publisher_ocean_instance):
    publisher = publisher_ocean_instance.main_account
    metadata = get_computing_metadata()
    ddo = publisher_ocean_instance.assets.create(metadata, publisher)
    assert ddo
    publisher_ocean_instance.assets.retire(ddo.did)


def test_ocean_transfer_ownership(publisher_ocean_instance, metadata, consumer_ocean_instance):
    publisher = publisher_ocean_instance.main_account
    consumer = consumer_ocean_instance.main_account
    ddo = publisher_ocean_instance.assets.create(metadata, publisher)
    owner = publisher_ocean_instance.assets.owner(ddo.did)
    assert owner == publisher.address
    publisher_ocean_instance.assets.transfer_ownership(ddo.did, consumer.address, publisher)
    assert publisher_ocean_instance.assets.owner(ddo.did) == consumer.address
    publisher_ocean_instance.assets.retire(ddo.did)


def test_ocean_grant_permissions(publisher_ocean_instance, metadata, consumer_ocean_instance):
    publisher = publisher_ocean_instance.main_account
    consumer = consumer_ocean_instance.main_account
    ddo = publisher_ocean_instance.assets.create(metadata, publisher)
    assert not publisher_ocean_instance.assets.get_permissions(ddo.did, consumer.address)
    publisher_ocean_instance.assets.delegate_persmission(ddo.did, consumer.address, publisher)
    assert publisher_ocean_instance.assets.get_permissions(ddo.did, consumer.address)
    publisher_ocean_instance.assets.revoke_permissions(ddo.did, consumer.address, publisher)
    assert not publisher_ocean_instance.assets.get_permissions(ddo.did, consumer.address)


# def test_ocean_execute_workflow(publisher_ocean_instance, consumer_ocean_instance):
#     publisher = publisher_ocean_instance.main_account
#     consumer = consumer_ocean_instance.main_account
#     publisher_ocean_instance.assets._get_aquarius().retire_all_assets()
#     metadata = get_workflow_ddo()['service'][0]
#     workflow_ddo = publisher_ocean_instance.assets.create(metadata['attributes'], publisher)
#     assert workflow_ddo
#     metadata = get_computing_metadata()
#     ddo_computing = publisher_ocean_instance.assets.create(metadata, publisher)
#     assert ddo_computing
#     service = ddo_computing.get_service(service_type=ServiceTypes.CLOUD_COMPUTE)
#     sa = ServiceAgreement.from_json(service.as_dictionary())
#     agreement_id = consumer_ocean_instance.assets.order(ddo_computing.did, sa.index, consumer)
#     keeper = publisher_ocean_instance.keeper
#     event = keeper.compute_execution_condition.subscribe_condition_fulfilled(
#         agreement_id,
#         90,
#         log_event(keeper.compute_execution_condition.FULFILLED_EVENT),
#         (),
#         wait=True
#     )
#     assert event, 'no event for compute_execution_condition.Fulfilled'
#
#     try:
#         job_id = consumer_ocean_instance.assets.execute(
#             agreement_id, ddo_computing.did, sa.index, consumer, workflow_ddo.did)
#         print(f'Compute job started successfully, job id is {job_id}')
#     except Exception as e:
#         print(f'Executing the compute job for agreementId {agreement_id} failed: {e}')
