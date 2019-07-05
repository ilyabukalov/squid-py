#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import os
from time import sleep

from ocean_commons.ddo.metadata import Metadata

from examples import ExampleConfig
from squid_py import Ocean
from ocean_commons.config_provider import ConfigProvider


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
