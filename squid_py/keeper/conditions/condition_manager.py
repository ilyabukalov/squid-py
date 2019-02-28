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
        """Retrieve the condition state.

        :param condition_id: id of the condition, str
        :return: State of the condition
        """
        return self.contract_concise.getConditionState(condition_id)

    def get_num_condition(self):
        """
        Return the size of the Conditions list.

        :return: the length of the conditions list, int
        """
        return self.contract_concise.getConditionListSize()
