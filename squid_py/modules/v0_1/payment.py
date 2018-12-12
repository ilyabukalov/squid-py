import logging

from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.utils import get_contract_abi_and_address
from squid_py.modules.v0_1.utils import (
    get_condition_contract_data,
    is_condition_fulfilled,
    process_tx_receipt)
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate

logger = logging.getLogger('service_agreement')


def handlePaymentAction(web3, contract_path, account, service_agreement_id,
                        service_definition, function_name, event_name):
    payment_conditions, contract, abi, payment_condition_definition = get_condition_contract_data(
        web3,
        contract_path,
        service_definition,
        function_name,
    )

    contract_name = service_definition['serviceAgreementContract']['contractName']
    service_agreement_address = get_contract_abi_and_address(web3, contract_path, contract_name)[1]
    if is_condition_fulfilled(web3, contract_path, service_definition[ServiceAgreementTemplate.TEMPLATE_ID_KEY],
                              service_agreement_id, service_agreement_address,
                              payment_conditions.address, abi, function_name):
        return

    name_to_parameter = {param['name']: param for param in payment_condition_definition['parameters']}
    asset_id = name_to_parameter['assetId']['value']
    price = name_to_parameter['price']['value']
    transact = {'from': account.address, 'gas': DEFAULT_GAS_LIMIT}

    try:
        account.unlock()
        tx_hash = getattr(payment_conditions, function_name)(service_agreement_id, asset_id, price, transact=transact)
        process_tx_receipt(web3, tx_hash, getattr(contract.events, event_name), event_name)
    except Exception as e:
        logger.error('Error when calling %s function: %s', event_name, e, exc_info=1)
        raise


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
