"""
    Test config class

"""

import os

from squid_py.config import (
    Config,
)

test_config_text = """

[keeper-contracts]

market.address = test_market_address
auth.address = test_auth_address
token.address = test_token_address
keeper.url = test_keeper_url
keeper.path = test_keeper_path
gas_limit = 200
aquarius.url = test_aquarius_url

"""


def test_load():
    config = Config(filename='./resources/config_test.ini')
    assert config
    assert config.gas_limit == 200
    assert config.keeper_url == 'test_keeper_url'
    if os.getenv('VIRTUAL_ENV'):
        assert config.keeper_path == os.path.join(os.getenv('VIRTUAL_ENV'), 'artifacts')
    else:
        assert config.keeper_path == '/usr/contracts'
