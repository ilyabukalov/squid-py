from squid_py.agreements.service_factory import ServiceDescriptor
from squid_py.agreements.service_types import ACCESS_SERVICE_TEMPLATE_ID, ServiceTypes


class OceanServices:

    def __init__(self, ocean_assets):
        self._ocean_assets = ocean_assets

    def create_accesss_service(
            self, metadata, account, price, service_endpoint, consume_endpoint, timeout=None
    ):
        """
        Publish an asset with an `Access` service according to the supplied attributes.

        :param metadata: dict conforming to the Metadata accepted by Ocean Protocol.
        :param account: Account instance
        :param price: int price of service in ocean tokens
        :param service_endpoint: str URL for initiating service access request
        :param consume_endpoint: str URL to consume service
        :param timeout: int amount of time in seconds before the agreement expires
        :return: Service instance or None
        """
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
