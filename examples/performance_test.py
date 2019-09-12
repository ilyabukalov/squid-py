import json
import os
import logging
import time

import sys
from eth_utils import remove_0x_prefix
from ocean_keeper.account import Account

from ocean_keeper.diagnostics import Diagnostics
from ocean_keeper.contract_handler import ContractHandler
from ocean_utils.agreements.service_types import ServiceTypes
from ocean_utils.ddo.metadata import Metadata

from examples import ExampleConfig
from ocean_utils.agreements.service_agreement import ServiceAgreement

from squid_py import Ocean
from squid_py.config_provider import ConfigProvider
from ocean_keeper.web3_provider import Web3Provider
from tests.resources.helper_functions import (
    get_publisher_account,
)


def create_account(w3, index, secret_base, path_base):
    local_account = w3.eth.account.create()
    password = f'{secret_base}:!{index}'
    encrypted_key = local_account.encrypt(password)
    fname = f'{path_base}/{remove_0x_prefix(local_account.address)}.json.testaccount'
    with open(fname, 'w') as f:
        json.dump(encrypted_key, f)

    return Account(local_account.address, password, fname)


def create_accounts(w3, num_accounts, save_file):
    accounts = []
    with open(save_file, 'w') as f:
        for i in range(num_accounts):
            a = create_account(w3, i, "sHt8Uwdru3McRYqDve~Dp>", os.path.expanduser('~/test_accounts'))
            accounts.append(a)
            n = i + 10 + 1
            f.writelines(
                [f'\naccount.parity.address{n} = "{a.address}"',
                 f'\naccount.parity.password{n} = "{a.password}"',
                 f'\naccount.parity.file{n} = "{a.key_file}"']
            )


def generate_java_commands(num, offset, save_file):
    with open(save_file, 'w') as f:
        for i in range(num):
            n = i + offset + 1
            f.write(f'\n/usr/lib/jvm/java-11-oracle/bin/java -Dconfig.file=duero-direct-application.conf  -jar squid-0.6.3_test-exe.jar {n} $NUM_ORDERS &')
    print(f'done saving commands to file {save_file}')


def extract_addresses(file_name, save_file):
    """Extract ethereum addresses from file generated using `create_accounts`"""
    addresses = []
    with open(file_name, 'r') as f:
        for l in f.readlines():
            if '0x' not in l:
                continue

            address = l.split("0x")[-1][:-2]
            addresses.append(f'"0x{address}"')

    with open(save_file, 'w') as f:
        f.write(','.join(addresses))


def register_asset(ocn, publisher_acc, metadata, providers):
    """Create asset and wait for confirmation from the keeper nodes, then return the asset DDO"""
    keeper = ocn.keeper
    ddo = ocn.assets.create(metadata, publisher_acc, providers=providers)
    did = ddo.did
    # Wait for did registry event
    event = keeper.did_registry.subscribe_to_event(
        keeper.did_registry.DID_REGISTRY_EVENT_NAME,
        30,
        event_filter={
            '_did': Web3Provider.get_web3().toBytes(hexstr=ddo.asset_id),
            '_owner': publisher_acc.address},
        wait=True
    )
    if not event:
        logging.warning(f'Failed to get the did registry event for asset with did {did}.')
    assert keeper.did_registry.get_block_number_updated(ddo.asset_id) > 0, \
        f'There is an issue in registering asset {did} on-chain.'

    logging.info(f'is {providers[0]} set as did provider: '
                 f'{keeper.did_registry.is_did_provider(ddo.asset_id, providers[0])}')
    return ddo


