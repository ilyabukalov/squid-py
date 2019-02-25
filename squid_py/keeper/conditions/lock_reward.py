from squid_py.keeper.conditions.condition_base import ConditionBase


class LockRewardCondition(ConditionBase):
    """Class representing the LockRewardCondition contract."""
    CONTRACT_NAME = 'LockRewardCondition'

    def fulfill(self, agreement_id, reward_address, amount):
        """

        :param agreement_id:
        :param reward_address:
        :param amount:
        :return:
        """
        return super(self).fulfill(
            agreement_id,
            reward_address,
            amount
        )

    def hash_values(self, reward_address, amount):
        """

        :param reward_address:
        :param amount:
        :return:
        """
        return super(self).hash_values(reward_address, amount)
