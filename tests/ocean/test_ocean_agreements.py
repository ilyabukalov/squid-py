#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from unittest.mock import MagicMock, Mock

import pytest

from squid_py import ConfigProvider
from squid_py.agreements.service_agreement_template import ServiceAgreementTemplate
from squid_py.agreements.service_types import ServiceTypes
from squid_py.assets.asset_consumer import AssetConsumer
from squid_py.keeper import Keeper
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.ocean.ocean_agreements import OceanAgreements
from tests.resources.helper_functions import get_consumer_account, get_ddo_sample
from tests.resources.tiers import e2e_test


@pytest.fixture
def ocean_agreements():
    keeper = Keeper.get_instance()
    w3 = Web3Provider.get_web3()
    did_resolver = Mock()
    ddo = get_ddo_sample()
    service = ddo.get_service(ServiceTypes.ASSET_ACCESS)
    service.update_value(
        ServiceAgreementTemplate.TEMPLATE_ID_KEY,
        w3.toChecksumAddress("0x00bd138abd70e2f00903268f3db08f2d25677c9e")
    )
    did_resolver.resolve = MagicMock(return_value=ddo)
    consumer_class = Mock
    consumer_class.download = MagicMock(return_value='')
    return OceanAgreements(
        keeper,
        did_resolver,
        AssetConsumer,
        ConfigProvider.get_config()
    )


def test_prepare_agreement(ocean_agreements):
    consumer_account = get_consumer_account(ConfigProvider.get_config())
    ddo = get_ddo_sample()
    ocean_agreements.prepare(ddo.did, ServiceTypes.ASSET_ACCESS, consumer_account)
    # :TODO:


def test_send_agreement(ocean_agreements):
    pass


def test_create_agreement(ocean_agreements):
    pass


@e2e_test
def test_agreement_release_reward():
    pass


@e2e_test
def test_agreement_refund_reward():
    pass
