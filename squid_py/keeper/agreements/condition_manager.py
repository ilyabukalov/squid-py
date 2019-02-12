from squid_py.keeper import ContractBase


class ConditionManager(ContractBase):
    def get_condition(self, condition_id):
        return self.contract_concise.getCondition(condition_id)

    def get_condition_state(self, condition_id):
        return
