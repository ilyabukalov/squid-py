"""Test Market contract."""
import secrets

import pytest

from squid_py.config_provider import ConfigProvider
from squid_py.ddo.ddo import DDO
from squid_py.exceptions import OceanInvalidTransaction
from squid_py.keeper.market import Market
from tests.conftest import get_consumer_account
from tests.resources.helper_functions import get_resource_path, get_publisher_account
from tests.resources.tiers import e2e_test

market = Market('OceanMarket')


@e2e_test
def test_market_contract():
    assert market
    assert isinstance(market, Market), f'{market} is not instance of Market'


@e2e_test
def test_check_asset_no_registered():
    test_id = secrets.token_hex(32)
    assert not market.check_asset(test_id)


@e2e_test
def test_check_assets_no_valid():
    with pytest.raises(Exception):
        market.check_asset('no valid')


@e2e_test
def test_check_assets_registered():
    sample_ddo_path = get_resource_path('ddo', 'ddo_sample2.json')
    asset = DDO(json_filename=sample_ddo_path)
    market.register_asset(asset, 100,
                          get_publisher_account(ConfigProvider.get_config()).address)
    assert market.check_asset(asset.asset_id), f'{asset.asset_id} is not registered.'


@e2e_test
def test_verify_order_payment():
    test_id = secrets.token_hex(32)
    assert market.verify_order_payment(test_id)


@e2e_test
def test_get_asset_price():
    assert market.get_asset_price(secrets.token_hex(32)) == 0
    sample_ddo_path = get_resource_path('ddo', 'ddo_sample2.json')
    asset = DDO(json_filename=sample_ddo_path)
    market.register_asset(asset, 100,
                          get_publisher_account(ConfigProvider.get_config()).address)
    assert market.get_asset_price(asset.asset_id), f'{asset.asset_id} price is not correct.'


@e2e_test
def test_get_asset_price_no_valid_asset():
    with pytest.raises(Exception):
        market.get_asset_price('not valid')


@e2e_test
def test_request_tokens():
    account = get_consumer_account(ConfigProvider.get_config())
    account.unlock()
    assert market.request_tokens(100, account.address), f'{account.address} do not get 100 tokens.'


@e2e_test
def test_request_tokens_with_locked_account():
    with pytest.raises(OceanInvalidTransaction):
        market.request_tokens(100, get_consumer_account(ConfigProvider.get_config()).address)


@e2e_test
def test_register_asset():
    sample_ddo_path = get_resource_path('ddo', 'ddo_sample2.json')
    asset = DDO(json_filename=sample_ddo_path)
    assert market.register_asset(asset, 100,
                                 get_publisher_account(
                                     ConfigProvider.get_config()).address), \
        f'{asset} asset is not registered.'


@e2e_test
def test_register_invalid_asset():
    asset = DDO()
    with pytest.raises(ValueError):
        market.register_asset(asset, 100,
                              get_publisher_account(
                                  ConfigProvider.get_config()).address)
