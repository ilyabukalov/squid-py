import logging

from squid_py import Metadata, Ocean
from squid_py.config import Config
from tests.resources.helper_functions import (get_account_from_config)


def publish_asset():
    # make ocean instance
    path_config = 'config_local.ini'
    ocn = Ocean(Config(path_config))
    account = get_account_from_config(ocn.config, 'parity.address', 'parity.password')
    ddo = ocn.register_asset(Metadata.get_example(), account)

    logging.info(f'Registered asset: did={ddo.did}, ddo-services={ddo.services}')
