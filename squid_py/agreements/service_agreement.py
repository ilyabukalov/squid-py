from collections import namedtuple

from eth_utils import add_0x_prefix

from squid_py.agreements.service_agreement_condition import ServiceAgreementCondition
from squid_py.agreements.service_agreement_contract import ServiceAgreementContract
from squid_py.agreements.service_agreement_template import ServiceAgreementTemplate
from squid_py.agreements.utils import (
    get_conditions_data_from_keeper_contracts,
    get_conditions_with_updated_keys
)
from squid_py.keeper import Keeper
from squid_py.keeper.utils import generate_multi_value_hash
from squid_py.utils.utilities import generate_prefixed_id

Agreement = namedtuple('Agreement', ('template', 'conditions'))


class ServiceAgreement(object):
    SERVICE_DEFINITION_ID = 'serviceDefinitionId'
    SERVICE_CONTRACT = 'serviceAgreementContract'
    SERVICE_CONDITIONS = 'conditions'
    PURCHASE_ENDPOINT = 'purchaseEndpoint'
    SERVICE_ENDPOINT = 'serviceEndpoint'

    def __init__(self, sa_definition_id, template_id, conditions, service_agreement_contract,
                 purchase_endpoint=None,
                 service_endpoint=None):
        self.sa_definition_id = sa_definition_id
        self.template_id = add_0x_prefix(template_id)
        self.conditions = conditions
        self.service_agreement_contract = service_agreement_contract
        self.purchase_endpoint = purchase_endpoint
        self.service_endpoint = service_endpoint

    def get_price(self):
        for cond in self.conditions:
            for p in cond.parameters:
                if p.name == 'price':
                    return p.value

    @property
    def service_definition_id(self):
        return self.sa_definition_id

    @property
    def agreement(self):
        return Agreement(self.template_id, self.conditions[:])

    @property
    def conditions_params_value_hashes(self):
        value_hashes = []
        for cond in self.conditions:
            value_hashes.append(cond.values_hash)

        return value_hashes

    @property
    def conditions_timeouts(self):
        return [cond.timeout for cond in self.conditions]

    @property
    def conditions_keys(self):
        return [cond.condition_key for cond in self.conditions]

    @property
    def conditions_contracts(self):
        return [cond.contract_address for cond in self.conditions]

    @property
    def conditions_fingerprints(self):
        return [cond.function_fingerprint for cond in self.conditions]

    @classmethod
    def from_ddo(cls, service_definition_id, ddo):
        service_def = ddo.find_service_by_id(service_definition_id).as_dictionary()
        if not service_def:
            raise ValueError(
                f'Service with definition id {service_definition_id} is not found in this DDO.')

        return cls.from_service_dict(service_def)

    @classmethod
    def from_service_dict(cls, service_dict):
        return cls(
            service_dict[cls.SERVICE_DEFINITION_ID],
            service_dict[ServiceAgreementTemplate.TEMPLATE_ID_KEY],
            [ServiceAgreementCondition(cond) for cond in service_dict[cls.SERVICE_CONDITIONS]],
            ServiceAgreementContract(service_dict[cls.SERVICE_CONTRACT]),
            service_dict.get(cls.PURCHASE_ENDPOINT), service_dict.get(cls.SERVICE_ENDPOINT)
        )

    @staticmethod
    def generate_service_agreement_hash(
            sa_template_id,
            condition_keys,
            values_hash_list,
            timeouts,
            service_agreement_id):
        return generate_multi_value_hash(
            ['bytes32', 'bytes32[]', 'bytes32[]', 'uint256[]', 'bytes32'],
            [sa_template_id, condition_keys, values_hash_list, timeouts, service_agreement_id]
        )

    @staticmethod
    def create_new_agreement_id():
        return generate_prefixed_id()

    def get_service_agreement_hash(self, service_agreement_id):
        """Return the hash of the service agreement values to be signed by a consumer.

        :param web3: Web3 instance
        :param contract_path: str -- path to keeper contracts artifacts (abi files)
        :param service_agreement_id: hex str identifies an executed service agreement on-chain
        :return:
        """
        agreement_hash = ServiceAgreement.generate_service_agreement_hash(
            self.template_id, self.conditions_keys,
            self.conditions_params_value_hashes, self.conditions_timeouts, service_agreement_id
        )
        return agreement_hash

    def get_signed_agreement_hash(self, service_agreement_id, consumer_account):
        """Return the consumer-signed service agreement hash and the raw hash.

        :param service_agreement_id: hex str -- a new service agreement id for this service
        transaction
        :param consumer_account: Account instance -- account of consumer to sign the message

        :return: signed_msg_hash, msg_hash
        """
        agreement_hash = self.get_service_agreement_hash(service_agreement_id)
        # We cannot use `web3.eth.account.signHash()` here because it requires privateKey which
        # is not available.
        return (Keeper.get_instance().sign_hash(agreement_hash, consumer_account),
                agreement_hash.hex())

    def update_conditions_keys(self):
        """Update the conditions keys based on the current keeper contracts.

        :param web3:
        :param contract_path:
        :return:
        """
        self.conditions = get_conditions_with_updated_keys(self.conditions,
                                                           self.template_id)

    def validate_conditions(self):
        # conditions_data = (contract_addresses, fingerprints, fulfillment_indices, conditions_keys)
        conditions_data = get_conditions_data_from_keeper_contracts(
            self.conditions, self.template_id
        )
        if conditions_data[3] != self.conditions_keys:
            raise AssertionError(f'Conditions keys set in this service agreement do not match the '
                                 f'conditions keys from the keeper\'s agreement template '
                                 f'"{self.template_id}".')

    def as_dictionary(self):
        return {
            ServiceAgreement.SERVICE_DEFINITION_ID: self.sa_definition_id,
            ServiceAgreementTemplate.TEMPLATE_ID_KEY: self.template_id,
            ServiceAgreement.SERVICE_CONTRACT: self.service_agreement_contract.as_dictionary(),
            ServiceAgreement.SERVICE_CONDITIONS: [cond.as_dictionary() for cond in
                                                  self.conditions]
        }
