
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
from datetime import datetime

from squid_py.agreements.events import (access_secret_store_condition, escrow_reward_condition,
                                        lock_reward_condition, verify_reward_condition)
from squid_py.agreements.service_agreement import ServiceAgreement
from squid_py.keeper import Keeper
from .storage import get_service_agreements, record_service_agreement

logger = logging.getLogger(__name__)


def register_service_agreement_consumer(storage_path, publisher_address, agreement_id, did,
                                        service_agreement, service_definition_id, price,
                                        encrypted_files, consumer_account, condition_ids,
                                        consume_callback=None, start_time=None):
    """
    Registers the given service agreement in the local storage.
    Subscribes to the service agreement events.

    :param storage_path:
    :param publisher_address:
    :param agreement_id:
    :param did:
    :param service_agreement:
    :param service_definition_id:
    :param price:
    :param encrypted_files:
    :param consumer_account:
    :param condition_ids:
    :param consume_callback:
    :param start_time:
    :return:
    """
    if start_time is None:
        start_time = int(datetime.now().timestamp())

    record_service_agreement(
        storage_path, agreement_id, did, service_definition_id, price, encrypted_files, start_time)

    process_agreement_events_consumer(
        publisher_address, agreement_id, did, service_agreement,
        price, consumer_account, condition_ids,
        consume_callback
    )


def process_agreement_events_consumer(publisher_address, agreement_id, did, service_agreement,
                                      price, consumer_account, condition_ids,
                                      consume_callback):
    """


    :param publisher_address:
    :param agreement_id:
    :param did:
    :param service_agreement:
    :param price:
    :param consumer_account:
    :param condition_ids:
    :param consume_callback:
    :return:
    """
    conditions_dict = service_agreement.condition_by_name
    keeper = Keeper.get_instance()
    keeper.escrow_access_secretstore_template.subscribe_agreement_created(
        agreement_id,
        60,
        lock_reward_condition.fulfillLockRewardCondition,
        (agreement_id, price, consumer_account)
    )

    if consume_callback:
        def _refund_callback(_price, _publisher_address, _condition_ids):
            def do_refund(_event, _agreement_id, _did, _service_agreement, _consumer_account, *_):
                escrow_reward_condition.refund_reward(
                    _event, _agreement_id, _did, _service_agreement, _price,
                    _consumer_account, _publisher_address, _condition_ids
                )

            return do_refund

        keeper.access_secret_store_condition.subscribe_condition_fulfilled(
            agreement_id,
            conditions_dict['accessSecretStore'].timeout,
            escrow_reward_condition.consume_asset,
            (agreement_id, did, service_agreement, consumer_account, consume_callback),
            _refund_callback(price, publisher_address, condition_ids)
        )


def register_service_agreement_publisher(storage_path, consumer_address, agreement_id, did,
                                         service_agreement, service_definition_id, price,
                                         publisher_account, condition_ids, start_time=None):
    """
    Registers the given service agreement in the local storage.
    Subscribes to the service agreement events.

    :param storage_path:
    :param consumer_address:
    :param agreement_id:
    :param did:
    :param service_agreement:
    :param service_definition_id:
    :param price:
    :param publisher_account:
    :param condition_ids:
    :param start_time:
    :return:
    """
    if start_time is None:
        start_time = int(datetime.now().timestamp())

    record_service_agreement(
        storage_path, agreement_id, did, service_definition_id, price, '', start_time)

    process_agreement_events_publisher(
        publisher_account, agreement_id, did, service_agreement,
        price, consumer_address, condition_ids
    )


def process_agreement_events_publisher(publisher_account, agreement_id, did, service_agreement,
                                       price, consumer_address,
                                       condition_ids):
    """

    :param publisher_account:
    :param agreement_id:
    :param did:
    :param service_agreement:
    :param price:
    :param consumer_address:
    :param condition_ids:
    :return:
    """
    conditions_dict = service_agreement.condition_by_name
    keeper = Keeper.get_instance()
    keeper.lock_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        conditions_dict['lockReward'].timeout,
        access_secret_store_condition.fulfillAccessSecretStoreCondition,
        (agreement_id, did, service_agreement,
         consumer_address, publisher_account)
    )

    keeper.access_secret_store_condition.subscribe_condition_fulfilled(
        agreement_id,
        conditions_dict['accessSecretStore'].timeout,
        escrow_reward_condition.fulfillEscrowRewardCondition,
        (agreement_id, service_agreement,
         price, consumer_address, publisher_account, condition_ids)
    )

    keeper.escrow_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        conditions_dict['escrowReward'].timeout,
        verify_reward_condition.verifyRewardTokens,
        (agreement_id, did, service_agreement,
         price, consumer_address, publisher_account)
    )


def execute_pending_service_agreements(storage_path, account, actor_type, did_resolver_fn):
    """
     Iterates over pending service agreements recorded in the local storage,
    fetches their service definitions, and subscribes to service agreement events.

    :param storage_path:
    :param account:
    :param actor_type:
    :param did_resolver_fn:
    :return:
    """
    keeper = Keeper.get_instance()
    # service_agreement_id, did, service_definition_id, price, files, start_time, status
    for (agreement_id, did, _,
         price, files, start_time, _) in get_service_agreements(storage_path):

        ddo = did_resolver_fn(did)
        for service in ddo.services:
            if service.type != 'Access':
                continue

            consumer_provider_tuple = keeper.escrow_access_secretstore_template.get_agreement_data(
                agreement_id)
            if not consumer_provider_tuple:
                continue

            consumer, provider = consumer_provider_tuple
            did = ddo.did
            service_agreement = ServiceAgreement.from_service_dict(service.as_dictionary())
            condition_ids = service_agreement.generate_agreement_condition_ids(
                agreement_id, did, consumer, provider, keeper)

            if actor_type == 'consumer':
                assert account.address == consumer
                process_agreement_events_consumer(
                    provider, agreement_id, did, service_agreement,
                    price, account, condition_ids, None)
            else:
                assert account.address == provider
                process_agreement_events_publisher(
                    account, agreement_id, did, service_agreement,
                    price, consumer, condition_ids)
