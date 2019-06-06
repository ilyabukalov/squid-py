
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from eth_utils import add_0x_prefix

from squid_py.did import did_to_id
from squid_py.keeper import Keeper

logger = logging.getLogger(__name__)


def fulfill_access_secret_store_condition(event, agreement_id, did, service_agreement,
                                          consumer_address, publisher_account):
    """
    Fulfill the access condition.

    :param event: AttributeDict with the event data.
    :param agreement_id: id of the agreement, hex str
    :param did: DID, str
    :param service_agreement: ServiceAgreement instance
    :param consumer_address: ethereum account address of consumer, hex str
    :param publisher_account: Account instance of the publisher
    """
    logger.debug(f"grant access after event {event}.")
    name_to_parameter = {param.name: param for param in
                         service_agreement.condition_by_name['accessSecretStore'].parameters}
    document_id = add_0x_prefix(name_to_parameter['_documentId'].value)
    asset_id = add_0x_prefix(did_to_id(did))
    assert document_id == asset_id, f'document_id {document_id} <=> asset_id {asset_id} mismatch.'
    try:
        Keeper.get_instance().access_secret_store_condition.fulfill(
            agreement_id, document_id, consumer_address, publisher_account
        )
    except Exception as e:
        logger.error(f'Error when calling grantAccess condition function: {e}', exc_info=1)
        raise e


fulfillAccessSecretStoreCondition = fulfill_access_secret_store_condition
