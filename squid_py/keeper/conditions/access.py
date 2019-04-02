#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from squid_py.keeper.conditions.condition_base import ConditionBase


class AccessSecretStoreCondition(ConditionBase):
    """Class representing the AccessSecretStoreCondition contract."""
    CONTRACT_NAME = 'AccessSecretStoreCondition'

    def fulfill(self, agreement_id, document_id, grantee_address, account):
        """
        Fulfill the access secret store condition.

        :param agreement_id: id of the agreement, hex str
        :param document_id: refers to the DID in which secret store will issue the decryption
        keys, DID
        :param grantee_address: is the address of the granted user, str
        :param account: Account instance
        :return: true if the condition was successfully fulfilled, bool
        """
        return self._fulfill(
            agreement_id,
            document_id,
            grantee_address,
            transact={'from': account.address,
                      'passphrase': account.password}
        )

    def hash_values(self, document_id, grantee_address):
        """
        Hast the values of the document_id with the grantee address.

        :param document_id: refers to the DID in which secret store will issue the decryption
        keys, DID
        :param grantee_address: is the address of the granted user, str
        :return: hex str
        """
        return self._hash_values(document_id, grantee_address)

    def check_permissions(self, document_id, grantee_address):
        """
        Check that the grantee_address has permissions to decrypt the document stored with this
        document_id.

        :param document_id: refers to the DID in which secret store will issue the decryption
        keys, DID
        :param grantee_address: is the address of the granted user, str
        :return: true if the access was granted, bool
        """
        return self.contract_concise.checkPermissions(grantee_address, document_id)
