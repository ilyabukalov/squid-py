import logging

logger = logging.getLogger(__name__)


class EventFilter:
    def __init__(self, event_name, event, arguments_filter, from_block, to_block):
        self.event_name = event_name
        self.event = event
        self.arguments_filter = arguments_filter
        self.block_range = (from_block, to_block)
        self._filter = None

    def recreate_filter(self):
        self._create_filter()

    def _create_filter(self):
        self._filter = self.event().createFilter(
            fromBlock=self.block_range[0],
            toBlock=self.block_range[1],
            argument_filters=self.arguments_filter
        )

    def get_all_entries(self, max_tries=3):
        self._create_filter()
        i = 0
        while i < max_tries:
            try:
                logs = self._filter.get_all_entries()
                return logs
            except ValueError as e:
                logger.debug(f'Got error fetching event logs: {str(e)}')
                if 'Filter not found' in str(e):
                    self._create_filter()
                else:
                    raise

            i += 1
