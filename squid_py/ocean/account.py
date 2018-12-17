from collections import namedtuple

Balance = namedtuple('Balance', ('eth', 'ocn'))


class Account:
    def __init__(self, keeper, address, password=None):
        """
        Hold account address, and update balances of Ether and Ocean token

        :param keeper: The keeper instance
        :param address: The address of this account
        """
        self.keeper = keeper
        self.address = address
        self.password = password

    def unlock(self):
        if self.password:
            return self.keeper.web3.personal.unlockAccount(self.address, self.password)
        return False

    def request_tokens(self, amount):
        self.unlock()
        return self.keeper.market.request_tokens(amount, self.address)

    @property
    def balance(self):
        return Balance(self.ether_balance, self.ocean_balance)

    @property
    def ether_balance(self):
        """
        Call the Token contract method .web3.eth.getBalance()
        :return: Ether balance, int
        """
        return self.keeper.web3.eth.getBalance(self.address, block_identifier='latest')

    @property
    def ocean_balance(self):
        """
        Call the Token contract method .balanceOf(account_address)
        :return: Ocean token balance, int
        """
        return self.keeper.token.get_token_balance(self.address)
