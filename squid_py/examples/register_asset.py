"""Example of register and asset in Ocean."""
import logging
import os
from time import sleep

from squid_py import Metadata, Ocean
from squid_py.config_provider import ConfigProvider
from squid_py.examples.example_config import ExampleConfig

if 'TEST_NILE' in os.environ and os.environ['TEST_NILE'] == '1':
    ASYNC_DELAY = 5  # seconds
else:
    ASYNC_DELAY = 1  # seconds


def register_asset():
    # make ocean instance
    ConfigProvider.set_config(ExampleConfig.get_config())
    ocn = Ocean()
    account = ([acc for acc in ocn.accounts.list() if acc.password] or ocn.accounts.list())[0]
    ddo = ocn.assets.create(Metadata.get_example(), account)

    sleep(ASYNC_DELAY)

    logging.info(f'Registered asset: did={ddo.did}, ddo-services={ddo.services}')
    resolved_ddo = ocn.assets.resolve(ddo.did)
    logging.info(f'resolved asset ddo: did={resolved_ddo.did}, ddo={resolved_ddo.as_text()}')


if __name__ == '__main__':
    register_asset()
