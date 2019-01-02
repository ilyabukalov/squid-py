"""
    Keeper module to call keeper-contracts.
"""

from squid_py.keeper.contract_base import ContractBase


class Auth(ContractBase):
    """
    Class representing the OceanAuth contract.
    """

    @staticmethod
    def get_instance():
        return Auth('OceanAuth')

    def cancel_access_request(self, order_id, sender_address):
        """
        You can cancel consent and do refund only after consumer makes the payment and timeout.

        :param order_id: Order id , str
        :param sender_address: Sender account address, str
        :return:
        """
        return self.contract_concise.cancelAccessRequest(order_id, call={'from': sender_address})

    def initiate_access_request(self, asset_id, aquarius_address, pubkey, expiry, sender_address):
        """
        Consumer initiates access request of service.

        :param asset_id: Asset id, str
        :param aquarius_address:
        :param pubkey:
        :param expiry:
        :param sender_address:
        :return:
        """
        return self.contract_concise.initiateAccessRequest(asset_id,
                                                           aquarius_address,
                                                           pubkey,
                                                           expiry,
                                                           transact={'from': sender_address})

    def commit_access_request(self, order_id, is_available, expiration_date, discovery, permissions,
                              access_agreement_ref, accesss_agreement_type, sender_address,
                              gas_amount):
        """
        Aquarius commits the access request of service.

        :param order_id:
        :param is_available:
        :param expiration_date:
        :param discovery:
        :param permissions:
        :param access_agreement_ref:
        :param accesss_agreement_type:
        :param sender_address:
        :param gas_amount:
        :return:
        """
        return self.contract_concise.commitAccessRequest(order_id,
                                                         is_available,
                                                         expiration_date,
                                                         discovery,
                                                         permissions,
                                                         access_agreement_ref,
                                                         accesss_agreement_type,
                                                         transact={
                                                             'from': sender_address,
                                                             'gas': gas_amount}
                                                         )

    def deliver_access_token(self, order_id, enc_jwt, sender_address):
        """
        Aquarius delivers the access token of service to on-chain.

        :param order_id:
        :param enc_jwt:
        :param sender_address:
        :return:
        """
        return self.contract_concise.deliverAccessToken(order_id,
                                                        enc_jwt,
                                                        transact={'from': sender_address,
                                                                  'gas': 4000000})

    def get_order_status(self, order_id):
        """

        :param order_id:
        :return:
        """
        return self.contract_concise.statusOfAccessRequest(order_id)

    def get_encrypted_access_token(self, order_id, sender_address):
        """

        :param order_id:
        :param sender_address:
        :return:
        """
        return self.contract_concise.getEncryptedAccessToken(order_id,
                                                             call={'from': sender_address})
