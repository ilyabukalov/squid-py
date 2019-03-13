"""
    Test Keeper class.

    This tests basic contract loading and one call to the smart contract to prove
    that the contact can be loaded and used

"""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from squid_py.keeper import Keeper
from tests.resources.tiers import e2e_test


@e2e_test
def test_keeper_instance():
    keeper = Keeper()
    assert keeper
    assert isinstance(keeper.get_instance(), Keeper)


@e2e_test
def test_keeper_networks():
    keeper = Keeper()
    assert isinstance(keeper.get_network_id(), int)
    assert keeper.get_network_name(1) == Keeper._network_name_map.get(1)
    assert keeper.get_network_name(2) == Keeper._network_name_map.get(2)
    assert keeper.get_network_name(3) == Keeper._network_name_map.get(3)
    assert keeper.get_network_name(4) == Keeper._network_name_map.get(4)
    assert keeper.get_network_name(42) == Keeper._network_name_map.get(42)
    assert keeper.get_network_name(77) == Keeper._network_name_map.get(77)
    assert keeper.get_network_name(99) == Keeper._network_name_map.get(99)
    assert keeper.get_network_name(8995) == Keeper._network_name_map.get(8995)
    assert keeper.get_network_name(8996) == Keeper._network_name_map.get(8996)
    assert keeper.get_network_name(0) == 'development'
