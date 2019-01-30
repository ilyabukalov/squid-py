from squid_py.accounts.account import Account


class OceanAccounts:
    def __init__(self, ocean):
        self._ocean = ocean

    def list(self):
        accounts_dict = dict()
        for account_address in self._ocean._keeper.accounts:
            accounts_dict[account_address] = Account(account_address)
        return accounts_dict
