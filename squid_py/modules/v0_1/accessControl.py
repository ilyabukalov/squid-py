import logging

from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.utils import get_contract_abi_and_address
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
    logger.debug('Start handling `grantAccess` action: account {}, saId {}, templateId {}'
                 .format(account.address, service_agreement_id,
                         service_definition[ServiceAgreementTemplate.TEMPLATE_ID_KEY]))
    access_conditions, contract, abi, access_condition_definition = get_condition_contract_data(
        web3,
        contract_path,
        service_definition,
        'grantAccess',
    )
    contract_name = service_definition['serviceAgreementContract']['contractName']
    service_agreement_address = get_contract_abi_and_address(web3, contract_path, contract_name)[1]
    if is_condition_fulfilled(web3, contract_path, service_definition[ServiceAgreementTemplate.TEMPLATE_ID_KEY],
                              service_agreement_id, service_agreement_address,
                              access_conditions.address, abi, 'grantAccess'):
        logger.debug('grantAccess conditions is already fulfilled, no need to grant access again.')
        return

    name_to_parameter = {param['name']: param for param in access_condition_definition['parameters']}
    asset_id = name_to_parameter['assetId']['value']
    document_key_id = name_to_parameter['documentKeyId']['value']
    transact = {'from': account.address, 'gas': DEFAULT_GAS_LIMIT}
    logger.info('About to do grantAccess: account {}, saId {}, assetId {}, documentKeyId {}'
                .format(account.address, service_agreement_id,
                        asset_id, document_key_id))
    try:
        account.unlock()
        tx_hash = access_conditions.grantAccess(service_agreement_id, asset_id, document_key_id, transact=transact)
        process_tx_receipt(web3, tx_hash, contract.events.AccessGranted, 'AccessGranted')
    except Exception as e:
        logger.error('Error when calling grantAccess condition function: ', e, exc_info=1)
        raise


def consumeAsset(web3, contract_path, account, service_agreement_id, service_definition,
                 consume_callback, *args, **kwargs):

    if consume_callback:
        consume_callback(
            service_agreement_id, service_definition.get('id'),
            service_definition.get(ServiceAgreement.SERVICE_DEFINITION_ID_KEY), account
        )
        logger.info('Done consuming asset.')

    else:
        logger.error('Handling consume asset but the consume callback is not set.')
        raise ValueError('Consume asset triggered but the consume callback is not set.')
