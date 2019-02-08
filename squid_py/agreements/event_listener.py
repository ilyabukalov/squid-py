import importlib

from squid_py.agreements.service_agreement_condition import Event, ServiceAgreementCondition
from squid_py.agreements.storage import update_service_agreement_status
from squid_py.keeper.contract_handler import ContractHandler
from squid_py.keeper.event_listener import EventListener
from squid_py.keeper.service_execution_agreement import ServiceExecutionAgreement
from squid_py.keeper.utils import get_event_def_from_abi
from squid_py.keeper.web3_provider import Web3Provider

MIN_TIMEOUT = 2  # seconds
MAX_TIMEOUT = 60 * 60 * 24 * 7  # 7 days expressed in seconds


def get_event_handler_function(event):
    fn_name = event.handler_function_name
    version = event.handler_version.replace('.', '_')
    import_path = f'squid_py.modules.v{version}.{event.handler_module_name}'
    module = importlib.import_module(import_path, 'squid_py')
    return getattr(module, fn_name)


def watch_service_agreement_events(did, storage_path, account,
                                   service_agreement_id, service_definition, actor_type,
                                   start_time, consume_callback=None):
    """ Subscribes to the events defined in the given service definition, targeted
        for the given actor type. Filters events by the given service agreement ID.

        The service definition format is described in OEP-11.
    """

    # subscribe cleanup
    def _cleanup(_):
        update_service_agreement_status(storage_path, service_agreement_id, 'fulfilled')

    watch_service_agreement_fulfilled(service_agreement_id, service_definition,
                                      _cleanup, )

    # collect service agreement and condition events
    events = []

    # Events from agreement contract `serviceAgreementContract` section. These are the initial
    # events from executing the service agreement.
    for event in service_definition['serviceAgreementContract']['events']:
        if event['actorType'] != actor_type:
            continue

        events.append((service_definition['serviceAgreementContract']['contractName'], Event(event),
                       None, None))

    conditions = [ServiceAgreementCondition(condition_json=condition_dict)
                  for condition_dict in service_definition['conditions']]
    name_to_cond = {cond.name: cond for cond in conditions}
    # Events from conditions
    cond_to_dependants_timeouts = {}
    for cond_instance in conditions:
        if cond_instance.dependencies and cond_instance.timeout > 0:
            for i, cond_dep_name in enumerate(cond_instance.dependencies):
                if cond_instance.timeout_flags[i] == 1:
                    # dependency has a timeout
                    assert cond_dep_name in name_to_cond, f'dependency name {cond_dep_name}' \
                        f' not found in conditions'
                    cond_to_dependants_timeouts[cond_dep_name] = [
                        (cond_instance.name, cond_instance.timeout)]

    for cond_instance in conditions:
        _dependent_cond_timeout = None
        timeout_event = None
        if cond_to_dependants_timeouts.get(cond_instance.name):
            _dependent_cond_timeout = cond_to_dependants_timeouts.get(cond_instance.name)[0]
            timeout_events = [event for event in cond_instance.events if
                              event.name.endswith('Timeout')]
            timeout_event = timeout_events[0] if timeout_events else None
            if not timeout_event:
                raise AssertionError(
                    f'Expected a timeout event in this condition {cond_instance.name} because '
                    f'another'
                    f'condition {_dependent_cond_timeout[0]} depends on this condition timing out.')

        for event in cond_instance.events:
            if event.actor_type != actor_type or event.name.endswith('Timeout'):
                continue
            events.append(
                (cond_instance.contract_name, event, _dependent_cond_timeout, timeout_event))

    # subscribe to the events
    for contract_name, event, dependent_cond_timeout, timeout_event in events:
        timeout = None
        if dependent_cond_timeout and timeout_event:
            dependent_cond_name, timeout = dependent_cond_timeout

        # event of type service_agreement_condition.Event
        fn = get_event_handler_function(event)
        if timeout_event and timeout:
            assert MIN_TIMEOUT < timeout < MAX_TIMEOUT, f'TIMEOUT value not within allowed ' \
                f'range {MIN_TIMEOUT}-{MAX_TIMEOUT}.'

        def _get_callback(func_to_call):
            def _callback(payload):
                func_to_call(
                    account, service_agreement_id,
                    service_definition, consume_callback, did, payload
                )

            return _callback

        contract = ContractHandler.get(contract_name)
        event_abi_dict = get_event_def_from_abi(contract.abi, event.name)
        service_id_arg_name = event_abi_dict['inputs'][0]['name']
        assert service_id_arg_name == ServiceExecutionAgreement.SERVICE_AGREEMENT_ID, \
            f'unknown event first arg, ' \
                f'expected {ServiceExecutionAgreement.SERVICE_AGREEMENT_ID}, ' \
                f'got {service_id_arg_name}'

        _filters = {
            service_id_arg_name: Web3Provider.get_web3().toBytes(hexstr=service_agreement_id)
        }
        EventListener(contract_name, event.name, filters=_filters) \
            .listen_once(_get_callback(fn), timeout, start_time)


def watch_service_agreement_fulfilled(service_agreement_id, service_definition, callback):
    """ Subscribes to the service agreement fulfilled event, filtering by the given
        service agreement ID.
    """
    contract_name = service_definition['serviceAgreementContract']['contractName']
    filters = {
        ServiceExecutionAgreement.SERVICE_AGREEMENT_ID:
            Web3Provider.get_web3().toBytes(hexstr=service_agreement_id)
    }
    EventListener(contract_name, 'AgreementFulfilled', filters=filters).listen_once(callback)
