import logging


from squid_py import Metadata, Ocean
from squid_py.config_provider import ConfigProvider
from squid_py.examples.example_config import ExampleConfig
from tests.resources.helper_functions import (
    get_account_from_config,
)


def register_asset():
    # make ocean instance
    ConfigProvider.set_config(ExampleConfig.get_config())
    ocn = Ocean()
    account = get_account_from_config(ocn.config, 'parity.address', 'parity.password')
    ddo = ocn.register_asset(Metadata.get_example(), account)

    logging.info(f'Registered asset: did={ddo.did}, ddo-services={ddo.services}')
    resolved_ddo = ocn.resolve_asset_did(ddo.did)
    logging.info(f'resolved asset ddo: did={resolved_ddo.did}, ddo={resolved_ddo.as_text()}')


if __name__ == '__main__':
    register_asset()
