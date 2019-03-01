from squid_py.keeper import ContractBase, utils
from squid_py.keeper.web3_provider import Web3Provider


class ConditionBase(ContractBase):
    """Base class for all the Condition contract objects."""
    FULFILLED_EVENT = 'Fulfilled'

    def generate_id(self, agreement_id, types, values):
        values_hash = utils.generate_multi_value_hash(types, values)
        return utils.generate_multi_value_hash(
            ['bytes32', 'address', 'bytes32'],
            [agreement_id, self.address, values_hash]
        )

    def _fulfill(self, *args, **kwargs):
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

    def _hash_values(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        return self.contract_concise.hashValues(*args, **kwargs)

    def subscribe_condition_fulfilled(self, agreement_id, timeout, callback, args,
                                      timeout_callback=None, wait=False):
        return self.subscribe_to_event(
            self.FULFILLED_EVENT,
            timeout,
            {'_agreementId': Web3Provider.get_web3().toBytes(hexstr=agreement_id)},
            callback=callback,
            timeout_callback=timeout_callback,
            args=args,
            wait=wait
        )
