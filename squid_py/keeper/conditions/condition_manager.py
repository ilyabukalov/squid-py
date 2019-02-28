from collections import namedtuple

from squid_py.keeper import ContractBase


ConditionValues = namedtuple(
    'ConditionValues',
    ('type_ref', 'state', 'time_lock', 'time_out',
     'block_number', 'last_updated_by', 'block_number_updated')
)


class ConditionStoreManager(ContractBase):
    """Class representing the ConditionStoreManager contract."""
    CONTRACT_NAME = 'ConditionStoreManager'

    def get_condition(self, condition_id):
        """Retrieve the condition for a condition_id.

        :param condition_id: id of the condition, str
        :return:
        """
        condition = self.contract_concise.getCondition(condition_id)
        if condition and len(condition) == 7:
            return ConditionValues(*condition)

        return None

    def get_condition_state(self, condition_id):
        return self.contract_concise.getConditionState(condition_id)
