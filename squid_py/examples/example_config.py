"""Examples of dictionary configs to work in Nile and Spree."""
import logging
import os

from squid_py import Config


class ExampleConfig:
    if 'TEST_NILE' in os.environ and os.environ['TEST_NILE'] == '1':
        environment = 'TEST_NILE'
        config_dict = {
            "keeper-contracts": {
                "keeper.url": "https://nile.dev-ocean.com",
                "keeper.path": "artifacts",
                "secret_store.url": "https://secret-store.dev-ocean.com",
                "parity.url": "https://nile.dev-ocean.com",
                "parity.address": "0x413c9ba0a05b8a600899b41b0c62dd661e689354",
                "parity.password": "ocean_secret",
                "parity.address1": "0x064789569D09b4d40b54383d84A25A840E5D67aD",
                "parity.password1": "ocean_secret"
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
