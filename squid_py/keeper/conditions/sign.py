#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.conditions.condition_base import ConditionBase


class SignCondition(ConditionBase):
    """Class representing the SignCondition contract."""
    CONTRACT_NAME = 'SignCondition'

    def fulfill(self, agreement_id, message, account_address, signature, from_account):
        """

        :param agreement_id:
        :param message:
        :param account_address:
        :param signature:
        :param from_account:
        :return:
        """
        return self._fulfill(
            agreement_id,
            message,
            account_address,
            signature,
            transact={'from': from_account.address, 'gas': DEFAULT_GAS_LIMIT}
        )

    def hash_values(self, message, account_address):
        """

        :param message:
        :param account_address:
        :return:
        """
        return self._hash_values(message, account_address)
