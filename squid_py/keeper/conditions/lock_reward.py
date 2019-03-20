#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from squid_py.keeper.conditions.condition_base import ConditionBase


class LockRewardCondition(ConditionBase):
    """Class representing the LockRewardCondition contract."""
    CONTRACT_NAME = 'LockRewardCondition'

    def fulfill(self, agreement_id, reward_address, amount, account):
        """

        :param agreement_id:
        :param reward_address:
        :param amount:
        :param account: Account instance
        :return:
        """
        return self._fulfill(
            agreement_id,
            reward_address,
            amount,
            transact={'from': account.address,
                      'passphrase': account.password}
        )

    def hash_values(self, reward_address, amount):
        """

        :param reward_address:
        :param amount:
        :return:
        """
        return self._hash_values(reward_address, amount)
