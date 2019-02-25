from squid_py.keeper import ContractBase


class ConditionStoreManager(ContractBase):
    """Class representing the ConditionStoreManager contract."""
    CONTRACT_NAME = 'ConditionStoreManager'

    def get_condition(self, condition_id):
        """Retrieve the condition for a condition_id.

        :param condition_id: id of the condition, str
        :return:
        """
        return self.contract_concise.getCondition(condition_id)

    def get_condition_state(self, condition_id):
        return
