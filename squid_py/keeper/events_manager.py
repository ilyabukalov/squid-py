#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import os
import time
from datetime import datetime
from threading import Thread

from squid_py.agreements.events.access_secret_store_condition import fulfill_access_secret_store_condition
from squid_py.agreements.service_agreement import ServiceAgreement
from squid_py.data_store.agreements import AgreementsStorage
from squid_py.did_resolver.did_resolver import DIDResolver
from squid_py.keeper.multi_event_listener import MultiEventListener
from squid_py.keeper.web3_provider import Web3Provider

logger = logging.getLogger(__name__)


class AgreementRecord:
    ESCROW_REWARD = AgreementsStorage.ESCROW_REWARD_NAME
    ACCESS_SECRETSTORE = AgreementsStorage.ACCESS_NAME
    LOCK_REWARD = AgreementsStorage.LOCK_REWARD_NAME

    def __init__(self, agreement_id, publisher, consumer, provider, did, condition_ids):
        self.agreement_id = agreement_id
        self.publisher = publisher
        self.consumer = consumer
        self.provider = provider
        self.did = did
        self.condition_ids = {
            self.ACCESS_SECRETSTORE: condition_ids[0],
            self.LOCK_REWARD: condition_ids[1],
            self.ESCROW_REWARD: condition_ids[2],
        }
        self.cond_state = {
            self.ACCESS_SECRETSTORE: 0,
            self.LOCK_REWARD: 0,
            self.ESCROW_REWARD: 0,

        }

        self.created = int(datetime.now().timestamp())

    @property
    def completed(self):
        return len([1 for s in self.cond_state.values() if s >= 2]) == 3

    @property
    def missing_conditions(self):
        return {cond for cond, state in self.cond_state.items() if state < 2}

    def get_condition_id(self, cond):
        return self.condition_ids[cond]

    def update_cond_state(self, cond, state):
        self.cond_state[cond] = state

    @property
    def report(self):
        return f'{self.agreement_id} -> {self.cond_state.items()}'


