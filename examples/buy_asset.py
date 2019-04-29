#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import os
import time

from examples import ExampleConfig, get_account_from_config
from squid_py import ConfigProvider, Metadata, Ocean
from squid_py.agreements.service_agreement import ServiceAgreement
from squid_py.agreements.service_types import ServiceTypes
from squid_py.keeper import Keeper
from tests.resources.helper_functions import get_publisher_account


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

    # make ocean instance
    ocn = Ocean()
    acc = get_publisher_account(config)
    if not acc:
        acc = ([acc for acc in ocn.accounts.list() if acc.password] or ocn.accounts.list())[0]

    # Register ddo
    ddo = ocn.assets.create(Metadata.get_example(), acc, providers=[acc.address], use_secret_store=False)
    logging.info(f'registered ddo: {ddo.did}')
    # ocn here will be used only to publish the asset. Handling the asset by the publisher
    # will be performed by the Brizo server running locally
    keeper = Keeper.get_instance()
    if 'TEST_LOCAL_NILE' in os.environ and os.environ['TEST_LOCAL_NILE'] == '1':
        provider = keeper.did_registry.to_checksum_address(
            '0x413c9ba0a05b8a600899b41b0c62dd661e689354'
        )
        keeper.did_registry.add_provider(ddo.asset_id, provider, acc)
        logging.debug(f'is did provider: '
                      f'{keeper.did_registry.is_did_provider(ddo.asset_id, provider)}')

    cons_ocn = Ocean()
    consumer_account = get_account_from_config(config, 'parity.address1', 'parity.password1')

    # sign agreement using the registered asset did above
    service = ddo.get_service(service_type=ServiceTypes.ASSET_ACCESS)
    # This will send the order request to Brizo which in turn will execute the agreement on-chain
    cons_ocn.accounts.request_tokens(consumer_account, 100)
    sa = ServiceAgreement.from_service_dict(service.as_dictionary())

    agreement_id = cons_ocn.assets.order(
        ddo.did, sa.service_definition_id, consumer_account)
    logging.info('placed order: %s, %s', ddo.did, agreement_id)
    i = 0
    while ocn.agreements.is_access_granted(
            agreement_id, ddo.did, consumer_account.address) is not True and i < 30:
        time.sleep(1)
        i += 1

    assert ocn.agreements.is_access_granted(agreement_id, ddo.did, consumer_account.address)

    ocn.assets.consume(
        agreement_id,
        ddo.did,
        sa.service_definition_id,
        consumer_account,
        config.downloads_path)
    logging.info('Success buying asset.')


if __name__ == '__main__':
    buy_asset()
