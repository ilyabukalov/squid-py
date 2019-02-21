"""Example of how to sign a service agreement in Ocean."""
import logging
import os
from time import sleep

from squid_py import ConfigProvider, Metadata, Ocean
from squid_py.agreements.service_types import ServiceTypes
from squid_py.examples.example_config import ExampleConfig
from squid_py.examples.helper_functions import get_account_from_config

if 'TEST_NILE' in os.environ and os.environ['TEST_NILE'] == '1':
    ASYNC_DELAY = 5  # seconds
else:
    ASYNC_DELAY = 1  # seconds


def sign_service_agreement():
    ConfigProvider.set_config(ExampleConfig.get_config())
    config = ConfigProvider.get_config()
    # make ocean instance and register an asset
    ocn = Ocean()
    acc = ([acc for acc in ocn.accounts.list() if acc.password] or ocn.accounts.list())[0]
    ddo = ocn.assets.create(Metadata.get_example(), acc)

    consumer_account = get_account_from_config(config, 'parity.address1', 'parity.password1')
    service = ddo.get_service(service_type=ServiceTypes.ASSET_ACCESS)
    agreement_id, signature = ocn.agreements.prepare(
        ddo.did,
        service.service_definition_id,
        consumer_account
    )

    sleep(ASYNC_DELAY)

    logging.info(f'service agreement signed: '
                 f'\nservice agreement id: {agreement_id}, '
                 f'\nsignature: {signature}')


if __name__ == '__main__':
    sign_service_agreement()
