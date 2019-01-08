from web3 import Web3

from squid_py.keeper.contract_handler import ContractHandler
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


def init_ocean(w3, account=None):
    """
    Create an ocean instance with all the contracts deployed.

    :param w3: Web3 instance
    :param account: Account address, str
    :return: Ocean instance
    """
    ocn = Ocean()
    token_contract = deploy_contract(w3, account, 'OceanToken')
    ContractHandler.set('OceanToken', token_contract)
    ContractHandler.set('DIDRegistry', deploy_contract(w3, account, 'DIDRegistry'))
    ContractHandler.set('OceanMarket',
                        deploy_contract(w3, account, 'OceanMarket', token_contract.address))
    service_agreement_contract = deploy_contract(w3, account, 'ServiceAgreement')
    ContractHandler.set('ServiceAgreement', service_agreement_contract)
    ContractHandler.set('PaymentConditions', deploy_contract(w3, account, 'PaymentConditions',
                                                             service_agreement_contract.address,
                                                             token_contract.address))
    ContractHandler.set('AccessConditions', deploy_contract(w3, account, 'AccessConditions',
                                                            service_agreement_contract.address))
    return ocn


def deploy_contract(w3, account, contract_name, *args):
    """
    Deploy a json abi artifact on the chain that web3 is connected.

    :param w3: Web3 instance
    :param account: Account address, str
    :param contract_name: Contract name, str
    :param args: Args that the contract need to be deployed. Should be a list.
    :return: Contract instance
    """
    w3.eth.defaultAccount = account
    contract_instance = ContractHandler.get_contract_dict_by_name(contract_name)
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
