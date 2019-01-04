import logging

from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.contract_handler import ContractHandler
from squid_py.modules.v0_1.utils import (
    get_condition_contract_data,
    is_condition_fulfilled,
    process_tx_receipt)
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate

logger = logging.getLogger('service_agreement')


def handlePaymentAction(web3, contract_path, account, service_agreement_id,
                        service_definition, function_name, event_name):
    payment_conditions, contract, abi, payment_condition_definition = get_condition_contract_data(
        service_definition,
        function_name,
    )

    contract_name = service_definition['serviceAgreementContract']['contractName']
    service_agreement_contract = ContractHandler.get_concise_contract(contract_name)
    if is_condition_fulfilled(service_definition[ServiceAgreementTemplate.TEMPLATE_ID_KEY],
                              service_agreement_id, service_agreement_contract,
                              payment_conditions.address, abi, function_name):
        return

    name_to_parameter = {param['name']: param for param in
                         payment_condition_definition['parameters']}
    asset_id = name_to_parameter['assetId']['value']
    price = name_to_parameter['price']['value']
    transact = {'from': account.address, 'gas': DEFAULT_GAS_LIMIT}

    try:
        account.unlock()
        tx_hash = getattr(payment_conditions, function_name)(service_agreement_id, asset_id, price,
                                                             transact=transact)
        process_tx_receipt(web3, tx_hash, getattr(contract.events, event_name), event_name)
    except Exception as e:
        logger.error(f'Error when calling {event_name} function: {e}')
        raise e


def lockPayment(web3, contract_path, account, service_agreement_id,
                service_definition, *args, **kwargs):
    """ Checks if the lockPayment condition has been fulfilled and if not calls
        PaymentConditions.lockPayment smart contract function.

        The account is supposed to have sufficient amount of approved Ocean tokens.
    """
    handlePaymentAction(web3, contract_path, account, service_agreement_id, service_definition,
                        'lockPayment', 'PaymentLocked')


def releasePayment(web3, contract_path, account, service_agreement_id,
                   service_definition, *args, **kwargs):
    """ Checks if the releasePayment condition has been fulfilled and if not calls
        PaymentConditions.releasePayment smart contract function.
    """
    handlePaymentAction(web3, contract_path, account, service_agreement_id, service_definition,
                        'releasePayment', 'PaymentReleased')


def refundPayment(web3, contract_path, account, service_agreement_id,
                  service_definition, *args, **kwargs):
    """ Checks if the refundPayment condition has been fulfilled and if not calls
        PaymentConditions.refundPayment smart contract function.
    """
    handlePaymentAction(web3, contract_path, account, service_agreement_id, service_definition,
                        'refundPayment', 'PaymentRefund')
