"""Keeper module to call keeper-contracts."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from web3.utils.threads import Timeout

from squid_py.exceptions import OceanInvalidTransaction
from squid_py.keeper.contract_base import ContractBase
from squid_py.keeper.event_filter import EventFilter
from squid_py.keeper.web3_provider import Web3Provider


class GenericContract(ContractBase):
    """Class for instantiating any contract.

    Contract name is set at time of loading the contract.

    """

