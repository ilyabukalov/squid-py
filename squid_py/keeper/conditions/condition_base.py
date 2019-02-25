from squid_py.keeper import ContractBase


class ConditionBase(ContractBase):
    """Base class for all the Condition contract objects."""

    def fulfill(self, *args, **kwargs):
        """
        Fulfill the condition.

        :param args:
        :param kwargs:
        :return: true if the condition was successfully fulfilled, bool
        """
        tx_hash = self.contract_concise.fulfill(*args, **kwargs)
        receipt = self.get_tx_receipt(tx_hash)
        return receipt.status == 1

    def abort_by_timeout(self, condition_id):
        """

        :param condition_id:
        :return:
        """
        tx_hash = self.contract_concise.abortByTimeOut(condition_id)
        receipt = self.get_tx_receipt(tx_hash)
        return receipt.status == 1

    def hash_values(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        return self.contract_concise.hashValues(*args, **kwargs)
