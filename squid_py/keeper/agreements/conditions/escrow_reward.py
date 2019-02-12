from squid_py.keeper.agreements.conditions.condition_base import ConditionBase


class EscrowRewardCondition(ConditionBase):
    def fulfill(
            self,
            agreement_id,
            amount,
            receiver_address,
            sender_address,
            lock_condition_id,
            release_condition_id
    ):
        return super(self).fulfill(
            agreement_id,
            amount,
            receiver_address,
            sender_address,
            lock_condition_id,
            release_condition_id
        )

    def hash_values(
            self,
            amount,
            receiver_address,
            sender_address,
            lock_condition_id,
            release_condition_id
    ):
        return super(self).hash_values(
            amount,
            receiver_address,
            sender_address,
            lock_condition_id,
            release_condition_id
        )

