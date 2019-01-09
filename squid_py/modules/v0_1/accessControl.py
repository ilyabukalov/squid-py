import logging

from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.contract_handler import ContractHandler
from squid_py.modules.v0_1.utils import (
    get_condition_contract_data,
    is_condition_fulfilled,
    process_tx_receipt)
from squid_py.service_agreement.service_agreement import ServiceAgreement
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate

logger = logging.getLogger('service_agreement')


def grantAccess(web3, contract_path, account, service_agreement_id, service_definition,
                *args, **kwargs):
    """ Checks if grantAccess condition has been fulfilled and if not calls
        AccessConditions.grantAccess smart contract function.
    """
    logger.debug(f'Start handling `grantAccess` action: account {account.address}, '
                 f'saId {service_agreement_id}, '
                 f'templateId {service_definition[ServiceAgreementTemplate.TEMPLATE_ID_KEY]}')
    access_conditions, contract, abi, access_condition_definition = get_condition_contract_data(
        service_definition,
        'grantAccess',
    )
    contract_name = service_definition['serviceAgreementContract']['contractName']
    service_agreement_contract = ContractHandler.get_concise_contract(contract_name)
    if is_condition_fulfilled(service_definition[ServiceAgreementTemplate.TEMPLATE_ID_KEY],
                              service_agreement_id, service_agreement_contract,
                              access_conditions.address, abi, 'grantAccess'):
        logger.debug('grantAccess conditions is already fulfilled, no need to grant access again.')
        return

    name_to_parameter = {param['name']: param for param in
                         access_condition_definition['parameters']}
    asset_id = name_to_parameter['assetId']['value']
    document_key_id = name_to_parameter['documentKeyId']['value']
    transact = {'from': account.address, 'gas': DEFAULT_GAS_LIMIT}
    logger.info(f'About to do grantAccess: account {account.address}, saId {service_agreement_id}, '
                f'assetId {asset_id}, documentKeyId {document_key_id}')
    try:
        account.unlock()
        tx_hash = access_conditions.grantAccess(service_agreement_id, asset_id, document_key_id,
                                                transact=transact)
        process_tx_receipt(web3, tx_hash, contract.events.AccessGranted, 'AccessGranted')
    except Exception as e:
        logger.error(f'Error when calling grantAccess condition function: {e}')
        raise e


def consumeAsset(web3, contract_path, account, service_agreement_id, service_definition,
                 consume_callback, *args, **kwargs):
    if consume_callback:
        consume_callback(
            service_agreement_id, service_definition.get('id'),
            service_definition.get(ServiceAgreement.SERVICE_DEFINITION_ID), account
        )
        logger.info('Done consuming asset.')

    else:
        logger.error('Handling consume asset but the consume callback is not set.')
        raise ValueError('Consume asset triggered but the consume callback is not set.')
