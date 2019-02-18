from squid_py.keeper import ContractBase


class EscrowAccessSecretStoreTemplate(ContractBase):
    CONTRACT_NAME = 'EscrowAccessSecretStoreTemplate'

    def create_agreement(
            self,
            agreement_id,
            did,
            did_owner,
            condition_ids,
            time_locks,
            time_outs,
            consumer
    ):

        tx_hash = self.contract_concise.createAgreement(
            agreement_id,
            did,
            did_owner,
            condition_ids,
            time_locks,
            time_outs,
            consumer
        )

        return self.get_tx_receipt(tx_hash).status == 1
