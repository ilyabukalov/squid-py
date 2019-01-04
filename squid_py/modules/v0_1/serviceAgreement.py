import logging

from squid_py.keeper.contract_handler import ContractHandler
from squid_py.modules.v0_1.utils import process_tx_receipt

logger = logging.getLogger('service_agreement')


def fulfillAgreement(web3, contract_path, account, service_agreement_id,
                     service_definition, *args, **kwargs):
    """ Checks if serviceAgreement has been fulfilled and if not calls
        ServiceAgreement.fulfillAgreement smart contract function.
    """
    contract_name = service_definition['serviceAgreementContract']['contractName']
    service_agreement = ContractHandler.get(contract_name)
    service_agreement_address = service_agreement.address
    service_agreement_concise = ContractHandler.get_concise_contract(contract_name)

    logger.info(f'About to do fulfillAgreement: account {account.address}, '
                f'saId {service_agreement_id}, '
                f'ServiceAgreement address {service_agreement_address}')
    try:
        account.unlock()
        tx_hash = service_agreement_concise.fulfillAgreement(service_agreement_id,
                                                             transact={'from': account.address})
        process_tx_receipt(
            web3, tx_hash, service_agreement.events.AgreementFulfilled, 'AgreementFulfilled')
    except Exception as e:
        logger.error(f'Error when calling fulfillAgreement function: {e}')
        raise e


def terminateAgreement(web3, contract_path, account, service_agreement_id,
                       service_definition, *args, **kwargs):
    fulfillAgreement(web3, contract_path, account, service_agreement_id, service_definition, *args,
                     **kwargs)
