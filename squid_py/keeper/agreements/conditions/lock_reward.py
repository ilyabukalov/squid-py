from squid_py.keeper.agreements.conditions.condition_base import ConditionBase


class LockRewardCondition(ConditionBase):
    def fulfill(self, agreement_id, reward_address, amount):
        return super(self).fulfill(
            agreement_id,
            reward_address,
            amount
        )

    def hash_values(self, reward_address, amount):
        return super(self).hash_values(reward_address, amount)
