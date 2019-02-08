import logging

from squid_py.agreements.utils import build_condition_key
from squid_py.keeper.contract_handler import ContractHandler
from squid_py.keeper.utils import (
    get_fingerprint_by_name,
    hexstr_to_bytes,
)
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.modules.v0_1.exceptions import InvalidModule

logger = logging.getLogger('keeper-utils')


def process_tx_receipt(tx_hash, event, event_name):
    web3 = Web3Provider.get_web3()
    web3.eth.waitForTransactionReceipt(tx_hash)
    receipt = web3.eth.getTransactionReceipt(tx_hash)
    event = event().processReceipt(receipt)
    if event:
        logger.info(f'Success: got {event_name} event after fulfilling condition.')
        logger.debug(
            f'Success: got {event_name} event after fulfilling condition. {receipt}, ::: {event}')
    else:
        logger.debug(f'Something is not right, cannot find the {event_name} event after calling the'
                     f' fulfillment condition. This is the transaction receipt {receipt}')

    if receipt and receipt.status == 0:
        logger.warning(
            f'Transaction failed: tx_hash {tx_hash}, tx event {event_name}, receipt {receipt}')


def is_condition_fulfilled(template_id, service_agreement_id,
                           service_agreement_contract, condition_address, condition_abi, fn_name):
    status = service_agreement_contract.getConditionStatus(
        service_agreement_id,
        build_condition_key(
            condition_address,
            hexstr_to_bytes(Web3Provider.get_web3(),
                            get_fingerprint_by_name(condition_abi, fn_name)),
            template_id
        )
    )
    return status == 1


def get_condition_contract_data(service_definition, name):
    condition_definition = None
    for condition in service_definition['conditions']:
        if condition['name'] == name:
            condition_definition = condition
            break

    if condition_definition is None:
        raise InvalidModule(
            'Failed to find the {} condition in the service definition'.format(name))

    contract = ContractHandler.get(condition_definition['contractName'])
    concise_contract = ContractHandler.get_concise_contract(condition_definition['contractName'])
    return concise_contract, contract, contract.abi, condition_definition
