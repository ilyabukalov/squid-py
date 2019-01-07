import json
import os

from web3 import Web3
from squid_py.keeper.conditions.access_conditions import AccessConditions
from squid_py.keeper.conditions.payment_conditions import PaymentConditions
from squid_py.keeper.didregistry import DIDRegistry
from squid_py.keeper.keeper import Keeper
from squid_py.keeper.market import Market
from squid_py.keeper.service_agreement import ServiceAgreement
from squid_py.keeper.token import Token
from squid_py.ocean.ocean import Ocean


def test_deploy_contracts():
    w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
    account = w3.toChecksumAddress('0x00bd138abd70e2f00903268f3db08f2d25677c9e')
    ocn = init_ocean(w3, account)
    balance_before = ocn.keeper.token.get_token_balance(account)
    tx = ocn.keeper.market.request_tokens(100, account)
    w3.eth.waitForTransactionReceipt(w3.toHex(tx))
    balance_after = ocn.keeper.token.get_token_balance(account)
    assert balance_after == balance_before + 100, 'The token request was not successful'


def init_keeper(w3, account=None):
    keeper = Keeper()
    keeper.accounts = w3.eth.accounts
    keeper.token = Token('OceanToken', deploy_contract(w3, account, 'OceanToken'))
    keeper.did_registry = DIDRegistry('DIDRegistry', deploy_contract(w3, account, 'DIDRegistry'))
    keeper.market = Market('OceanMarket',
                           deploy_contract(w3, account, 'OceanMarket', keeper.token.address))
    keeper.service_agreement = ServiceAgreement('ServiceAgreement',
                                                deploy_contract(w3, account, 'ServiceAgreement'))

    keeper.payment_conditions = PaymentConditions('PaymentConditions',
                                                  deploy_contract(w3, account, 'PaymentConditions',
                                                                  keeper.service_agreement.address,
                                                                  keeper.token.address))
    keeper.access_conditions = AccessConditions('AccessConditions',
                                                deploy_contract(w3, account, 'AccessConditions',
                                                                keeper.service_agreement.address))
    keeper._instance = keeper
    return keeper


def init_ocean(w3, account=None):
    keeper = init_keeper(w3, account)
    ocn = Ocean(keeper_instance=keeper)
    return ocn


def deploy_contract(w3, account, contract_name, *args):
    w3.eth.defaultAccount = account
    contract_instance = get_contract_by_name('artifacts', 'spree', contract_name)
    contract_initial = w3.eth.contract(abi=contract_instance['abi'],
                                       bytecode=contract_instance['bytecode'])
    # Using deploy because the new option constructor().transact() is not stable now.
    tx_hash = contract_initial.deploy(transaction={'from': account}, args=args)
    w3.eth.waitForTransactionReceipt(w3.toHex(tx_hash))
    tx_receipt = w3.eth.getTransactionReceipt(w3.toHex(tx_hash))
    contract = w3.eth.contract(
        abi=contract_instance['abi'],
        address=tx_receipt['contractAddress']
    )
    return contract


def get_contract_by_name(contract_path, network_name, contract_name):
    """
    :param contract_path:
    :param network_name:
    :param contract_name:
    :return:
    """
    file_name = f'{contract_name}.{network_name}.json'
    path = os.path.join(contract_path, file_name)
    if not os.path.exists(path):
        file_name = f'{contract_name}.{network_name.lower()}.json'
        for name in os.listdir(contract_path):
            if name.lower() == file_name.lower():
                file_name = name
                path = os.path.join(contract_path, file_name)
                break

    if not os.path.exists(path):
        raise FileNotFoundError(f'Keeper contract {contract_name} file not found: {path}')

    with open(path) as f:
        contract = json.loads(f.read())
        return contract
