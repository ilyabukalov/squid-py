from squid_py.keeper.conditions.condition_base import ConditionBase


class HashLockCondition(ConditionBase):
    CONTRACT_NAME = 'HashLockCondition'

    def fulfill(self, agreement_id, preimage):
        return super(self).fulfill(
            agreement_id,
            preimage,
        )

    def hash_values(self, preimage):
        return super(self).hash_values(preimage)
