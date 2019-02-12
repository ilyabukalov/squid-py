"""Keeper module to transact/call `AccessConditions` keeper contract methods."""

from squid_py.keeper.contract_base import ContractBase


class AccessConditions(ContractBase):
    """Class representing the AccessConditions contract."""

    @staticmethod
    def get_instance():
        """Returns a ContractBase instance of the AccessConditions contract."""
        return AccessConditions('AccessConditions')

    def check_permissions(self, address, asset_did):
        """
        Check permissions contract call.

        This method check that the account address has permission to access the asset represented
        for the asset_did.

        :param address: Account address, string
        :param asset_did: Asset did, str
        :param sender_address: Address that call the function, str
        :return: bool
        """
        return self.contract_concise.checkPermissions(address, asset_did)
