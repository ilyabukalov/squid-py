"""Ocean module."""
from .ocean_base import OceanBase


class Order(OceanBase):
    def __init__(self, order_id, asset, timeout, pub_key, key, paid, status):
        self.order_id = order_id
        self.asset = asset
        self.asset_id = self.asset.id
        self.timeout = timeout
        self.pub_key = pub_key
        self.key = key
        self.paid = paid
        self.status = status
        OceanBase.__init__(self, self.order_id)

    def get_status(self):
        return self.status

    def verify_payment(self):
        return self.paid

    def pay(self):
        return self.status

    def commit(self):
        return self.status

    def consume(self):
        return self.status
