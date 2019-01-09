import os
import pathlib
import time

from squid_py import (
    ServiceAgreementTemplate,
    ACCESS_SERVICE_TEMPLATE_ID,
    ServiceDescriptor,
    Ocean,
    Account)
from squid_py.config import Config
from squid_py.ddo.metadata import Metadata
from squid_py.keeper import Keeper
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.brizo.brizo import Brizo
from squid_py.secret_store.secret_store import SecretStore
from squid_py.service_agreement.utils import get_sla_template_path, register_service_agreement_template
from tests.resources.mocks.brizo_mock import BrizoMock
from tests.resources.mocks.secret_store_mock import SecretStoreClientMock


PUBLISHER_INDEX = 1
CONSUMER_INDEX = 0


def get_resource_path(dir_name, file_name):
    base = os.path.realpath(__file__).split(os.path.sep)[1:-1]
    if dir_name:
        return pathlib.Path(os.path.join(os.path.sep, *base, dir_name, file_name))
    else:
        return pathlib.Path(os.path.join(os.path.sep, *base, file_name))


def init_ocn_tokens(ocn, amount=100):
    ocn.main_account.request_tokens(amount)
    ocn.keeper.token.token_approve(
        ocn.keeper.payment_conditions.address,
        amount,
        ocn.main_account
    )


def make_ocean_instance(secret_store_client, account_index):
    path_config = 'config_local.ini'
    os.environ['CONFIG_FILE'] = path_config
    SecretStore.set_client(secret_store_client)
    ocn = Ocean(Config(path_config))
    Brizo.set_http_client(BrizoMock(ocn))
    ocn.set_main_account(list(ocn.accounts)[account_index], '')
    return ocn


def get_publisher_ocean_instance():
    ocn = make_ocean_instance(SecretStoreClientMock, PUBLISHER_INDEX)
    address = None
    if ocn.config.has_option('keeper-contracts', 'parity.address'):
        address = ocn.config.get('keeper-contracts', 'parity.address')
    address = Web3Provider.get_web3().toChecksumAddress(address) if address else None
    if address and address in ocn.accounts:
        password = ocn.config.get('keeper-contracts', 'parity.password') \
            if ocn.config.has_option('keeper-contracts', 'parity.password') else None
        ocn.set_main_account(address, password)
    init_ocn_tokens(ocn)
    return ocn


def get_consumer_ocean_instance():
    ocn = make_ocean_instance(SecretStoreClientMock, CONSUMER_INDEX)
    address = None
    if ocn.config.has_option('keeper-contracts', 'parity.address1'):
        address = ocn.config.get('keeper-contracts', 'parity.address1')

    address = Web3Provider.get_web3().toChecksumAddress(address) if address else None
    if address and address in ocn.accounts:
        password = ocn.config.get('keeper-contracts', 'parity.password1') \
            if ocn.config.has_option('keeper-contracts', 'parity.password1') else None
        ocn.set_main_account(address, password)
    init_ocn_tokens(ocn)
    return ocn


def get_account_from_config(config, config_account_key, config_account_password_key):
    address = None
    if config.has_option('keeper-contracts', config_account_key):
        address = config.get('keeper-contracts', config_account_key)

    if not address:
        return None

    password = None
    address = Web3Provider.get_web3().toChecksumAddress(address) if address else None
    if (address
            and address in Keeper.get_instance().accounts
            and config.has_option('keeper-contracts', config_account_password_key)):
        password = config.get('keeper-contracts', config_account_password_key)

    return Account(Keeper.get_instance(), address, password)


def get_registered_access_service_template(ocean_instance):
    # register an asset Access service agreement template
    template = ServiceAgreementTemplate.from_json_file(get_sla_template_path())
    template_id = ACCESS_SERVICE_TEMPLATE_ID
    template_owner = ocean_instance.keeper.service_agreement.get_template_owner(template_id)
    if not template_owner:
        template = register_service_agreement_template(
            ocean_instance.keeper.service_agreement,
            ocean_instance.main_account, template,
            ocean_instance.keeper.network_name
        )

    return template


def get_registered_ddo(ocean_instance):
    template = get_registered_access_service_template(ocean_instance)
    config = ocean_instance.config
    purchase_endpoint = Brizo.get_purchase_endpoint(config)
    service_endpoint = Brizo.get_service_endpoint(config)
    ddo = ocean_instance.register_asset(
        Metadata.get_example(), ocean_instance.main_account,
        [ServiceDescriptor.access_service_descriptor(7, purchase_endpoint, service_endpoint, 360,
                                                     template.template_id)]
    )

    return ddo


def wait_for_event(event, arg_filter, wait_iterations=20):
    _filter = event.createFilter(fromBlock=0, argument_filters=arg_filter)
    for check in range(wait_iterations):
        events = _filter.get_all_entries()
        if events:
            return events[0]
        time.sleep(0.5)
