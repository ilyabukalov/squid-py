import os.path
import pathlib
import sys
import site

from web3 import Web3

from squid_py.ddo.service import Service
from squid_py.service_agreement.service_agreement import ServiceAgreement
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate
from squid_py.service_agreement.service_types import ServiceTypes
from squid_py.utils.utilities import get_id_from_did


class ServiceDescriptor(object):
    @staticmethod
    def access_service_descriptor(price, purchase_endpoint, service_endpoint, timeout):
        return (ServiceTypes.ASSET_ACCESS,
                {'price': price, 'purchaseEndpoint': purchase_endpoint, 'serviceEndpoint': service_endpoint,
                 'timeout': timeout})

    @staticmethod
    def compute_service_descriptor(price, purchase_endpoint, service_endpoint, timeout):
        return (ServiceTypes.CLOUD_COMPUTE,
                {'price': price, 'purchaseEndpoint': purchase_endpoint, 'serviceEndpoint': service_endpoint,
                 'timeout': timeout})


class ServiceFactory(object):
    @staticmethod
    def build_service(service_descriptor, did):
        assert isinstance(service_descriptor, tuple) and len(
            service_descriptor) == 2, 'Unknown service descriptor format.'
        service_type, kwargs = service_descriptor
        if service_type == ServiceTypes.ASSET_ACCESS:
            return ServiceFactory.build_access_service(
                did, kwargs['price'], kwargs['purchaseEndpoint'], kwargs['serviceEndpoint'], kwargs['timeout']
            )

        if service_type == ServiceTypes.CLOUD_COMPUTE:
            return ServiceFactory.build_compute_service(
                did, kwargs['price'], kwargs['purchaseEndpoint'], kwargs['serviceEndpoint'], kwargs['timeout']
            )

        raise ValueError('Unknown service type "%s"' % service_type)

    @staticmethod
    def build_metadata_service(did, metadata, service_endpoint):
        Service(did, service_endpoint, ServiceTypes.METADATA, values={'metadata': metadata})

    @staticmethod
    def build_access_service(did, price, purchase_endpoint, service_endpoint, timeout):
        param_map = {
            'assetId': Web3.toHex(get_id_from_did(did)),
            'price': price
        }

        sla_template_path = os.path.join(os.path.sep, *os.path.realpath(__file__).split(os.path.sep)[1:-1],
                                         'access_sla_template.json')
        sla_template = ServiceAgreementTemplate.from_json_file(sla_template_path)
        conditions = sla_template.conditions[:]
        conditions_json_list = []
        for cond in conditions:
            for param in cond.parameters:
                param.value = param_map[param.name]

            if cond.timeout > 0:
                cond.timeout = timeout

            conditions_json_list.append(cond)

        sa = ServiceAgreement('services-1', sla_template.template_id, sla_template.conditions,
                              sla_template.service_agreement_contract)
        other_values = {
            ServiceAgreement.SERVICE_DEFINITION_ID_KEY: sa.sa_definition_id,
            ServiceAgreementTemplate.TEMPLATE_ID_KEY: sla_template.template_id,
            ServiceAgreement.SERVICE_CONDITIONS_KEY: conditions,
            'purchaseEndpoint': purchase_endpoint
        }

        return Service(did, service_endpoint, ServiceTypes.ASSET_ACCESS, values=other_values)

    @staticmethod
    def build_compute_service(did, price, purchase_endpoint, service_endpoint, timeout):
        # TODO: implement this once the compute flow is ready
        return
