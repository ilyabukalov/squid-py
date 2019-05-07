#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import os

import sys

from squid_py import Config


def get_variable_value(variable):
    if os.getenv(variable) is None:
        logging.error(f'you should provide a {variable}')
        sys.exit(1)
    else:
        return os.getenv(variable)


class ExampleConfig:
    @staticmethod
    def get_config_net():
        return os.environ.get('TEST_NET', 'spree')

    @staticmethod
    def get_env_name():
        net = ExampleConfig.get_config_net()
        if net == 'nile':
            return 'TEST_NILE'
        elif net == 'nile_local':
            return 'TEST_LOCAL_NILE'
        elif net == 'duero':
            return 'TEST_DUERO'
        elif net == 'duero_local':
            return 'TEST_LOCAL_DUERO'
        elif net == 'spree':
            return 'TEST_LOCAL_SPREE'

        return None

    @staticmethod
    def get_remote_parity_addresses():
        return (
            get_variable_value('PARITY_ADDRESS'),
            get_variable_value('PARITY_PASSWORD'),
            get_variable_value('PARITY_ADDRESS1'),
            get_variable_value('PARITY_PASSWORD1')
        )

    @staticmethod
    def get_local_parity_addresses():
        return (
            "0x00bd138abd70e2f00903268f3db08f2d25677c9e", "node0",
            "0x068ed00cf0441e4829d9784fcbe7b9e26d4bd8d0", "secret"
        )

    @staticmethod
    def get_config_dict():
        test_net = ExampleConfig.get_config_net()

        if test_net == 'nile':
            a, p, a1, p1 = ExampleConfig.get_remote_parity_addresses()
            keeper_url = "https://nile.dev-ocean.com"
            ss_url = "https://secret-store.dev-ocean.com"
            aqua_url = "https://nginx-aquarius.dev-ocean.com/"
            brizo_url = "https://nginx-brizo.dev-ocean.com/"

        elif test_net == 'nile_local':
            # As above, but uses local nile node instead of connecting directly to the remote node.
            # This is actually the recommended method in practical use cases.
            a, p, a1, p1 = ExampleConfig.get_local_parity_addresses()
            keeper_url = "http://localhost:8545"
            ss_url = "https://secret-store.dev-ocean.com"
            aqua_url = "https://nginx-aquarius.dev-ocean.com/"
            brizo_url = "https://nginx-brizo.dev-ocean.com/"
        elif test_net == 'duero':
            a, p, a1, p1 = ExampleConfig.get_remote_parity_addresses()
            keeper_url = "https://duero.dev-ocean.com"
            ss_url = "https://secret-store.duero.dev-ocean.com"
            aqua_url = "https://nginx-aquarius.dev-ocean.com/"
            brizo_url = "http://localhost:8030"
        elif test_net == 'duero_local':
            a, p, a1, p1 = ExampleConfig.get_remote_parity_addresses()
            keeper_url = "http://localhost:8545"
            ss_url = "https://secret-store.duero.dev-ocean.com"
            aqua_url = "https://nginx-aquarius.dev-ocean.com/"
            brizo_url = "http://localhost:8030"
        else:  # test_net == 'spree':
            a, p, a1, p1 = ExampleConfig.get_local_parity_addresses()
            keeper_url = "http://localhost:8545"
            ss_url = "http://localhost:12001"
            aqua_url = "http://172.15.0.15:5000"
            brizo_url = "http://localhost:8030"

        return {
            "keeper-contracts": {
                "keeper.url": keeper_url,
                "keeper.path": "artifacts",
                "secret_store.url": ss_url,
                "parity.url": keeper_url,
                "parity.address": a,
                "parity.password": p,
                "parity.address1": a1,
                "parity.password1": p1
            },
            "resources": {
                "aquarius.url": aqua_url,
                "brizo.url": brizo_url,
                "storage.path": "squid_py.db",
                "downloads.path": "consume-downloads"
            }
        }

    @staticmethod
    def get_config():
        logging.info("Configuration loaded for environment '{}'"
                     .format(ExampleConfig.get_config_net()))
        return Config(options_dict=ExampleConfig.get_config_dict())
