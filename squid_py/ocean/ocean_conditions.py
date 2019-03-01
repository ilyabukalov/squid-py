from eth_utils import add_0x_prefix

from squid_py.did import did_to_id


class OceanConditions:
    def __init__(self, keeper):
        self._keeper = keeper

    def lock_reward(self, agreement_id, amount, account):
        tx_hash = self._keeper.lock_reward_condition.fulfill(
            agreement_id, self._keeper.escrow_reward_condition.address, amount, account
        )
        return self._keeper.lock_reward_condition.get_tx_receipt(tx_hash).status == 1

    def grant_access(self, agreement_id, did, grantee_address, account):
        tx_hash = self._keeper.access_secret_store_condition.fulfill(
            agreement_id, add_0x_prefix(did_to_id(did)), grantee_address, account
        )
        return self._keeper.access_secret_store_condition.get_tx_receipt(tx_hash).status == 1

    def release_reward(self, agreement_id, amount, account):
        agreement_values = self._keeper.agreement_manager.get_agreement(agreement_id)
        consumer, provider = self._keeper.escrow_access_secretstore_template.get_agreement_data(agreement_id)
        access_id, lock_id = agreement_values.condition_ids[:2]
        tx_hash = self._keeper.escrow_reward_condition.fulfill(
            agreement_id,
            amount,
            provider,
            consumer,
            lock_id,
            access_id,
            account
        )
        return self._keeper.escrow_reward_condition.get_tx_receipt(tx_hash).status == 1

    def refund_reward(self, agreement_id, amount, account):
        return self.release_reward(agreement_id, amount, account)
