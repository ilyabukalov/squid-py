import logging

from squid_py import Ocean, Metadata, ServiceDescriptor
from squid_py.brizo.brizo_provider import BrizoProvider
from squid_py.config import Config
from squid_py.config_provider import ConfigProvider
from tests.resources.helper_functions import get_registered_access_service_template, get_account_from_config


def publish_asset():
    # make ocean instance
    path_config = 'config_local.ini'
    ocn = Ocean(Config(path_config))
    account = get_account_from_config(ocn.config, 'parity.address', 'parity.password')
    template = get_registered_access_service_template(ocn, account)
    config = ConfigProvider.get_config()
    brizo = BrizoProvider.get_brizo()
    purchase_endpoint = brizo.get_purchase_endpoint(config)
    service_endpoint = brizo.get_service_endpoint(config)
    service_timeout = 600  # seconds (10 minutes)
    ddo = ocn.register_asset(
        Metadata.get_example(), account,
        [ServiceDescriptor.access_service_descriptor(
            20, purchase_endpoint, service_endpoint, service_timeout, template.template_id)]
    )

    logging.info(f'Registered asset: did={ddo.did}, ddo-services={ddo.services}')
