import logging

from ocean_keeper import Keeper, DIDRegistry, Dispenser, Token
from ocean_keeper.agreements import AgreementStoreManager
from ocean_keeper.conditions import SignCondition, LockRewardCondition, EscrowRewardCondition, AccessSecretStoreCondition, HashLockCondition
from ocean_keeper.conditions.condition_manager import ConditionStoreManager
from ocean_keeper.templates import TemplateStoreManager, EscrowAccessSecretStoreTemplate


class SquidKeeper(Keeper):

    @staticmethod
    def get_instance(artifacts_path=None, contract_names=None):
        return SquidKeeper(artifacts_path)

    def get_condition_name_by_address(self, address):
        """Return the condition name for a given address."""
        if self.lock_reward_condition.address == address:
            return 'lockReward'
        elif self.access_secret_store_condition.address == address:
            return 'accessSecretStore'
        elif self.escrow_reward_condition.address == address:
            return 'escrowReward'
        else:
            logging.error(f'The current address {address} is not a condition address')
