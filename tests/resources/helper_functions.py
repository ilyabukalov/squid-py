#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import json
import os
import pathlib

from ocean_keeper.utils import get_account

from squid_py import ConfigProvider
from squid_py.brizo.brizo_provider import BrizoProvider
from ocean_utils.ddo.ddo import DDO
from ocean_utils.ddo.metadata import Metadata
from squid_py.ocean.keeper import SquidKeeper as Keeper
from squid_py.ocean.ocean import Ocean
from squid_py.secret_store.secret_store_provider import SecretStoreProvider
from tests.resources.mocks.brizo_mock import BrizoMock
from tests.resources.mocks.secret_store_mock import SecretStoreMock

PUBLISHER_INDEX = 1
CONSUMER_INDEX = 0


def get_resource_path(dir_name, file_name):
    base = os.path.realpath(__file__).split(os.path.sep)[1:-1]
    if dir_name:
        return pathlib.Path(os.path.join(os.path.sep, *base, dir_name, file_name))
    else:
        return pathlib.Path(os.path.join(os.path.sep, *base, file_name))


def init_ocn_tokens(ocn, account, amount=100):
    ocn.accounts.request_tokens(account, amount)
    Keeper.get_instance().token.token_approve(
        Keeper.get_instance().dispenser.address,
        amount,
        account
    )


def get_publisher_account(config):
    return get_account(0)


def get_consumer_account(config):
    return get_account(1)


def get_publisher_ocean_instance(init_tokens=True, use_ss_mock=True, use_brizo_mock=True):
    ocn = Ocean()
    account = get_publisher_account(ConfigProvider.get_config())
    ocn.main_account = account
    if init_tokens:
        init_ocn_tokens(ocn, ocn.main_account)
    if use_ss_mock:
        SecretStoreProvider.set_secret_store_class(SecretStoreMock)
    if use_brizo_mock:
        BrizoProvider.set_brizo_class(BrizoMock)

    return ocn


def get_consumer_ocean_instance(init_tokens=True, use_ss_mock=True, use_brizo_mock=True):
    ocn = Ocean()
    account = get_consumer_account(ConfigProvider.get_config())
    ocn.main_account = account
    if init_tokens:
        init_ocn_tokens(ocn, ocn.main_account)
    if use_ss_mock:
        SecretStoreProvider.set_secret_store_class(SecretStoreMock)
    if use_brizo_mock:
        BrizoProvider.set_brizo_class(BrizoMock)

    return ocn


def get_ddo_sample():
    return DDO(json_filename=get_resource_path('ddo', 'ddo_sa_sample.json'))


def get_registered_ddo(ocean_instance, account):
    ddo = ocean_instance.assets.create(Metadata.get_example(), account)
    return ddo


def log_event(event_name):
    def _process_event(event):
        print(f'Received event {event_name}: {event}')

    return _process_event


def get_metadata():
    path = get_resource_path('ddo', 'valid_metadata.json')
    assert path.exists(), f"{path} does not exist!"
    with open(path, 'r') as file_handle:
        metadata = file_handle.read()
    return json.loads(metadata)
