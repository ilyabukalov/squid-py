from squid_py.keeper.conditions.condition_base import ConditionBase


class SignCondition(ConditionBase):
    CONTRACT_NAME = 'SignCondition'

    def fulfill(self, agreement_id, message, account_address, signature):
        return super(self).fulfill(
            agreement_id,
            message,
            account_address,
            signature
        )

    def hash_values(self, message, account_address):
        return super(self).hash_values(message, account_address)
