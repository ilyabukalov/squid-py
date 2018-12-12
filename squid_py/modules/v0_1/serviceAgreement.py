import logging

from web3.contract import ConciseContract

from squid_py.keeper.utils import get_contract_abi_and_address
from squid_py.modules.v0_1.utils import process_tx_receipt

logger = logging.getLogger('service_agreement')


def fulfillAgreement(web3, contract_path, account, service_agreement_id,
                     service_definition, *args, **kwargs):
    """ Checks if serviceAgreement has been fulfilled and if not calls
        ServiceAgreement.fulfillAgreement smart contract function.
    """
    contract_name = service_definition['serviceAgreementContract']['contractName']
    abi, service_agreement_address = get_contract_abi_and_address(web3, contract_path, contract_name)
    service_agreement = web3.eth.contract(address=service_agreement_address, abi=abi, ContractFactoryClass=ConciseContract)

    logger.info('About to do fulfillAgreement: account {}, saId {}, ServiceAgreement address {}'
                .format(account.address, service_agreement_id, service_agreement_address))
    try:
        account.unlock()
        tx_hash = service_agreement.fulfillAgreement(service_agreement_id, transact={'from': account.address})
        contract = web3.eth.contract(address=service_agreement_address, abi=abi)
        process_tx_receipt(web3, tx_hash, contract.events.AgreementFulfilled, 'AgreementFulfilled')
    except Exception as e:
        logger.error('Error when calling fulfillAgreement function: ', e, exc_info=1)
        raise


def terminateAgreement(web3, contract_path, account, service_agreement_id,
                       service_definition, *args, **kwargs):
    fulfillAgreement(web3, contract_path, account, service_agreement_id, service_definition, *args, **kwargs)
