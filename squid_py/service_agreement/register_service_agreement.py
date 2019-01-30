from datetime import datetime

from .event_listener import watch_service_agreement_events
from .storage import get_service_agreements, record_service_agreement


def register_service_agreement(storage_path, account, service_agreement_id,
                               did, service_definition, actor_type, service_definition_id, price,
                               files, consume_callback=None,
                               start_time=None):
    """ Registers the given service agreement in the local storage.
        Subscribes to the service agreement events.
    """
    if start_time is None:
        start_time = int(datetime.now().timestamp())

    record_service_agreement(storage_path, service_agreement_id, did, service_definition_id, price,
                             files, start_time)
    watch_service_agreement_events(
        did, storage_path, account,
        service_agreement_id, service_definition, actor_type,
        start_time, consume_callback
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

            watch_service_agreement_events(
                ddo.did,
                storage_path,
                account,
                service_agreement_id,
                service.as_dictionary(),
                actor_type,
                start_time
            )
