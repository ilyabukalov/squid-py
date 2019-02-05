"""Keeper module to call keeper-contracts."""

from squid_py.keeper.contract_base import ContractBase
from squid_py.keeper.web3_provider import Web3Provider


class Token(ContractBase):
    """Class representing the Token contract."""

    @staticmethod
    def get_instance():
        """Returns a ContractBase instance of the OceanToken contract."""
        return Token('OceanToken')

    def get_token_balance(self, account_address):
        """
        Retrieve the amount of tokens of an account address.

        :param account_address: Account address, str
        :return: int
        """
        return self.contract_concise.balanceOf(account_address)

    def get_allowance(self, owner_address, spender_address):
        """

        :param owner_address:
        :param spender_address:
        :return:
        """
        return self.contract_concise.allowance(owner_address, spender_address)

    def token_approve(self, spender_address, price, from_account):
        """
        Approve the passed address to spend the specified amount of tokens.

        :param spender_address: Account address, str
        :param price: Price, int
        :param from_account: Account address, str
        :return:
        """
        if not Web3Provider.get_web3().isChecksumAddress(spender_address):
            spender_address = Web3Provider.get_web3().toChecksumAddress(spender_address)

        return self.contract_concise.approve(
            spender_address,
            price,
            transact={'from': from_account.address}
        )

    def transfer(self, receiver_address, amount, from_account):
        return self.contract_concise.transfer(
            receiver_address,
            amount,
            transact={'from': from_account.address}
        )
