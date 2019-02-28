from unittest.mock import Mock, MagicMock

import pytest

from squid_py import ConfigProvider
from squid_py.assets.asset_consumer import AssetConsumer
from squid_py.ocean.ocean_agreements import OceanAgreements
from tests.resources.helper_functions import get_consumer_account, get_ddo_sample


@pytest.fixture
def ocean_agreements():
    keeper = Mock()
    did_resolver = Mock()
    did_resolver.resolve = MagicMock(return_value=get_ddo_sample())
    consumer_class = Mock
    consumer_class.download = MagicMock(return_value='')
    return OceanAgreements(
        keeper,
        did_resolver,
        AssetConsumer,
        ConfigProvider.get_config()
    )


def test_prepare_agreement(ocean_agreements):
    consumer_account = get_consumer_account()
    did = get_ddo_sample().did
    ocean_agreements.prepare(did, '1', consumer_account)
    # :TODO:

def test_send_agreement(ocean_agreements):
    pass


def test_create_agreement(ocean_agreements):
    pass
