from squid_py.keeper import ContractBase


class TemplateStoreManager(ContractBase):
    CONTRACT_NAME = 'TemplateStoreManager'

    def get_template(self, template_id):
        (state,
         owner,
         updated_by,
         block_number_updated) = self.contract_concise.getTemplate(template_id)

        return (
            state,
            owner,
            updated_by,
            block_number_updated
        )

    def propose_template(self, template_id, from_account):
        tx_hash = self.contract_concise.proposeTemplate(
            template_id, transact={'from': from_account})
        return self.get_tx_receipt(tx_hash).status == 1

    def approve_template(self, template_id, from_account):
        tx_hash = self.contract_concise.approveTemplate(
            template_id, transact={'from': from_account})
        return self.get_tx_receipt(tx_hash).status == 1

    def revoke_template(self, template_id, from_account):
        tx_hash = self.contract_concise.revokeTemplate(
            template_id, transact={'from': from_account})
        return self.get_tx_receipt(tx_hash).status == 1

    def is_template_approved(self, template_id):
        return self.contract_concise.isTemplateApproved(template_id)

    def get_num_templates(self):
        return self.contract_concise.getTemplateListSize()
