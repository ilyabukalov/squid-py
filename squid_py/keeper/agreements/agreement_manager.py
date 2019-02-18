from squid_py.keeper import ContractBase


class AgreementStoreManager(ContractBase):
    CONTRACT_NAME = 'AgreementStoreManager'

    def create_agreement(
            self,
            agreement_id,     # bytes32 _id
            did,              # bytes32 _did
            did_owner,        # address _didOwner
            condition_types,  # address[] memory _conditionTypes
            condition_ids,    # bytes32[] memory _conditionIds
            time_locks,       # uint[] memory _timeLocks
            time_outs,        # uint[] memory _timeOuts
    ):

        tx_hash = self.contract_concise.createAgreement(
            agreement_id,
            did,
            did_owner,
            condition_types,
            condition_ids,
            time_locks,
            time_outs,
        )
        receipt = self.get_tx_receipt(tx_hash)
        return receipt and receipt.status == 1

    def get_agreement(self, agreement_id):
        (did,
         owner,
         template_id,
         conditions_ids,
         updated_by,
         block_number_updated) = self.contract_concise.getAgreement(agreement_id)

        return (
            did,
            owner,
            template_id,
            conditions_ids,
            updated_by,
            block_number_updated
        )

    def get_agreement_did_owner(self, agreement_id):
        return self.contract_concise.getAgreementDidOwner(agreement_id)

    def get_num_agreements(self):
        return self.contract_concise.getAgreementListSize()
