from datetime import datetime

from squid_py.agreements.events import (
    lock_reward_condition,
    access_secret_store_condition,
    escrow_access_secret_store_template,
    escrow_reward_condition
)
from squid_py.keeper import Keeper
from .storage import get_service_agreements, record_service_agreement


def register_service_agreement_consumer(
        storage_path, publisher_address, agreement_id, did, service_agreement,
        service_definition_id, price, encrypted_files, consumer_account,
        consume_callback=None, start_time=None):
    """ Registers the given service agreement in the local storage.
        Subscribes to the service agreement events.
    """
    if start_time is None:
        start_time = int(datetime.now().timestamp())

    conditions_dict = service_agreement.condition_by_name

    record_service_agreement(
        storage_path, agreement_id, did, service_definition_id, price, encrypted_files, start_time)

    keeper = Keeper.get_instance()
    keeper.escrow_access_secretstore_template.subscribe_agreement_created(
        agreement_id,
        60,
        escrow_access_secret_store_template.fulfillLockRewardCondition,
        (agreement_id, did, service_agreement, service_definition_id,
         price, publisher_address, consumer_account)
    )

    keeper.access_secret_store_condition.subscribe_condition_fulfilled(
        agreement_id,
        conditions_dict['accessSecretStore'].timeout,
        access_secret_store_condition.consume_asset,
        (agreement_id, did, service_agreement, service_definition_id,
         encrypted_files, publisher_address, consumer_account, consume_callback),
        access_secret_store_condition.refund_reward
    )


def register_service_agreement_publisher(
        storage_path, consumer_address, agreement_id, did, service_agreement,
        service_definition_id, price, publisher_account,
        start_time=None):
    if start_time is None:
        start_time = int(datetime.now().timestamp())

    conditions_dict = service_agreement.condition_by_name
    record_service_agreement(
        storage_path, agreement_id, did, service_definition_id, price, start_time)

    keeper = Keeper.get_instance()
    keeper.lock_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        conditions_dict['lockReward'].timeout,
        lock_reward_condition.fulfillAccessSecretStoreCondition,
        (agreement_id, did, service_agreement, service_definition_id,
         price, consumer_address, publisher_account)
    )

    keeper.access_secret_store_condition.subscribe_condition_fulfilled(
        agreement_id,
        conditions_dict['accessSecretStore'].timeout,
        access_secret_store_condition.fulfillEscrowRewardCondition,
        (agreement_id, did, service_agreement, service_definition_id,
         price, consumer_address, publisher_account)
    )

    keeper.escrow_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        conditions_dict['escrowReward'].timeout,
        escrow_reward_condition.verifyRewardTokens,
        (agreement_id, did, service_agreement, service_definition_id,
         price, consumer_address, publisher_account)
    )


def execute_pending_service_agreements(storage_path, account, actor_type,
                                       did_resolver_fn):
    """ Iterates over pending service agreements recorded in the local storage,
        fetches their service definitions, and subscribes to service agreement events.
    """
    # service_agreement_id, did, service_definition_id, price, files, start_time, status
    for (service_agreement_id, did, service_definition_id,
         price, files, start_time, _) in get_service_agreements(storage_path):

        ddo = did_resolver_fn(did)
        for service in ddo.services:
            if service.type != 'Access':
                continue

            # watch_service_agreement_events(
            #     ddo.did,
            #     storage_path,
            #     account,
            #     service_agreement_id,
            #     service.as_dictionary(),
            #     actor_type,
            #     start_time
            # )
