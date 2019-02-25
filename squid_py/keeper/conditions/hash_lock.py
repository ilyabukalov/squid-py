from squid_py.keeper.conditions.condition_base import ConditionBase


class HashLockCondition(ConditionBase):
    """Class representing the HashLockCondition contract."""
    CONTRACT_NAME = 'HashLockCondition'

    def fulfill(self, agreement_id, preimage):
        """

        :param agreement_id:
        :param preimage:
        :return:
        """
        return super(self).fulfill(
            agreement_id,
            preimage,
        )

    def hash_values(self, preimage):
        """

        :param preimage:
        :return:
        """
        return super(self).hash_values(preimage)
