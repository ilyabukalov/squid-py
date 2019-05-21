#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import os
import time

from examples import ExampleConfig
from squid_py import ConfigProvider, Metadata, Ocean
from squid_py.agreements.service_agreement import ServiceAgreement
from squid_py.agreements.service_types import ServiceTypes
from squid_py.keeper import Keeper
from squid_py.keeper.web3_provider import Web3Provider
from tests.resources.helper_functions import get_publisher_account, get_consumer_account


def _log_event(event_name):
    def _process_event(event):
        print(f'Received event {event_name}: {event}')

    return _process_event


if 'TEST_NILE' in os.environ and os.environ['TEST_NILE'] == '1':
    ASYNC_DELAY = 5  # seconds
else:
    ASYNC_DELAY = 1  # seconds


def buy_asset():
    """
    Requires all ocean services running.

    """
    ConfigProvider.set_config(ExampleConfig.get_config())
    config = ConfigProvider.get_config()
    providers = {
        'duero': '0x9d4ed58293f71122ad6a733c1603927a150735d0',
        'nile': '0x413c9ba0a05b8a600899b41b0c62dd661e689354',
    }
    # make ocean instance
    ocn = Ocean()
    acc = get_publisher_account(config)
    if not acc:
        acc = ([acc for acc in ocn.accounts.list() if acc.password] or ocn.accounts.list())[0]

    keeper = Keeper.get_instance()

    # Register ddo
    did = ''
    if did:
        ddo = ocn.assets.resolve(did)
        logging.info(f'using ddo: {did}')
    else:
        ddo = ocn.assets.create(Metadata.get_example(), acc, providers=[], use_secret_store=True)
        did = ddo.did
        logging.info(f'registered ddo: {did}')
        # ocn here will be used only to publish the asset. Handling the asset by the publisher
        # will be performed by the Brizo server running locally
        test_net = os.environ.get('TEST_NET')
        if test_net.startswith('nile'):
            provider = keeper.did_registry.to_checksum_address(providers['nile'])
        elif test_net.startswith('duero'):
            provider = keeper.did_registry.to_checksum_address(providers['duero'])
        else:
            provider = acc.address

        # Wait for did registry event
        event = keeper.did_registry.subscribe_to_event(
            keeper.did_registry.DID_REGISTRY_EVENT_NAME,
            30,
            event_filter={
                '_did': Web3Provider.get_web3().toBytes(hexstr=ddo.asset_id),
                '_owner': acc.address},
            wait=True
        )
        if not event:
            logging.warning(f'Failed to get the did registry event for asset with did {did}.')
        assert keeper.did_registry.get_block_number_updated(ddo.asset_id) > 0, \
            f'There is an issue in registering asset {did} on-chain.'

        keeper.did_registry.add_provider(ddo.asset_id, provider, acc)
        logging.info(f'is {provider} set as did provider: '
                     f'{keeper.did_registry.is_did_provider(ddo.asset_id, provider)}')

    cons_ocn = Ocean()
    consumer_account = get_consumer_account(config)

    # sign agreement using the registered asset did above
    service = ddo.get_service(service_type=ServiceTypes.ASSET_ACCESS)
    # This will send the order request to Brizo which in turn will execute the agreement on-chain
    cons_ocn.accounts.request_tokens(consumer_account, 100)
    sa = ServiceAgreement.from_service_dict(service.as_dictionary())

    agreement_id = ''
    if not agreement_id:
        # Use these 2 lines to request new agreement from Brizo
        # agreement_id, signature = cons_ocn.agreements.prepare(did, sa.service_definition_id, consumer_account)
        # cons_ocn.agreements.send(did, agreement_id, sa.service_definition_id, signature, consumer_account)

        # assets.order now creates agreement directly using consumer account.
        agreement_id = cons_ocn.assets.order(
            did, sa.service_definition_id, consumer_account)

    logging.info('placed order: %s, %s', did, agreement_id)
    event = keeper.escrow_access_secretstore_template.subscribe_agreement_created(
        agreement_id, 60, None, (), wait=True
    )
    assert event, "Agreement event is not found, check the keeper node's logs"
    logging.info(f'Got agreement event, next: lock reward condition')

    event = keeper.lock_reward_condition.subscribe_condition_fulfilled(
        agreement_id, 60, None, (), wait=True
    )
    assert event, "Lock reward condition fulfilled event is not found, check the keeper node's logs"
    logging.info('Got lock reward event, next: wait for the access condition..')

    event = keeper.access_secret_store_condition.subscribe_condition_fulfilled(
        agreement_id, 30, None, (), wait=True
    )
    logging.info(f'Got access event {event}')
    i = 0
    while ocn.agreements.is_access_granted(
            agreement_id, did, consumer_account.address) is not True and i < 30:
        time.sleep(1)
        i += 1
    assert ocn.agreements.is_access_granted(agreement_id, did, consumer_account.address)

    ocn.assets.consume(
        agreement_id,
        did,
        sa.service_definition_id,
        consumer_account,
        config.downloads_path)
    logging.info('Success buying asset.')
    logging.info('Done buy asset.')


if __name__ == '__main__':
    buy_asset()
