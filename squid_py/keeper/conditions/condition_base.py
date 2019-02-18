from squid_py.keeper import ContractBase


class ConditionBase(ContractBase):
    def fulfill(self, *args, **kwargs):
        tx_hash = self.contract_concise.fulfill(*args, **kwargs)
        receipt = self.get_tx_receipt(tx_hash)
        return receipt.status == 1

    def abort_by_timeout(self, condition_id):
        tx_hash = self.contract_concise.abortByTimeOut(condition_id)
        receipt = self.get_tx_receipt(tx_hash)
        return receipt.status == 1

    def hash_values(self, *args, **kwargs):
        return self.contract_concise.hashValues(*args, **kwargs)
