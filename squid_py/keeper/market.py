"""Keeper module to call keeper-contracts."""
import logging

from web3 import Web3

from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.exceptions import OceanDIDNotFound, OceanInvalidTransaction
from squid_py.keeper.contract_base import ContractBase


class Market(ContractBase):
    """Class representing the OceanMarket contract."""

    @staticmethod
    def get_instance():
        """Returns a ContractBase instance of the OceanMarket contract."""
        return Market('OceanMarket')

    def check_asset(self, asset_id):
        """
        Check that this particular asset is already registered on chain."

        :param asset_id: ID of the asset to check for existance
        :return: Boolean
        """
        asset_id_bytes = Web3.toBytes(hexstr=asset_id)
        return self.contract_concise.checkAsset(asset_id_bytes)

    def verify_order_payment(self, order_id):
        """Verify the payment of consumer is received by OceanMarket

        :param order_id: Order id, str
        :return: bool
        """
        return self.contract_concise.verifyPaymentReceived(order_id)

    def get_asset_price(self, asset_id):
        """
        Return the price of an asset already registered.

        :param asset_id: Asset id, str
        :return: Price, int
        """
        asset_id_bytes = Web3.toBytes(hexstr=asset_id)
        try:
            return self.contract_concise.getAssetPrice(asset_id_bytes)
        except OceanDIDNotFound:
            raise OceanDIDNotFound(f'There are no assets registered with id: {asset_id}')

    def request_tokens(self, amount, address):
        """
        Request an amount of tokens for a particular address.
        This transanction has gas cost

        :param amount: Amount of tokens, int
        :param address: Account address, str
        :raise OceanInvalidTransaction: Transaction failed
        :return: Tx receipt
        """
        try:
            receipt = self.contract_concise.requestTokens(amount, transact={'from': address})
            logging.debug(f'{address} requests {amount} tokens, returning receipt')
            return receipt
        except ValueError:
            raise OceanInvalidTransaction(f'Transaction on chain requesting {amount} tokens'
                                          f' to {address} failed.')

    def register_asset(self, asset, price, publisher_address):
        """
        Register an asset on chain.
        Calls the OceanMarket.register function.

        :param asset: Asset, DDO
        :param price: Price, int
        :param publisher_address: Publisher address, str
        """
        asset_id_bytes = Web3.toBytes(hexstr=asset.asset_id)
        assert asset_id_bytes
        assert len(asset_id_bytes) == 32
        # assert all(c in string.hexdigits for c in asset.asset_id)

        result = self.contract_concise.register(
            asset_id_bytes,
            price,
            transact={'from': publisher_address, 'gas': DEFAULT_GAS_LIMIT}
        )

        self.get_tx_receipt(result)
        logging.debug(f'Registered Asset {asset.asset_id} on chain.')
        return result
