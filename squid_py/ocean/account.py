"""Ocean module."""
import logging
from collections import namedtuple

from squid_py.keeper import Keeper
from squid_py.keeper.web3_provider import Web3Provider

Balance = namedtuple('Balance', ('eth', 'ocn'))

logger = logging.getLogger('account')


class Account:
    """Class representing an account."""

    def __init__(self, address, password=None):
        """
        Hold account address, and update balances of Ether and Ocean token.

        :param address: The address of this account
        :param password: account's password. This is necessary for unlocking account before doing
            a transaction.
        """
        self.address = address
        self.password = password

    def sign_hash(self, msg_hash):
        """
        Return signed hash using this user account keys.

        :param msg_hash:
        :return: signed hash
        """
        return Web3Provider.get_web3().eth.sign(self.address, msg_hash).hex()

    def unlock(self):
        """
        Unlock the account address using .web3.personal.unlockAccount(address, password).

        :return: Result of the operation, bool
        """
        if self.password:
            logger.debug(f'Unlocking account {self.address}')
            return Web3Provider.get_web3().personal.unlockAccount(self.address, self.password)
        logging.warning(f'Failed to unlock the account {self.address}')
        return False

    def request_tokens(self, amount):
        """
        Request an amount of tokens for the user account.

        :param amount: Amount of tokens, int
        :return: Result of the operation, bool
        """
        self.unlock()
        logger.info(f'Requesting {amount} tokens.')
        return Keeper.get_instance().market.request_tokens(amount, self.address)

    @property
    def balance(self):
        """
        Call for the balance of the account.

        :return: Tuple with the ether balance and the ocean tokens balance, (int, int)
        """
        return Balance(self.ether_balance, self.ocean_balance)

    @property
    def ether_balance(self):
        """
        Call the Token contract method .web3.eth.getBalance().

        :return: Ether balance, int
        """
        return Web3Provider.get_web3().eth.getBalance(self.address, block_identifier='latest')

    @property
    def ocean_balance(self):
        """
        Call the Token contract method .balanceOf(account_address).

        :return: Ocean token balance, int
        """
        return Keeper.get_instance().token.get_token_balance(self.address)
