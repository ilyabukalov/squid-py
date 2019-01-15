import logging

from squid_py import Ocean, ConfigProvider, Metadata
from squid_py.examples.example_config import ExampleConfig
from tests.resources.helper_functions import get_account_from_config


def search_assets():
    ConfigProvider.set_config(ExampleConfig.get_config())
    ocn = Ocean()
    account = get_account_from_config(ocn.config, 'parity.address', 'parity.password')
    ddo = ocn.register_asset(
        Metadata.get_example(), account,
    )

    logging.info(f'Registered asset: did={ddo.did}, ddo={ddo.as_text()}')
    resolved_ddo = ocn.resolve_asset_did(ddo.did)
    logging.info(f'resolved asset ddo: did={resolved_ddo.did}, ddo={resolved_ddo.as_text()}')

    ddo_list = ocn.search_assets_by_text('bonding curve')
    logging.info(f'found {len(ddo_list)} assets that contain `bonding curve` in their metadata.')
    ddo_list = ocn.search_assets({"query": {"service.metadata.base.name": 'Ocean protocol white paper'}})
    logging.info(f'found {len(ddo_list)} assets with name that contains `Ocean protocol white paper`')


if __name__ == '__main__':
    search_assets()
