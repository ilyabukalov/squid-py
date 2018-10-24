"""
    Test ocean class
"""

import logging
import os
from squid_py.ocean import Ocean

import json
import pathlib

SAMPLE_METADATA_PATH = pathlib.Path.cwd() / 'tests/resources/ddo' / 'sample_metadata1.json'
assert SAMPLE_METADATA_PATH.exists(), "{} does not exist!".format(SAMPLE_METADATA_PATH)
with open(SAMPLE_METADATA_PATH) as f:
    SAMPLE_METADATA = json.load(f)

# Disable low level loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)


def test_register_data():
    logging.debug("".format())
    ocean = Ocean('config_local.ini')
    asset_price = 100

    ##########################################################
    # Setup 2 accounts
    ##########################################################
    provider_address = list(ocean.accounts)[0]
    consumer_address = list(ocean.accounts)[1]
    provider_acct = ocean.accounts[provider_address]
    consumer_acct = ocean.accounts[consumer_address]

    # ensure Ocean token balance
    if provider_acct.ocean == 0:
        rcpt = provider_acct.request_tokens(200)
        ocean._web3.eth.waitForTransactionReceipt(rcpt)
    if consumer_acct.ocean == 0:
        rcpt = consumer_acct.request_tokens(200)
        ocean._web3.eth.waitForTransactionReceipt(rcpt)

    # You will need some token to make this transfer!
    assert provider_acct.ocean > 0
    assert consumer_acct.ocean > 0
    ##########################################################
    # Register
    ##########################################################
    asset_id = ocean.keeper.market.register_asset(SAMPLE_METADATA['base']['name'], SAMPLE_METADATA['base']['description'], asset_price, provider_acct.address)


    # Check exists
    chain_asset_exists = ocean.keeper.market.check_asset(asset_id)
    logging.info("check_asset = {}".format(chain_asset_exists))
    assert chain_asset_exists

    # Check price
    chain_asset_price = ocean.keeper.market.get_asset_price(asset_id)
    assert asset_price == chain_asset_price
    logging.info("chain_asset_price = {}".format(chain_asset_price))

def test_check_data():

    pass