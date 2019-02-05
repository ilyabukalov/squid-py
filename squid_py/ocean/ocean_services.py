from squid_py.agreements.service_factory import ServiceDescriptor
from squid_py.agreements.service_types import ACCESS_SERVICE_TEMPLATE_ID, ServiceTypes


class OceanServices:

    def __init__(self, ocean_assets):
        self._ocean_assets = ocean_assets

    def create_accesss_service(self, metadata, account, price, service_endpoint, consume_endpoint, timeout=None):
        timeout = timeout or 3600  # default to one hour timeout
        service = ServiceDescriptor.access_service_descriptor(
            price, service_endpoint, consume_endpoint, timeout, ACCESS_SERVICE_TEMPLATE_ID
        )
        asset = self._ocean_assets.create(
            metadata, account, [service]
        )
        for service in asset.services:
            if service.type == ServiceTypes.ASSET_ACCESS:
                return service

        return None