def load_accounts(accounts_path):
    """Return Account instances for the accounts listed in file generated in `create_accounts`."""
    file_name = 'accounts_data.txt'
    accounts_data_file = os.path.join(accounts_path, file_name)
    accounts = []
    address, password, key_file = None, None, None
    with open(accounts_data_file, 'r') as f:
        state = 0
        for l in f.readlines():
            if state == 0:
                if l.startswith('account.parity.address'):
                    address = l.split('=')[-1].strip()
                    state = 1

            elif state == 1:
                if l.startswith('account.parity.password'):
                    password = l.split('=')[-1].strip()
                    state = 2
                else:
                    state = 0
                    address, password, key_file = None, None, None

            elif state == 2:
                if l.startswith('account.parity.file'):
                    key_file = l.split('=')[-1].strip()
                    key_file = os.path.join(accounts_path, key_file)
                    assert os.path.exists(key_file), f'keyfile {key_file} is not found in the accounts folder {accounts_path}'
                    accounts.append(Account(address, password, key_file))
                state = 0
                address, password, key_file = None, None, None

    return accounts


def transfer_ether_to_accounts(keeper, from_account, receivers, amount):
    for receiver in receivers:
        keeper.send_ether(from_account, receiver.address if isinstance(receiver, Account) else receiver, amount)


def transfer_ether_to():
    init_env_vars(os.path.expanduser(os.environ["TEST_ACCOUNTS_FOLDER"]))
    receiver = '0x00Bd138aBD70e2F00903268F3Db08f2D25677C9e'
    account = get_publisher_account()
    ocn, keeper = get_ocn_and_keeper()

    transfer_ether_to_accounts(keeper, account, [receiver], 100000000000000000)


def init_env_vars(accounts_path):
    if not os.environ.get("TEST_NET"):
        # os.environ['TEST_NET'] = 'duero'
        os.environ['TEST_NET'] = 'nile'

    if not os.environ.get("PARITY_ADDRESS1"):
        os.environ["PARITY_ADDRESS1"] = "0x00bd138abd70e2f00903268f3db08f2d25677c9e"
        os.environ["PARITY_PASSWORD1"] = "node0"
        os.environ["PARITY_KEYFILE1"] = os.path.join(accounts_path, "key_file_2.json")
    if not os.environ.get("PARITY_ADDRESS"):
        os.environ["PARITY_ADDRESS"] = "0x068ed00cf0441e4829d9784fcbe7b9e26d4bd8d0"
        os.environ["PARITY_PASSWORD"] = "secret"
        os.environ["PARITY_KEYFILE"] = os.path.join(accounts_path, "key_file_1.json")


def get_ocn_and_keeper():
    ConfigProvider.set_config(ExampleConfig.get_config())
    config = ConfigProvider.get_config()
    Web3Provider.get_web3(config.keeper_url)
    ContractHandler.artifacts_path = config.keeper_path
    ocn = Ocean()
    keeper = ocn.keeper
    return ocn, keeper


def buy_asset(consumer_account, did):

    ocn, keeper = get_ocn_and_keeper()
    config = ConfigProvider.get_config()

    ocn.accounts.request_tokens(consumer_account, 10)
    ddo = ocn.assets.resolve(did)
    service = ddo.get_service(service_type=ServiceTypes.ASSET_ACCESS)
    sa = ServiceAgreement.from_service_dict(service.as_dictionary())

    agreement_id = ocn.assets.order(
        did, sa.service_definition_id, consumer_account)

    logging.info('placed order: %s, %s', did, agreement_id)
    event = keeper.escrow_access_secretstore_template.subscribe_agreement_created(
        agreement_id, 30, None, (), wait=True
    )
    assert event, "Agreement event is not found, check the keeper node's logs"
    logging.info(f'Got agreement event, next: lock reward condition')

    event = keeper.lock_reward_condition.subscribe_condition_fulfilled(
        agreement_id, 30, None, (), wait=True
    )
    assert event, "Lock reward condition fulfilled event is not found, check the keeper node's logs"
    logging.info('Got lock reward event, next: wait for the access condition..')

    event = keeper.access_secret_store_condition.subscribe_condition_fulfilled(
        agreement_id, 30, None, (), wait=True
    )
    logging.info(f'Got access event {event}')
    i = 0
    while ocn.agreements.is_access_granted(
            agreement_id, did, consumer_account.address) is not True and i < 15:
        time.sleep(1)
        i += 1

    assert ocn.agreements.is_access_granted(agreement_id, did, consumer_account.address)

    ocn.assets.consume(
        agreement_id,
        did,
        sa.service_definition_id,
        consumer_account,
        config.downloads_path)
    logging.info('Success buying asset.')

    logging.info(f'Done buy asset: agrId={agreement_id}, consumer={consumer_account.address}, did={did}')
    return agreement_id, consumer_account.address


