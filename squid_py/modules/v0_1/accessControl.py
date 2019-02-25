import logging

from squid_py import ConfigProvider
from squid_py.agreements.service_agreement import ServiceAgreement
from squid_py.agreements.service_agreement_template import ServiceAgreementTemplate
from squid_py.brizo.brizo_provider import BrizoProvider
from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.did_resolver.did_resolver import DIDResolver
from squid_py.keeper import Keeper
from squid_py.keeper.contract_handler import ContractHandler
from squid_py.modules.v0_1.utils import (
    get_condition_contract_data,
    is_condition_fulfilled,
    process_tx_receipt)
from squid_py.secret_store.secret_store_provider import SecretStoreProvider

logger = logging.getLogger('service_agreement')


def grant_access(account, service_agreement_id, service_definition,
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
    document_key_id = name_to_parameter['documentKeyId']['value']
    transact = {'from': account.address, 'gas': DEFAULT_GAS_LIMIT}
    logger.info(f'About to do grantAccess: account {account.address}, saId {service_agreement_id}, '
                f'documentKeyId {document_key_id}')
    try:
        Keeper.get_instance().unlock_account(account)
        tx_hash = access_conditions.grantAccess(service_agreement_id, document_key_id,
                                                transact=transact)
        process_tx_receipt(tx_hash, contract.events.AccessGranted, 'AccessGranted')
    except Exception as e:
        logger.error(f'Error when calling grantAccess condition function: {e}')
        raise e


def consume_asset(account, service_agreement_id, service_definition,
                  consume_callback, did, *args, **kwargs):
    if consume_callback:
        config = ConfigProvider.get_config()
        secret_store = SecretStoreProvider.get_secret_store(
            config.secret_store_url, config.parity_url, account
        )
        brizo = BrizoProvider.get_brizo()

        consume_callback(
            service_agreement_id,
            service_definition.get(ServiceAgreement.SERVICE_DEFINITION_ID),
            DIDResolver(Keeper.get_instance().did_registry).resolve(did),
            account,
            ConfigProvider.get_config().downloads_path,
            brizo,
            secret_store
        )

        logger.info('Done consuming asset.')

    else:
        logger.info('Handling consume asset but the consume callback is not set. The user '
                    'can trigger consume asset directly using the agreementId and assetId.')


grantAccess = grant_access
consumeAsset = consume_asset
