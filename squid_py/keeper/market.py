import logging

from squid_py.constants import OCEAN_MARKET_CONTRACT


class Market(object):

    def __init__(self, web3_helper):
        self.contract_concise = web3_helper.load(OCEAN_MARKET_CONTRACT, 'market')[0]
        self.contract = web3_helper.load(OCEAN_MARKET_CONTRACT, 'market')[1]
        self.defaultGas = 300000
        logging.info('Market contract loaded')

    # call functions (costs no gas)
    def check_asset(self, asset_id):
        """Check that this particular asset is already registered on chain."""
        return self.contract_concise.checkAsset(asset_id)

    def verify_order_payment(self, order_id):
        return self.contract_concise.verifyPaymentReceived(order_id)

    def get_asset_price(self, asset_id):
        """Return the price of an asset already registered."""
        try:
            return self.contract_concise.getAssetPrice(asset_id)
        except Exception:
            logging.error("There are no assets registered with id: %s" % asset_id)

    # Transactions with gas cost
    def request_tokens(self, amount, address):
        """Request an amount of tokens for a particular address."""
        try:
            self.contract_concise.requestTokens(amount, transact={'from': address})
            logging.info("Requesting %s tokens" % amount)
            return True
        except:
            return False

    def register_asset(self, name, description, price, publisher_address):
        """Register an asset on chain."""
        asset_id = self.contract_concise.generateId(name + description)
        result = self.contract_concise.register(
            asset_id,
            price,
            transact={'from': publisher_address, 'gas': self.defaultGas}
        )
        logging.info('registered: %s' % result)
        return asset_id

    def purchase_asset(self, asset_id, order, publisher_address, sender_address):
        asset_price = self.contract.getAssetPrice(asset_id)
        return self.contract.sendPayment(order.id, publisher_address, asset_price, order.timeout, {
            'from': sender_address,
            'gas': 2000000
        })

    def get_message_hash(self, message):
        pass

    def generate_did(self, content):
        pass

    def resolve_did(self, did):
        pass
