import os

import pytest
from web3 import Web3, HTTPProvider

from squid_py.config import Config
from tests.utils import get_registered_ddo, get_consumer_ocean_instance, get_publisher_ocean_instance


@pytest.fixture
def publisher_ocean_instance():
    return get_publisher_ocean_instance()


@pytest.fixture
def consumer_ocean_instance():
    return get_consumer_ocean_instance()


@pytest.fixture
def registered_ddo():
    return get_registered_ddo(get_publisher_ocean_instance())


@pytest.fixture
def web3_instance():
    path_config = 'config_local.ini'
    os.environ['CONFIG_FILE'] = path_config
    config = Config(path_config)
    return Web3(HTTPProvider(config.keeper_url))
