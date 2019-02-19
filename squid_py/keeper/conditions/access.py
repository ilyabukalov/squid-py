from squid_py.keeper.conditions.condition_base import ConditionBase


class AccessSecretStoreCondition(ConditionBase):
    CONTRACT_NAME = 'AccessSecretStoreCondition'

    def fulfill(self, agreement_id, document_id, grantee_address):
        return super(self).fulfill(agreement_id, document_id, grantee_address)

    def hash_values(self, document_id, grantee_address):
        return super(self).hash_values(document_id, grantee_address)

    def check_permissions(self, document_id, grantee_address):
        return self.contract_concise.check_permissions(grantee_address, document_id)
