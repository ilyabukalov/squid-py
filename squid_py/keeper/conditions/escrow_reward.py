#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from squid_py.keeper.conditions.condition_base import ConditionBase


class EscrowRewardCondition(ConditionBase):
    """Class representing the EscrowReward contract."""
    CONTRACT_NAME = 'EscrowReward'

    def fulfill(self,
                agreement_id,
                amount,
                receiver_address,
                sender_address,
                lock_condition_id,
                release_condition_id,
                account):
        """
        Fulfill the escrow reward condition.

        :param agreement_id:
        :param amount:
        :param receiver_address:
        :param sender_address:
        :param lock_condition_id:
        :param release_condition_id:
        :param account: Account instance
        :return:
        """
        return self._fulfill(
            agreement_id,
            amount,
            receiver_address,
            sender_address,
            lock_condition_id,
            release_condition_id,
            transact={'from': account.address,
                      'passphrase': account.password}
        )

    def hash_values(self, amount, receiver_address, sender_address, lock_condition_id,
                    release_condition_id):
        """

        :param amount:
        :param receiver_address:
        :param sender_address:
        :param lock_condition_id:
        :param release_condition_id:
        :return:
        """
        return self._hash_values(
            amount,
            receiver_address,
            sender_address,
            lock_condition_id,
            release_condition_id
        )
