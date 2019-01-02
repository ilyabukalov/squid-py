"""Keeper module to call keeper-contracts."""
import logging

from web3 import Web3

from squid_py.exceptions import OceanDIDNotFound, OceanInvalidTransaction
from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.contract_base import ContractBase


class Market(ContractBase):
    """Class representing the OceanMarket contract."""

    def __init__(self, web3, contract_path):
        ContractBase.__init__(self, web3, contract_path, 'OceanMarket')
        self._defaultGas = DEFAULT_GAS_LIMIT

    # call functions (costs no gas)
    def check_asset(self, asset_id):
        """
        Check that this particular asset is already registered on chain."

        :param asset_id: ID of the asset to check for existance
        :return: Boolean
        """
        asset_id_bytes = Web3.toBytes(hexstr=asset_id)
        return self.contract_concise.checkAsset(asset_id_bytes)

    def verify_order_payment(self, order_id):
        return self.contract_concise.verifyPaymentReceived(order_id)

    def get_asset_price(self, asset_id):
        """Return the price of an asset already registered."""
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
        except OceanInvalidTransaction:
            raise OceanInvalidTransaction(f'Transaction on chain requesting {amount} tokens'
                                          f' to {address} failed.')

    def register_asset(self, asset, price, publisher_address):
        """
        Register an asset on chain.
        Calls the OceanMarket.register function.

        :param asset:
        :param price:
        :param publisher_address:
        """
        asset_id_bytes = Web3.toBytes(hexstr=asset.asset_id)
        assert asset_id_bytes
        assert len(asset_id_bytes) == 32
        # assert all(c in string.hexdigits for c in asset.asset_id)

        result = self.contract_concise.register(
            asset_id_bytes,
            price,
            transact={'from': publisher_address, 'gas': self._defaultGas}
        )

        self.get_tx_receipt(result)
        logging.debug(f'Registered Asset {asset.asset_id} on chain.')
        return result

    def pay_order(self, order_id, publisher_address, price, timeout, sender_address,
                  gas_amount=None):
        """

        :param order_id:
        :param publisher_address:
        :param price:
        :param timeout:
        :param sender_address:
        :param gas_amount:
        :return:
        """
        tx_hash = self.contract_concise.sendPayment(order_id, publisher_address, price, timeout, {
            'from': sender_address,
            'gas': gas_amount if gas_amount else self._defaultGas
        })
        return self.get_tx_receipt(tx_hash)

    def purchase_asset(self, asset_id, order, publisher_address, sender_address):
        """

        :param asset_id:
        :param order:
        :param publisher_address:
        :param sender_address:
        :return:
        """
        asset_id_bytes = Web3.toBytes(hexstr=asset_id)
        asset_price = self.contract_concise.getAssetPrice(asset_id_bytes)
        return self.contract_concise.sendPayment(order.id, publisher_address, asset_price,
                                                 order.timeout, {
                                                     'from': sender_address,
                                                     'gas': self._defaultGas
                                                 })

    def calculate_message_hash(self, message):
        """

        :param message:
        :return:
        """
        return self.contract_concise.generateId(message)
