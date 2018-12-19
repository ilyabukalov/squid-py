import time
from datetime import datetime
from threading import Thread

from .utils import get_contract_instance


class EventListener(object):
    def __init__(self, contract_name, event_name, contract_path, web3, from_block='latest', to_block='latest', filters=None):
        contract = get_contract_instance(web3, contract_path, contract_name)
        self.event = getattr(contract.events, event_name)
        self.filters = filters if filters else {}
        self.event_filter = self.event().createFilter(
            fromBlock=from_block, toBlock=to_block, argument_filters=self.filters
        )
        self.event_filter.poll_interval = 0.5
        self.timeout = 60  # seconds

    def listen_once(self, callback, timeout=None):
        Thread(
            target=EventListener.watch_one_event,
            args=(self.event_filter, callback, timeout if timeout is not None else self.timeout),
            daemon=True,
        ).start()

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
                print('Got error grabbing keeper events: ', str(err))

            time.sleep(0.1)
            if 0 < timeout < (int(datetime.now().timestamp()) - start_time):
                callback(None, True)
                break
