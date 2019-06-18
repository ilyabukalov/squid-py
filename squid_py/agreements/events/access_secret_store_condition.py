
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import time

from eth_utils import add_0x_prefix

from squid_py.did import did_to_id
from squid_py.keeper import Keeper
from squid_py.keeper.utils import process_tx_receipt

logger = logging.getLogger(__name__)


def fulfill_access_secret_store_condition(event, agreement_id, did, service_agreement,
                                          consumer_address, publisher_account, access_condition_id):
    """
    Fulfill the access condition.

    :param event: AttributeDict with the event data.
    :param agreement_id: id of the agreement, hex str
    :param did: DID, str
    :param service_agreement: ServiceAgreement instance
    :param consumer_address: ethereum account address of consumer, hex str
    :param publisher_account: Account instance of the publisher
    :param access_condition_id: hex str the id of the access secretstore condition for this
        `agreement_id`
    """
    if not event:
        logger.debug(f'`fulfill_access_secret_store_condition` got empty event: '
                     f'event listener timed out.')
        return

    keeper = Keeper.get_instance()
    if keeper.condition_manager.get_condition_state(access_condition_id) > 1:
        logger.debug(
            f'access secretstore condition already fulfilled/aborted: '
            f'agreementId={agreement_id}, access secretstore conditionId={access_condition_id}'
        )
        return

    logger.debug(f"grant access (agreement {agreement_id}) after event {event}.")
    name_to_parameter = {param.name: param for param in
                         service_agreement.condition_by_name['accessSecretStore'].parameters}
    document_id = add_0x_prefix(name_to_parameter['_documentId'].value)
    asset_id = add_0x_prefix(did_to_id(did))
    assert document_id == asset_id, f'document_id {document_id} <=> asset_id {asset_id} mismatch.'
    num_tries = 10
    for i in range(num_tries):
        try:
            access_condition = Keeper.get_instance().access_secret_store_condition
            tx_hash = access_condition.fulfill(
                agreement_id, document_id, consumer_address, publisher_account
            )
            success = process_tx_receipt(
                tx_hash,
                getattr(access_condition.contract.events, access_condition.FULFILLED_EVENT)(),
                'AccessSecretStoreCondition.Fulfilled'
            )
            if success or keeper.condition_manager.get_condition_state(access_condition_id) > 1:
                logger.info(f'done fulfill access condition for agreement {agreement_id}')
                break

            logger.info(f'done trial {i} fulfill access condition for agreement {agreement_id}, success?: {bool(success)}')
            time.sleep(2)

        except Exception as e:
            logger.error(f'Error when calling grantAccess condition function (agreementId {agreement_id}): {e}', exc_info=1)
            raise e


fulfillAccessSecretStoreCondition = fulfill_access_secret_store_condition