def send_ether_to_all_accounts():
    accounts_path = os.path.expanduser(os.environ["TEST_ACCOUNTS_FOLDER"])
    init_env_vars(accounts_path)

    ConfigProvider.set_config(ExampleConfig.get_config())

    config = ConfigProvider.get_config()
    Web3Provider.get_web3(config.keeper_url)
    ContractHandler.artifacts_path = config.keeper_path
    ocn, keeper = get_ocn_and_keeper()
    acc = get_publisher_account()
    receivers = [a.address for a in load_accounts(accounts_path)]
    transfer_ether_to_accounts(keeper, acc, receivers, 100000000000000000)


def run_performance_test():
    """
    Make sure to export the envvar TEST_ACCOUNTS_FOLDER which must contain all of the accounts keyfiles
    to use in the test. This folder must also have the accounts data file which has the address, password
    and keyfile name for each account.

    `Note`: The keyfiles for the accounts that will be used in this test must all be available to the
    local parity node (copy the keyfiles to the network's `keys`
    folder (e.g. barge/networks/duero/keys).

    To run this test on duero, it is sufficient to start ocean services in barge using this command:
      >> ./start_ocean.sh --local-duero-node --no-aquarius --no-brizo --no-events-handler --no-pleuston
    So, the following services are not needed (remote services will be used):
      Brizo, Aquarius, Events-listener and Pleuston (don't need a marketplace here)

    :return:
    """
    accounts_path = os.path.expanduser(os.environ["TEST_ACCOUNTS_FOLDER"])
    init_env_vars(accounts_path)

    ocn, keeper = get_ocn_and_keeper()
    w3 = Web3Provider.get_web3()

    supported_networks = ('duero', 'nile')  # , 'pacific', 'spree')
    network = os.environ.get("TEST_NET")
    assert network in supported_networks, \
        f'Bad network name {network}, set `TEST_NET` to one ' \
        f'of {supported_networks} and try again.'

    # make ocean instance
    Diagnostics.verify_contracts()

    did = 'did:op:c678e7e5963d4fdc99afea49ac221d4d4177790f30204417823319d4d35f851f'
    if not did:
        # This is the provider address used in Brizo and the Events-handler on the Duero/Nile network
        # make sure to change this address to match the current network
        providers = []
        if network == 'duero':
            providers = [w3.toChecksumAddress('0x9D4eD58293F71122aD6a733C1603927a150735D0')]
        elif network == 'nile':
            providers = [w3.toChecksumAddress('0x4aaab179035dc57b35e2ce066919048686f82972')]

        acc = get_publisher_account()
        # Register asset once for consume requests
        ddo = register_asset(ocn, acc, Metadata.get_example(), providers)
        assert ddo is not None, f'Registering asset on-chain failed.'
        logging.info(f'registered ddo: {ddo.did}')
        did = ddo.did

    accounts = load_accounts(accounts_path)
    index = int(sys.argv[1])
    a = accounts[index]
    print(f'run for index: {index}, {a.address}, {a.password}########################### {[index]*25}')
    values = buy_asset(accounts[index], did)

    print(f'results: {values} ********* {index} ###################################### {[index]*25}')


if __name__ == '__main__':
    run_performance_test()
