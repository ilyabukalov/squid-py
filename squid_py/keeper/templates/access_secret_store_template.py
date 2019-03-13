#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper import ContractBase
from squid_py.keeper.web3_provider import Web3Provider


class EscrowAccessSecretStoreTemplate(ContractBase):
    """Class representing the EscrowAccessSecretStoreTemplate contract."""
    CONTRACT_NAME = 'EscrowAccessSecretStoreTemplate'
    AGREEMENT_CREATED_EVENT = 'AgreementCreated'

    def create_agreement(self, agreement_id, did, condition_ids, time_locks, time_outs,
                         consumer_address, publisher_account):
        """

        :param agreement_id:
        :param did:
        :param condition_ids:
        :param time_locks:
        :param time_outs:
        :param consumer_address:
        :param publisher_account:
        :return:
        """
        publisher_account.unlock()
        tx_hash = self.contract_concise.createAgreement(
            agreement_id,
            did,
            condition_ids,
            time_locks,
            time_outs,
            consumer_address,
            transact={'from': publisher_account.address, 'gas': DEFAULT_GAS_LIMIT}
        )
        return self.get_tx_receipt(tx_hash).status == 1

    def get_condition_types(self):
        """

        :return:
        """
        return self.contract_concise.getConditionTypes()

    def get_agreement_data(self, agreement_id):
        """

        :param agreement_id:
        :return:
        """
        consumer, provider = self.contract_concise.getAgreementData(agreement_id)
        return consumer, provider

    def get_agreement_consumer(self, agreement_id):
        """

        :param agreement_id:
        :return:
        """
        data = self.get_agreement_data(agreement_id)
        return data[0] if data and len(data) > 1 else None

    def subscribe_agreement_created(self, agreement_id, timeout, callback, args, wait=False):
        """
        Subscribe to an agreement created.

        :param agreement_id:
        :param timeout:
        :param callback:
        :param args:
        :param wait:
        :return:
        """
        return self.subscribe_to_event(
            self.AGREEMENT_CREATED_EVENT,
            timeout,
            {'_agreementId': Web3Provider.get_web3().toBytes(hexstr=agreement_id)},
            callback=callback,
            args=args,
            wait=wait
        )
