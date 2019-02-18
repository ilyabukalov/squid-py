"""
Example of a buying an asset.
"""
import logging
import os
import time

from squid_py import ConfigProvider, Metadata, Ocean
from squid_py.agreements.service_types import ServiceTypes
from squid_py.examples.example_config import ExampleConfig
from squid_py.keeper.event_listener import EventListener
from squid_py.keeper.web3_provider import Web3Provider
from tests.resources.helper_functions import get_account_from_config


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
    w3 = Web3Provider.get_web3()

    # make ocean instance
    ocn = Ocean()
    acc = ([acc for acc in ocn.accounts.list() if acc.password] or ocn.accounts.list())[0]

    # Register ddo
    ocn.templates.create(ocn.templates.access_template_id, acc)
    ddo = ocn.assets.create(Metadata.get_example(), acc)
    logging.info(f'registered ddo: {ddo.did}')
    # ocn here will be used only to publish the asset. Handling the asset by the publisher
    # will be performed by the Brizo server running locally

    cons_ocn = Ocean()
    consumer_account = get_account_from_config(config, 'parity.address1', 'parity.password1')

    # sign agreement using the registered asset did above
    service = ddo.get_service(service_type=ServiceTypes.ASSET_ACCESS)
    # This will send the purchase request to Brizo which in turn will execute the agreement on-chain
    cons_ocn.accounts.request_tokens(consumer_account, 100)

    time.sleep(ASYNC_DELAY)

    service_agreement_id = cons_ocn.assets.order(
        ddo.did, service.service_definition_id, consumer_account)

    _filter = {'agreementId': w3.toBytes(hexstr=service_agreement_id)}

    EventListener('ServiceExecutionAgreement', 'AgreementInitialized', filters=_filter).listen_once(
        _log_event('AgreementInitialized'),
        10,
        blocking=True
    )
    EventListener('AccessConditions', 'AccessGranted', filters=_filter).listen_once(
        _log_event('AccessGranted'),
        10,
        blocking=True
    )
    event = EventListener('ServiceExecutionAgreement', 'AgreementFulfilled',
                          filters=_filter).listen_once(
        _log_event('AgreementFulfilled'),
        10,
        blocking=True
    )
    time.sleep(10)

    ocn.agreements.is_access_granted(service_agreement_id, ddo.did, consumer_account.address)

    assert event, 'No event received for ServiceAgreement Fulfilled.'
    logging.info('Success buying asset.')


if __name__ == '__main__':
    buy_asset()
