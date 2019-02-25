from squid_py.keeper.conditions.condition_base import ConditionBase


class SignCondition(ConditionBase):
    """Class representing the SignCondition contract."""
    CONTRACT_NAME = 'SignCondition'

    def fulfill(self, agreement_id, message, account_address, signature):
        """

        :param agreement_id:
        :param message:
        :param account_address:
        :param signature:
        :return:
        """
        return super(self).fulfill(
            agreement_id,
            message,
            account_address,
            signature
        )

    def hash_values(self, message, account_address):
        """

        :param message:
        :param account_address:
        :return:
        """
        return super(self).hash_values(message, account_address)
