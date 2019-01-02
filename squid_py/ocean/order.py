"""Ocean module."""
from .ocean_base import OceanBase


class Order(OceanBase):
    def __init__(self, order_id, asset, timeout, pub_key, key, paid, status):
        """
        Initialize an order.

        :param order_id: Order id, str.
        :param asset: Asset
        :param timeout: Timeout, int
        :param pub_key: Public key, str
        :param key: Key, str
        :param paid: Amount paid, int
        :param status: Status of this order, str
        """
        self.order_id = order_id
        self.asset = asset
        self.asset_id = self.asset.id
        self.timeout = timeout
        self.pub_key = pub_key
        self.key = key
        self.paid = paid
        self.status = status
        OceanBase.__init__(self, self.order_id)
