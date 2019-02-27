from collections import namedtuple

from squid_py.agreements.service_agreement_template import ServiceAgreementTemplate
from squid_py.agreements.service_types import ServiceTypes
from squid_py.ddo.service import Service
from squid_py.keeper.utils import generate_multi_value_hash
from squid_py.utils.utilities import generate_prefixed_id

Agreement = namedtuple('Agreement', ('template', 'conditions'))


class ServiceAgreement(Service):
    """"""
    SERVICE_DEFINITION_ID = 'serviceDefinitionId'
    AGREEMENT_TEMPLATE = 'serviceAgreementTemplate'
    SERVICE_CONDITIONS = 'conditions'
    PURCHASE_ENDPOINT = 'purchaseEndpoint'
    SERVICE_ENDPOINT = 'serviceEndpoint'

    def __init__(self, sa_definition_id, service_agreement_template, service_endpoint=None,
                 consume_endpoint=None, service_type=None):
        """

        :param sa_definition_id:
        :param service_agreement_template:
        :param service_endpoint:
        :param consume_endpoint:
        :param service_type:
        """
        self.sa_definition_id = sa_definition_id
        self.service_agreement_template = service_agreement_template

        values_dict = {
            ServiceAgreement.SERVICE_DEFINITION_ID: self.sa_definition_id,
            ServiceAgreementTemplate.TEMPLATE_ID_KEY: self.template_id,
            ServiceAgreement.AGREEMENT_TEMPLATE: self.service_agreement_template.as_dictionary(),

        }

        Service.__init__(self, service_endpoint,
                         service_type or ServiceTypes.ASSET_ACCESS,
                         values_dict, consume_endpoint)

    def get_price(self):
        for cond in self.conditions:
            for p in cond.parameters:
                if p.name == '_amount':
                    return p.value

    @property
    def agreement(self):
        return Agreement(self.template_id, self.conditions[:])

    @property
    def template_id(self):
        return self.service_agreement_template.template_id

    @property
    def conditions(self):
        return self.service_agreement_template.conditions

    @property
    def condition_by_name(self):
        return {cond.name: cond for cond in self.conditions}

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
    def conditions_timelocks(self):
        return [cond.timelock for cond in self.conditions]

    @property
    def conditions_contracts(self):
        return [cond.contract_name for cond in self.conditions]

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
            ServiceAgreementTemplate(service_dict[cls.AGREEMENT_TEMPLATE]),
            service_dict.get(cls.PURCHASE_ENDPOINT),
            service_dict.get(cls.SERVICE_ENDPOINT),
            service_dict.get('type')
        )

    @staticmethod
    def generate_service_agreement_hash(
            template_id,
            values_hash_list,
            timelocks,
            timeouts,
            agreement_id):
        return generate_multi_value_hash(
            ['bytes32', 'bytes32[]', 'uint256[]', 'uint256[]', 'bytes32'],
            [template_id, values_hash_list, timelocks, timeouts, agreement_id]
        )

    @staticmethod
    def create_new_agreement_id():
        return generate_prefixed_id()

    def generate_agreement_condition_ids(self, agreement_id, asset_id, consumer_address,
                                         publisher_address, keeper):

        lock_cond_id = keeper.lock_reward_condition.generate_id(
            agreement_id,
            self.condition_by_name['lockReward'].param_types,
            [keeper.escrow_reward_condition.address, self.get_price()])

        access_cond_id = keeper.access_secret_store_condition.generate_id(
            agreement_id,
            self.condition_by_name['accessSecretStore'].param_types,
            [asset_id, consumer_address])

        escrow_cond_id = keeper.escrow_reward_condition.generate_id(
            agreement_id,
            self.condition_by_name['escrowReward'].param_types,
            [self.get_price(), publisher_address, consumer_address,
             lock_cond_id, access_cond_id])

        return lock_cond_id, access_cond_id, escrow_cond_id

    def get_service_agreement_hash(
            self, agreement_id, asset_id, consumer_address, publisher_address, keeper):
        """Return the hash of the service agreement values to be signed by a consumer.

        :param web3: Web3 instance
        :param contract_path: str -- path to keeper contracts artifacts (abi files)
        :param agreement_id: hex str identifies an executed service agreement on-chain
        :param asset_id:
        :param consumer_address:
        :param publisher_address:
        :param keeper:
        :return:
        """
        agreement_hash = ServiceAgreement.generate_service_agreement_hash(
            self.template_id,
            self.generate_agreement_condition_ids(
                agreement_id, asset_id, consumer_address, publisher_address, keeper),
            self.conditions_timelocks,
            self.conditions_timeouts,
            agreement_id
        )
        return agreement_hash

    def validate_conditions(self):
        # TODO: Rewrite this to verify conditions based on the agreement template.
        return
        # # conditions_data = (contract_addresses, fingerprints, fulfillment_indices,
        # conditions_keys)
        # conditions_data = get_conditions_data_from_keeper_contracts(
        #     self.conditions, self.template_id
        # )
        # if conditions_data[3] != self.conditions_keys:
        #     raise AssertionError(f'Conditions keys set in this service agreement do not match
        #     the '
        #                          f'conditions keys from the keeper\'s agreement template '
        #                          f'"{self.template_id}".')
