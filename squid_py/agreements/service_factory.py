from squid_py.agreements.service_agreement import ServiceAgreement
from squid_py.agreements.service_agreement_template import ServiceAgreementTemplate
from squid_py.agreements.service_types import ServiceTypes
from squid_py.agreements.utils import get_sla_template_path
from squid_py.ddo.service import Service
from squid_py.did import did_to_id
from squid_py.keeper import Keeper


class ServiceDescriptor(object):
    @staticmethod
    def metadata_service_descriptor(metadata, service_endpoint):
        return (ServiceTypes.METADATA,
                {'metadata': metadata, 'serviceEndpoint': service_endpoint})

    @staticmethod
    def authorization_service_descriptor(service_endpoint):
        return (ServiceTypes.AUTHORIZATION,
                {'serviceEndpoint': service_endpoint})

    @staticmethod
    def access_service_descriptor(price, purchase_endpoint, service_endpoint, timeout, template_id):
        return (ServiceTypes.ASSET_ACCESS,
                {'price': price, 'purchaseEndpoint': purchase_endpoint,
                 'serviceEndpoint': service_endpoint,
                 'timeout': timeout, 'templateId': template_id})

    @staticmethod
    def compute_service_descriptor(price, purchase_endpoint, service_endpoint, timeout):
        return (ServiceTypes.CLOUD_COMPUTE,
                {'price': price, 'purchaseEndpoint': purchase_endpoint,
                 'serviceEndpoint': service_endpoint,
                 'timeout': timeout})


class ServiceFactory(object):
    @staticmethod
    def build_services(did, service_descriptors):
        services = []
        sa_def_key = ServiceAgreement.SERVICE_DEFINITION_ID
        for i, service_desc in enumerate(service_descriptors):
            service = ServiceFactory.build_service(service_desc, did)
            # set serviceDefinitionId for each service
            service.update_value(sa_def_key, str(i))
            services.append(service)

        return services

    @staticmethod
    def build_service(service_descriptor, did):
        assert isinstance(service_descriptor, tuple) and len(
            service_descriptor) == 2, 'Unknown service descriptor format.'
        service_type, kwargs = service_descriptor
        if service_type == ServiceTypes.METADATA:
            return ServiceFactory.build_metadata_service(
                did,
                kwargs['metadata'],
                kwargs['serviceEndpoint']
            )

        elif service_type == ServiceTypes.AUTHORIZATION:
            return ServiceFactory.build_authorization_service(
                kwargs['serviceEndpoint']
            )

        elif service_type == ServiceTypes.ASSET_ACCESS:
            return ServiceFactory.build_access_service(
                did, kwargs['price'],
                kwargs['purchaseEndpoint'], kwargs['serviceEndpoint'],
                kwargs['timeout'], kwargs['templateId']
            )

        elif service_type == ServiceTypes.CLOUD_COMPUTE:
            return ServiceFactory.build_compute_service(
                did, kwargs['price'],
                kwargs['purchaseEndpoint'], kwargs['serviceEndpoint'], kwargs['timeout']
            )

        raise ValueError(f'Unknown service type {service_type}')

    @staticmethod
    def build_metadata_service(did, metadata, service_endpoint):
        return Service(service_endpoint,
                       ServiceTypes.METADATA,
                       values={'metadata': metadata},
                       did=did)

    @staticmethod
    def build_authorization_service(service_endpoint):
        return Service(service_endpoint, ServiceTypes.AUTHORIZATION,
                       values={'service': 'SecretStore'})

    @staticmethod
    def build_access_service(did, price, purchase_endpoint, service_endpoint,
                             timeout,
                             template_id):
        # TODO fill all the possible mappings
        param_map = {
            '_documentId': did_to_id(did),
            '_amount': price,
            '_rewardAddress': Keeper.get_instance().escrow_reward_condition.address,
        }
        sla_template_path = get_sla_template_path()
        sla_template = ServiceAgreementTemplate.from_json_file(sla_template_path)
        sla_template.template_id = template_id
        conditions = sla_template.conditions[:]
        for cond in conditions:
            for param in cond.parameters:
                param.value = param_map.get(param.name, '')

            if cond.timeout > 0:
                cond.timeout = timeout

        sla_template.set_conditions(conditions)
        sa = ServiceAgreement(
            1,
            sla_template,
            purchase_endpoint,
            service_endpoint,
            ServiceTypes.ASSET_ACCESS
        )
        sa.set_did(did)
        return sa

    @staticmethod
    def build_compute_service(did, price, purchase_endpoint, service_endpoint,
                              timeout):
        # TODO: implement this once the compute flow is ready
        return
