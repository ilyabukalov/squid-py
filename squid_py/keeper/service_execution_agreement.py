"""
    Keeper module to transact/call `ServiceExecutionAgreement` keeper contract methods.
"""

from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.contract_base import ContractBase


class ServiceExecutionAgreement(ContractBase):
    """Class representing the ServiceExecutionAgreement contract."""

    SERVICE_AGREEMENT_ID = 'agreementId'

    @staticmethod
    def get_instance():
        """Returns a ContractBase instance of the ServiceExecutionAgreement contract."""
        return ServiceExecutionAgreement('ServiceExecutionAgreement')

    def setup_agreement_template(self, template_id, contracts_addresses, fingerprints,
                                 dependencies_bits, fulfillment_indices,
                                 fulfillment_operator, owner_account):
        """
        Wrapper around the `setupTemplate` solidity function
        Deploy a service agreement template that can be used in executing service agreements
        for asset data access and compute services.

        :param template_id: id of this service agreement template, hex str
        :param contracts_addresses: list of hex str
        :param fingerprints: each fingerprint is the function selector, list of bytes arrays
        :param dependencies_bits: each int represents the dependencies and the
            timeout flags of a condition, list of int
        :param fulfillment_indices: the indices of the fulfillment/terminal conditions,  list of int
        :param fulfillment_operator: the logical operator used to determine the agreement
            fulfillment based on the conditions matching the `fulfillment_indices`, int
        :param owner_account: ethereum account publishing this agreement template, Account instance
        :return: transaction receipt, dict
        """

        assert contracts_addresses and isinstance(contracts_addresses, list), \
            f'contracts arg: expected list, got {type(contracts_addresses)}'
        assert fingerprints and isinstance(fingerprints, list), \
            f'fingerprints arg: expected list, got {type(fingerprints)}'
        assert dependencies_bits and isinstance(dependencies_bits, list), \
            f'dependencies_bits arg: expected list, got {type(dependencies_bits)}'
        for fin in fingerprints:
            assert isinstance(fin, (
                bytes, bytearray)), 'function finger print must be `bytes` or `bytearray`'

        assert len(contracts_addresses) == len(fingerprints), ''
        assert len(contracts_addresses) == len(dependencies_bits), ''
        for i in fulfillment_indices:
            assert i < len(contracts_addresses), ''
        assert isinstance(fulfillment_operator, int) and fulfillment_operator >= 0, ''

        tx_hash = self.contract_concise.setupTemplate(
            template_id,  # bytes32 templateId
            contracts_addresses,  # address[] contracts
            fingerprints,  # bytes4[] fingerprints
            dependencies_bits,  # uint256[] dependenciesBits
            fulfillment_indices,  # uint8[] fulfillmentIndices
            fulfillment_operator,  # uint8 fulfillmentOperator
            transact={'from': owner_account.address, 'gas': DEFAULT_GAS_LIMIT}
        )
        return self.get_tx_receipt(tx_hash)

    def execute_service_agreement(self, template_id, signature, consumer, hashes, timeouts,
                                  service_agreement_id,
                                  did_id, publisher_account):
        """
        Wrapper around the `initializeAgreement` solidity function.
        Start/initialize a service agreement on the blockchain. This is really the entry point for
        buying asset services (Access, Compute, etc.)

        :param template_id: id of the service agreement template that defines the agreement
                conditions and dependencies, hex str
        :param signature: the signed agreement hash. Signed by the `consumer`, hex str
        :param consumer: consumer's ethereum address, hex str
        :param hashes: each value is the hash of a condition's parameters values, list of hex str
        :param timeouts: timeout value of each condition, list of int
        :param service_agreement_id: id of this service execution agreement, hex str
        :param did_id: the asset id portion of did, hex str
        :param publisher_account: account of the publisher of this asset, Account instance
        :return: transaction receipt, dict
        """
        assert len(hashes) == len(timeouts), ''

        tx_hash = self.contract_concise.initializeAgreement(
            template_id,  # bytes32 templateId,
            signature,  # bytes signature,
            consumer,  # address consumer,
            hashes,  # bytes32[] valueHashes,
            timeouts,  # uint256[] timeoutValues,
            service_agreement_id,  # bytes32 agreementId,
            did_id,  # bytes32 did
            transact={'from': publisher_account.address, 'gas': DEFAULT_GAS_LIMIT}
        )
        return self.get_tx_receipt(tx_hash)

    def fulfill_agreement(self, service_agreement_id, from_account):
        """
        Called in case of there are no pending fulfilments.

        :param service_agreement_id: id of this service execution agreement, hex str
        :param from_account: Ethereum address of account calling the function, hex str
        :return: true if all the conditions are fulfilled according to the fulfillment criteria
        otherwise returns false, bool
        """
        return self.contract_concise.fulfillAgreement(service_agreement_id)

    def revoke_agreement_template(self, template_id, owner_account):
        """
        Revokes the template agreement, so the template will not be used in the future.

        :param template_id: id of this service execution agreement template, hex str
        :param owner_account: ethereum account revoking this agreement template, Account instance
        :return: True if the service execution agreement template was revoked, bool
        """
        return self.contract_concise.revokeAgreementTemplate(template_id)

    def get_template_status(self, template_id):
        return self.contract_concise.getTemplateStatus(template_id)

    def get_template_owner(self, template_id):
        """
        Returns service execution agreement template owner.

        :param template_id: id of this service execution agreement template, hex str
        :return: template owner address, hex str
        """
        return self.contract_concise.getTemplateOwner(template_id)

    def get_template_id(self, service_agreement_id):
        """
        Returns template Id using agreement ID.

        :param service_agreement_id: id of this service execution agreement, hex str
        :return: service execution template ID, hex str
        """
        return self.contract_concise.getTemplateId(service_agreement_id)

    def is_agreement_existing(self, service_agreement_id):
        """
        Checks if service execution agreement instance exists or not.

        :param service_agreement_id: id of this service execution agreement, hex str
        :return: True if the service execution agreement exists, bool
        """
        return self.contract_concise.isAgreementExisting(service_agreement_id)

    def get_service_agreement_publisher(self, service_agreement_id):
        """
        Retrieves the service execution agreement publisher address.

        :param service_agreement_id: id of this service execution agreement, hex str
        :return: Publisher ethereum address, hex str
        """
        return self.contract_concise.getAgreementPublisher(service_agreement_id)

    def get_service_agreement_consumer(self, service_agreement_id):
        """
        Retrieves the service execution agreement consumer address.

        :param service_agreement_id: id of this service execution agreement, hex str
        :return: Consumer ethereum address, hex str
        """
        return self.contract_concise.getAgreementConsumer(service_agreement_id)

    def generate_condition_key_for_id(self, service_agreement_id, contract_address,
                                      function_fingerprint):
        """
        Utility function that is in charge to generate condition key.

        :param service_agreement_id: id of this service execution agreement, hex str
        :param contract_address: Contract address, hex str
        :param function_fingerprint: each fingerprint is the function selector, list of bytes arrays
        :return: Condition Key, hex str
        """
        return self.contract_concise.generateConditionKeyForId(service_agreement_id,
                                                               contract_address,
                                                               function_fingerprint)
