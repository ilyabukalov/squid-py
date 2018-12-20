"""Keeper module to call keeper-contracts."""

from squid_py.keeper.contract_base import ContractBase


class Token(ContractBase):
    """Class representing the Token contract."""

    def __init__(self, web3, contract_path):
        """

        :param web3:
        :param contract_path:
        """
        ContractBase.__init__(self, web3, contract_path, 'OceanToken')

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

        :param spender_address:
        :param price:
        :param from_account:
        :return:
        """
        if not self.web3.isChecksumAddress(spender_address):
            spender_address = self.web3.toChecksumAddress(spender_address)

        from_account.unlock()
        return self.contract_concise.approve(spender_address,
                                             price,
                                             transact={'from': from_account.address}
                                             )
