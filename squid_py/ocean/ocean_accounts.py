from collections import namedtuple

from squid_py.accounts.account import Account

Balance = namedtuple('Balance', ('eth', 'ocn'))


class OceanAccounts:
    def __init__(self, keeper, config):
        self._keeper = keeper
        self._config = config
        self._accounts = [Account(account_address) for account_address in self._keeper.accounts]
        if config.parity_address and config.parity_password:
            address = config.parity_address.lower()
            for account in self._accounts:
                if account.address.lower() == address:
                    account.password = config.parity_password

    def list(self):
        return self._accounts[:]

    def balance(self, account):
        return Balance(self._keeper.get_ether_balance(account.address),
                       self._keeper.token.get_token_balance(account.address))

    def request_tokens(self, account, amount):
        return self._keeper.dispenser.request_tokens(amount, account.address)
