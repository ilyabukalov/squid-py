"""Ocean module."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from collections import namedtuple

from ocean_keeper.account import Account
from ocean_keeper.utils import get_account

Balance = namedtuple('Balance', ('eth', 'ocn'))


class OceanAccounts:
    """Ocean accounts class."""

    def __init__(self, keeper, config, ocean_tokens):
        self._keeper = keeper
        self._config = config
        self._ocean_tokens = ocean_tokens
        self._accounts = []
        addresses = [account_address for account_address in self._keeper.accounts]
        for address in addresses:
            for account in [get_account(0), get_account(1)]:
                if account and account.address.lower() == address.lower():
                    self._accounts.append(account)
                    break

    @property
    def accounts_addresses(self):
        """
        Return a list with the account addresses.

        :return: list
        """
        return [a.address for a in self._accounts]

    def list(self):
        """
        Return list of Account instances available in the current ethereum node

        :return: list of Account instances
        """
        return self._accounts[:]

    def balance(self, account):
        """
        Return the balance, a tuple with the eth and ocn balance.

        :param account: Account instance to return the balance of
        :return: Balance tuple of (eth, ocn)
        """
        return Balance(self._keeper.get_ether_balance(account.address),
                       self._keeper.token.get_token_balance(account.address))

    def request_tokens(self, account, amount):
        """
        Request an amount of ocean tokens for an account.

        :param account: Account instance making the tokens request
        :param amount: int amount of tokens requested
        :raises OceanInvalidTransaction: if transaction fails
        :return: bool
        """
        return self._ocean_tokens.request(account, amount)
