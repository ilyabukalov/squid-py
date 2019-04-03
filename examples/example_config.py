#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import os

from squid_py import Config

def get_variable_value(variable):
    if os.getenv(variable) is None:
        logging.error(f'you should provide a {variable}')
        os._exit(1)
    else:
        return os.getenv(variable)

class ExampleConfig:
    if 'TEST_NILE' in os.environ and os.environ['TEST_NILE'] == '1':
        environment = 'TEST_NILE'
        parity_address = get_variable_value('PARITY_ADDRESS')
        parity_password = get_variable_value('PARITY_PASSWORD')
        parity_address1 = get_variable_value('PARITY_ADDRESS1')
        parity_password1 = get_variable_value('PARITY_PASSWORD1')
        config_dict = {
            "keeper-contracts": {
                "keeper.url": "https://nile.dev-ocean.com",
                "keeper.path": "artifacts",
                "secret_store.url": "https://secret-store.dev-ocean.com",
                "parity.url": "https://nile.dev-ocean.com",
                "parity.address": parity_address,
                "parity.password": parity_password,
                "parity.address1": parity_address1,
                "parity.password1": parity_password1
            },
            "resources": {
                "aquarius.url": "https://nginx-aquarius.dev-ocean.com/",
                "brizo.url": "https://nginx-brizo.dev-ocean.com/",
                "storage.path": "squid_py.db",
                "downloads.path": "consume-downloads"
            }
        }
    elif 'TEST_LOCAL_NILE' in os.environ and os.environ['TEST_LOCAL_NILE'] == '1':
        # As above, but uses local nile node instead of connecting directly to the remote node.
        # This is actually the recommended method in practical use cases.
        environment = 'TEST_LOCAL_NILE'
        config_dict = {
            "keeper-contracts": {
                "keeper.url": "http://localhost:8545",
                "keeper.path": "artifacts",
                "secret_store.url": "https://secret-store.dev-ocean.com",
                "parity.url": "http://localhost:8545",
                "parity.address": "0x00bd138abd70e2f00903268f3db08f2d25677c9e",
                "parity.password": "node0",
                "parity.address1": "0x068ed00cf0441e4829d9784fcbe7b9e26d4bd8d0",
                "parity.password1": "secret"
            },
            "resources": {
                "aquarius.url": "https://nginx-aquarius.dev-ocean.com/",
                "brizo.url": "https://nginx-brizo.dev-ocean.com/",
                "storage.path": "squid_py.db",
                "downloads.path": "consume-downloads"
            }
        }
    else:
        environment = 'TEST_LOCAL_SPREE'
        config_dict = {
            "keeper-contracts": {
                "keeper.url": "http://localhost:8545",
                "keeper.path": "artifacts",
                "secret_store.url": "http://localhost:12001",
                "parity.url": "http://localhost:8545",
                "parity.address": "0x00bd138abd70e2f00903268f3db08f2d25677c9e",
                "parity.password": "node0",
                "parity.address1": "0x068ed00cf0441e4829d9784fcbe7b9e26d4bd8d0",
                "parity.password1": "secret"
            },
            "resources": {
                "aquarius.url": "http://172.15.0.15:5000",
                "brizo.url": "http://localhost:8030",
                "storage.path": "squid_py.db",
                "downloads.path": "consume-downloads"
            }
        }

    @staticmethod
    def get_config():
        logging.info("Configuration loaded for environment '{}'".format(ExampleConfig.environment))
        return Config(options_dict=ExampleConfig.config_dict)


