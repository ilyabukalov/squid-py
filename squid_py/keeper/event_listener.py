import logging
import time
from datetime import datetime
from threading import Thread

from squid_py.keeper.contract_handler import ContractHandler

logger = logging.getLogger(__name__)


class EventListener(object):
    def __init__(self, contract_name, event_name, from_block='latest', to_block='latest',
                 filters=None):
        contract = ContractHandler.get(contract_name)
        self.event = getattr(contract.events, event_name)
        self.filters = filters if filters else {}
        self.event_filter = self.event().createFilter(
            fromBlock=from_block, toBlock=to_block, argument_filters=self.filters
        )
        self.event_filter.poll_interval = 0.5
        self.timeout = 60  # seconds

    def listen_once(self, callback, timeout=None, blocking=False):
        """

        :param callback: a callback function that takes one argument the event dict
        :param timeout: float timeout in seconds
        :param blocking: bool blocks this call until the event is detected
        :return: event if blocking is True and an event is received, otherwise returns None
        """
        events = []
        original_callback = callback

        def _callback(event):
            events.append(event)
            original_callback(event)

        if blocking:
            callback = _callback

        Thread(
            target=EventListener.watch_one_event,
            args=(self.event_filter, callback, timeout if timeout is not None else self.timeout),
            daemon=True,
        ).start()
        if blocking:
            while not events:
                time.sleep(0.2)

            return events[0]

        return None

    @staticmethod
    def watch_one_event(event_filter, callback, timeout):
        start_time = int(datetime.now().timestamp())
        while True:
            try:
                events = event_filter.get_all_entries()
                if events:
                    callback(events[0])
                    break

            except ValueError as err:
                # ignore error, but log it
                logger.error(f'Got error grabbing keeper events: {str(err)}')

            time.sleep(0.1)
            if 0 < timeout < (int(datetime.now().timestamp()) - start_time):
                callback(None)
                break