class EventsManager:
    """Manage the main keeper events listeners necessary for processing service agreements.

    on init
        if not db -> create db
        determine LAST_N_BLOCKS (allow setting from outside using an env var)
        read agreements from local database since LAST_N_BLOCKS
            keep set of completed/fulfilled (all conditions fulfilled) agreements to avoid reprocessing during event processing
            process events for unfulfilled agreements

    in watcher loop
        get AgreementCreated events since LAST_N_BLOCKS or LAST_PROCESSED_BLOCK whichever is larger
            try to overlap LAST_PROCESSED_BLOCK when grabbing events so we don't miss any events

    on new agreement (AgreementCreated event)
        save agreement to db
        init agreement conditions with unfulfilled status
        watch condition events
            on each condition event
                update agreement condition status


    """
    _instance = None

    def __init__(self, keeper, storage_path):
        self._keeper = keeper
        self._storage_path = storage_path
        self._web3 = Web3Provider.get_web3()

        self.known_agreement_ids = set()
        self.completed_ids = set()
        self.other_agreement_ids = set()
        self.condition_event_names = {AgreementRecord.ESCROW_REWARD, AgreementRecord.LOCK_REWARD, AgreementRecord.ACCESS_SECRETSTORE}

        self.event_type_map = {
            'EscrowAccessTemplate': ['_accessConsumer', '_accessProvider', '_did'],
            AgreementRecord.LOCK_REWARD: ['_rewardAddress', '_amount', '_conditionId'],
            AgreementRecord.ACCESS_SECRETSTORE: ['_grantee', '_documentId', '_conditionId'],
            AgreementRecord.ESCROW_REWARD: ['_receiver', '_amount', '_conditionId'],
        }

        self.agreement_listener = MultiEventListener(
            self._keeper.escrow_access_secretstore_template.CONTRACT_NAME,
            self._keeper.escrow_access_secretstore_template.AGREEMENT_CREATED_EVENT,
        )
        self.lock_cond_listener = MultiEventListener(
            self._keeper.lock_reward_condition.CONTRACT_NAME,
            self._keeper.lock_reward_condition.FULFILLED_EVENT,
        )
        self.access_cond_listener = MultiEventListener(
            self._keeper.access_secret_store_condition.CONTRACT_NAME,
            self._keeper.access_secret_store_condition.FULFILLED_EVENT,
        )
        self.reward_cond_listener = MultiEventListener(
            self._keeper.escrow_reward_condition.CONTRACT_NAME,
            self._keeper.escrow_reward_condition.FULFILLED_EVENT,
        )

        w3 = Web3Provider.get_web3()
        db = AgreementsStorage(self._storage_path)
        db.create_tables()
        # get largest block_number from db or `latest` if db has no data
        self.last_block_number = w3.eth.getBlock('latest')
        db_latest = db.get_latest_block_number() or self.last_block_number
        self.last_block_number = min(db_latest, self.last_block_number)
        agreements, conditions = db.get_pending_agreements(self.last_block_number-500)
        # :TODO: prepare pending agreements for processing later in the watcher loop
        # for agrid, data in agreements.items():
        #     AgreementRecord(agrid, )
        # self.pending_agreements = agreements

        self._monitor_is_on = False
        self._monitor_enabled = bool(os.getenv('OCN_SQUID_EVENTS_MONITOR_ON') == 'True')
        try:
            self._monitor_sleep_time = os.getenv('OCN_SQUID_EVENTS_MONITOR_TIME', 30)
        except ValueError:
            self._monitor_sleep_time = 30

        self._monitor_sleep_time = max(self._monitor_sleep_time, 10)
        if self._monitor_enabled:
            logger.info(
                f'events monitor is enabled in env var '
                f'OCN_SQUID_EVENTS_MONITOR_ON (value={os.getenv("OCN_SQUID_EVENTS_MONITOR_ON")}')
            self.start_agreement_events_monitor()

    @staticmethod
    def get_instance(keeper, storage_path):
        if not EventsManager._instance:
            EventsManager._instance = EventsManager(keeper, storage_path)

        return EventsManager._instance

    @property
    def is_monitor_running(self):
        return self._monitor_is_on

    def start_agreement_events_monitor(self):
        if self._monitor_is_on:
            return

        t = Thread(
            target=self.run_monitor,
            daemon=True,
        )
        self._monitor_is_on = True
        t.start()
        logger.debug('started the agreement events monitor')

    def stop_monitor(self):
        self._monitor_is_on = False

    def run_monitor(self):
        i = 0
        completed_ids, id_to_pending_conditions = self.get_completed_and_pending_agreement_ids()
        while True:
            try:
                if not self._monitor_is_on:
                    return

                # for name, event_filter in event_filters.items():
                #     try:
                #         events = event_filter.get_new_entries()
                #         for event in events:
                #             self.process_event(name, event)
                #     except Exception as e:
                #         logger.error(f'Error processing event: {str(e)}', exc_info=1)

            except Exception as e:
                logger.debug(f'Error processing event: {str(e)}')

            time.sleep(self._monitor_sleep_time)
            i += 1

    def start_all_listeners(self):
        self.agreement_listener.start_watching()
        self.lock_cond_listener.start_watching()
        self.access_cond_listener.start_watching()
        self.reward_cond_listener.start_watching()

    def stop_all_listeners(self):
        self.agreement_listener.stop_watching()
        self.lock_cond_listener.stop_watching()
        self.access_cond_listener.stop_watching()
        self.reward_cond_listener.stop_watching()

    def watch_agreement_created_event(self, agreement_id, callback, timeout_callback,
                                      args, timeout, start_time=None):
        self.agreement_listener.add_event_filter(
            '_agreementId',
            Web3Provider.get_web3().toBytes(hexstr=agreement_id),
            callback,
            timeout_callback,
            args,
            timeout,
            start_time
        )

    def watch_agreement_provider_event(self, provider_account, storage_path, callback):
        self.agreement_listener.add_event_filter(
            '_accessProvider',
            provider_account.address,
            self._agreement_created_callback(callback, provider_account),
            None,
            (provider_account, storage_path),
            None,
            pin_event=True
        )
        # self.watch_all_lock_reward_events(provider_account, fulfill_access_secret_store_condition)

    def _agreement_created_callback(self, calback, provider_account):
        def _callback(event, *args):
            agreement_id = None
            try:
                provider = event.args._accessProvider
                agreement_id = Web3Provider.get_web3().toHex(event.args._agreementId)
                if provider.lower() != provider_account.address.lower():
                    logger.debug(f'AgreementCreated event with agreementId {agreement_id}, but for different provider {provider}')
                    return

                if agreement_id not in self.known_agreement_ids:
                    self.known_agreement_ids.add(agreement_id)
                    # agreement = self._keeper.agreement_manager.get_agreement(agreement_id)
                    # publisher = self._keeper.agreement_manager.contract_concise.getAgreementDIDOwner(agreement_id)
                    # consumer, provider = self._keeper.escrow_access_secretstore_template.get_agreement_data(agreement_id)
            except Exception as e:
                logger.error(f'Error reporting agreement: {agreement_id}, {e}')
            return calback(event, *args)

        return _callback

    def _lock_reward_callback(self, callback, provider_account, keeper):
        def _callback(event, *_):
            agreement_id = None
            try:
                logger.debug(f'lockReward.Fulfilled event: {event}')
                agreement_id = Web3Provider.get_web3().toHex(event.args._agreementId)
                if agreement_id in self.agreements_map:
                    agreement = self.agreements_map[agreement_id]
                    ddo = DIDResolver(keeper.did_registry)
                    service_agreement = ServiceAgreement.from_ddo('Access', ddo)
                    state = keeper.condition_manager.get_condition_state(agreement.condition_ids[0])
                    if state < 2:
                        logger.debug(
                            f'Processing lockReward event on agreement {agreement_id} '
                            f'=> access condition is not fulfilled yet, try to fulfill now.'
                        )
                        callback(event, agreement_id, agreement.did, service_agreement,
                                 agreement.consumer, provider_account, agreement.condition_ids[0])

            except Exception as e:
                logger.error(f'Error processing lockReward event: agreement={agreement_id}, error={e}', exc_info=1)
            return

        return _callback

    def watch_all_lock_reward_events(self, provider_account, callback):
        self.lock_cond_listener.add_event_filter(
            None,
            None,
            self._lock_reward_callback(callback, provider_account, self._keeper),
            None,
            (),
            None,
            None,
            pin_event=True
        )

    def watch_lock_reward_event(self, agreement_id, callback, timeout_callback,
                                args, timeout, start_time=None):
        self.lock_cond_listener.add_event_filter(
            '_agreementId',
            Web3Provider.get_web3().toBytes(hexstr=agreement_id),
            callback,
            timeout_callback,
            args,
            timeout,
            start_time
        )

    def watch_access_event(self, agreement_id, callback, timeout_callback,
                           args, timeout, start_time=None):
        self.access_cond_listener.add_event_filter(
            '_agreementId',
            Web3Provider.get_web3().toBytes(hexstr=agreement_id),
            callback,
            timeout_callback,
            args,
            timeout,
            start_time
        )

    def watch_reward_event(self, agreement_id, callback, timeout_callback,
                           args, timeout, start_time=None):
        self.reward_cond_listener.add_event_filter(
            '_agreementId',
            Web3Provider.get_web3().toBytes(hexstr=agreement_id),
            callback,
            timeout_callback,
            args,
            timeout,
            start_time
        )

    def get_agreements_from_keeper(self):
        return []

    def get_last_block_number(self):
        return self.last_block_number - 100

    def get_completed_and_pending_agreement_ids(self):
        store = AgreementsStorage(self._storage_path)
        _, agrid_to_conditions = store.get_pending_agreements(self.get_last_block_number())
        pending_agreements = {_id: conditions for _id, conditions in agrid_to_conditions.items() if conditions}
        completed_ids = store.get_completed_agreement_ids(self.get_last_block_number())
        return completed_ids, pending_agreements
