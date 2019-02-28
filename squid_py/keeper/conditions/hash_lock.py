from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.conditions.condition_base import ConditionBase


class HashLockCondition(ConditionBase):
    """Class representing the HashLockCondition contract."""
    CONTRACT_NAME = 'HashLockCondition'

    def fulfill(self, agreement_id, preimage, account):
        """

        :param agreement_id:
        :param preimage:
        :return:
        """
        return ConditionBase.fulfill(
            self,
            agreement_id,
            preimage,
            transact={'from': account.address, 'gas': DEFAULT_GAS_LIMIT}
        )

    def hash_values(self, preimage):
        """

        :param preimage:
        :return:
        """
        return ConditionBase.hash_values(self, preimage)
