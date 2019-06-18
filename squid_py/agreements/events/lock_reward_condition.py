
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import time

from squid_py.keeper import Keeper
from squid_py.keeper.utils import process_tx_receipt

logger = logging.getLogger(__name__)


def fulfill_lock_reward_condition(event, agreement_id, price, consumer_account, lock_condition_id):
    """
    Fulfill the lock reward condition.

    :param event: AttributeDict with the event data.
    :param agreement_id: id of the agreement, hex str
    :param price: Asset price, int
    :param consumer_account: Account instance of the consumer
    :param lock_condition_id: hex str the id of the lock reward condition for this `agreement_id`
    """
    if not event:
        logger.warning(f'`fulfill_lock_reward_condition` got empty event: event listener timed out.')
        return

    keeper = Keeper.get_instance()
    if keeper.condition_manager.get_condition_state(lock_condition_id) > 1:
        logger.debug(f'lock reward condition already fulfilled/aborted: '
                     f'agreementId={agreement_id}, lockReward conditionId={lock_condition_id}')
        return

    logger.debug(f"about to lock reward (agreement {agreement_id}) after event {event}.")

    approved = keeper.token.token_approve(
        keeper.lock_reward_condition.address, price, consumer_account)
    logger.debug(f'approval of token transfer was {"" if approved else "NOT"} successful')

    tx_hash = None
    num_tries = 10
    for i in range(num_tries):
        try:
            tx_hash = keeper.lock_reward_condition.fulfill(
                agreement_id, keeper.escrow_reward_condition.address, price, consumer_account
            )
            success = process_tx_receipt(
                tx_hash,
                getattr(keeper.lock_reward_condition.contract.events,
                        keeper.lock_reward_condition.FULFILLED_EVENT)(),
                'LockRewardCondition.Fulfilled',
                agreement_id
            )

            if success or keeper.condition_manager.get_condition_state(lock_condition_id) > 1:
                logger.info(f'done locking reward for agreement {agreement_id}')
                break

            logger.debug(f'done trial {i} locking reward for agreement {agreement_id}, success?: {bool(success)}')
            time.sleep(2)

        except Exception as e:
            logger.error(f'error locking reward (agreementId {agreement_id}): {e}', exc_info=1)
            if not tx_hash:
                raise e


fulfillLockRewardCondition = fulfill_lock_reward_condition
