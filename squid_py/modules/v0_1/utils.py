import logging

from web3.contract import ConciseContract

from squid_py.keeper.utils import (
    get_contract_abi_by_address,
    get_fingerprint_by_name,
    hexstr_to_bytes,
    get_contract_abi_and_address)
from squid_py.modules.v0_1.exceptions import InvalidModule
from squid_py.service_agreement.utils import build_condition_key

logger = logging.getLogger('keeper-utils')


def process_tx_receipt(web3, tx_hash, event, event_name):
    web3.eth.waitForTransactionReceipt(tx_hash)
    receipt = web3.eth.getTransactionReceipt(tx_hash)
    event = event().processReceipt(receipt)
    if event:
        logger.info('Success: got %s event after fulfilling condition.', event_name)
    else:
        logger.debug('Something is not right, cannot find the %s event after calling the '
                     'fulfillment condition. This is the transaction receipt %s', event_name, receipt)


def handle_action(web3, account, sa_id, contract):
    logger.info('About to do grantAccess: account %s, saId %s, assetId %s, documentKeyId %s'
                .format(account.address, service_agreement_id,
                        asset_id, document_key_id))
    try:
        account.unlock()
        tx_hash = access_conditions.grantAccess(service_agreement_id, asset_id, document_key_id, transact=transact)
        process_tx_receipt(web3, tx_hash, contract.events.AccessGranted, 'AccessGranted')
    except Exception as e:
        logger.error('Error when calling grantAccess condition function: ', e, exc_info=1)
        raise

def is_condition_fulfilled(web3, contract_path, template_id, service_agreement_id,
                           service_agreement_address, condition_address, condition_abi, fn_name):
    service_agreement = _get_concise_contract(web3, contract_path, service_agreement_address)
    status = service_agreement.getConditionStatus(
        service_agreement_id,
        get_condition_key(
            web3,
            template_id,
            condition_address,
            condition_abi,
            fn_name,
        ),
    )
    return status == 1


def get_condition_key(web3, template_id, address, abi, fn_name):
    return build_condition_key(web3, address, hexstr_to_bytes(web3, get_fingerprint_by_name(abi, fn_name)), template_id)


def get_condition_contract_data(web3, contract_path, service_definition, name):
    condition_definition = None
    for condition in service_definition['conditions']:
        if condition['name'] == name:
            condition_definition = condition
            break

    if condition_definition is None:
        raise InvalidModule('Failed to find the {} condition in the service definition'.format(name))

    contract_name = condition_definition['contractName']
    function_name = condition_definition['functionName']
    abi, address = get_contract_abi_and_address(web3, contract_path, contract_name)
    # fingerprint = get_fingerprint_by_name(abi, function_name)
    # if get_fingerprint_by_name(abi, name) != functionName:
    #     raise InvalidModule('The {} fingerprint specified in the service definition ' +
    #                         'does not match the known fingerprint'.format(name))
    concise_contract = web3.eth.contract(
        address=address,
        abi=abi,
        ContractFactoryClass=ConciseContract,
    )
    contract = web3.eth.contract(
        address=address,
        abi=abi
    )
    return concise_contract, contract, abi, condition_definition


def get_eth_contracts(web3, contract_path, address):
    abi = get_contract_abi_by_address(contract_path, address)
    concise_contract = web3.eth.contract(
        address=address,
        abi=abi,
        ContractFactoryClass=ConciseContract,
    )
    contract = web3.eth.contract(
        address=address,
        abi=abi
    )

    return concise_contract, contract


def _get_concise_contract(web3, contract_path, address):
    abi = get_contract_abi_by_address(contract_path, address)

    return web3.eth.contract(
        address=address,
        abi=abi,
        ContractFactoryClass=ConciseContract,
    )
