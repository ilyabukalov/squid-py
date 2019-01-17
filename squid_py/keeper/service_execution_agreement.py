"""
    Keeper module to transact/call `ServiceExecutionAgreement` keeper contract methods.
"""

from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.contract_base import ContractBase


class ServiceExecutionAgreement(ContractBase):
    SERVICE_AGREEMENT_ID = 'serviceAgreementId'

    @staticmethod
    def get_instance():
        """Returns a ContractBase instance of the ServiceExecutionAgreement contract."""
        return ServiceExecutionAgreement('ServiceExecutionAgreement')

    def setup_agreement_template(self, template_id, contracts_addresses, fingerprints,
                                 dependencies_bits, fulfillment_indices,
                                 fulfillment_operator, owner_account):
        """
        Wrapper around the `setupAgreementTemplate` solidity function
        Deploy a service agreement template that can be used in executing service agreements
        for asset data access and compute services.

        :param template_id: hex str -- id of this service agreement template
        :param contracts_addresses: list of hex str
        :param fingerprints: list of bytes arrays -- each fingerprint is the function selector
        :param dependencies_bits:  list of int -- each int represents the dependencies and the
            timeout flags of a condition
        :param fulfillment_indices: list of int -- the indices of the fulfillment/terminal
            conditions
        :param fulfillment_operator: int -- the logical operator used to determine the agreement
            fulfillment based on the conditions matching the `fulfillment_indices`
        :param owner_account: hex str -- ethereum address of account publishing this agreement
            template
        :return: dict -- transaction receipt
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

        owner_account.unlock()
        tx_hash = self.contract_concise.setupTemplate(
            template_id,           # bytes32 templateId
            contracts_addresses,   # address[] contracts
            fingerprints,          # bytes4[] fingerprints
            dependencies_bits,     # uint256[] dependenciesBits
            fulfillment_indices,   # uint8[] fulfillmentIndices
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

        :param template_id: hex str -- id of the service agreement template that defines the
            agreement conditions and dependencies
        :param signature: hex str -- the signed agreement hash. Signed by the `consumer`
        :param consumer: hex str -- consumer's ethereum address
        :param hashes: list of hex str -- each value is the hash of a condition's parameters values
        :param timeouts: list of int -- timeout value of each condition
        :param service_agreement_id: hex str
        :param did_id: hex str -- the asset id portion of did
        :param publisher_account: Account instance -- account of the publisher of this asset
        :return: dict -- transaction receipt
        """
        assert len(hashes) == len(timeouts), ''

        publisher_account.unlock()
        tx_hash = self.contract_concise.initializeAgreement(
            template_id,           # bytes32 templateId,
            signature,             # bytes signature,
            consumer,              # address consumer,
            hashes,                # bytes32[] valueHashes,
            timeouts,              # uint256[] timeoutValues,
            service_agreement_id,  # bytes32 agreementId,
            did_id,                # bytes32 did
            transact={'from': publisher_account.address, 'gas': DEFAULT_GAS_LIMIT}
        )
        return self.get_tx_receipt(tx_hash)

    def fulfill_agreement(self, service_agreement_id, from_account):
        from_account.unlock()
        return self.contract_concise.fulfillAgreement(service_agreement_id)

    def revoke_agreement_template(self, template_id, owner_account):
        owner_account.unlock()
        return self.contract_concise.revokeAgreementTemplate(template_id)

    def get_template_status(self, sa_template_id):
        return self.contract_concise.getTemplateStatus(sa_template_id)

    def get_template_owner(self, sa_template_id):
        return self.contract_concise.getTemplateOwner(sa_template_id)

    def get_template_id(self, service_agreement_id):
        return self.contract_concise.getTemplateId(service_agreement_id)

    def is_agreement_existing(self, service_agreement_id):
        return self.contract_concise.isAgreementExisting(service_agreement_id)

    def get_service_agreement_publisher(self, service_agreement_id):
        return self.contract_concise.getAgreementPublisher(service_agreement_id)

    def get_service_agreement_consumer(self, service_agreement_id):
        return self.contract_concise.getAgreementConsumer(service_agreement_id)

    def generate_condition_key_for_id(self, service_agreement_id, contract_address,
                                      function_fingerprint):
        return self.contract_concise.generateConditionKeyForId(service_agreement_id,
                                                               contract_address,
                                                               function_fingerprint)
