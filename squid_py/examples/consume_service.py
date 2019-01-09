
from squid_py import Ocean, ServiceTypes, ServiceAgreement
from squid_py.config import Config
from tests.resources.helper_functions import get_account_from_config, get_registered_ddo
from squid_py.keeper.event_listener import EventListener
from squid_py.keeper.web3_provider import Web3Provider


def _log_event(event_name):
    def _process_event(event):
        print(f'Received event {event_name}: {event}')
    return _process_event


def consume_service():
    """
    Requires all ocean services running.

    """
    w3 = Web3Provider.get_web3()
    # make ocean instance
    path_config = 'config_local.ini'
    ocn = Ocean(Config(path_config))
    acc = get_account_from_config(ocn.config, 'parity.address', 'parity.password')
    ocn.set_main_account(acc.address, acc.password)

    # Register ddo
    ddo = get_registered_ddo(ocn)

    # ocn here will be used only to publish the asset. Handling the asset by the publisher
    # will be performed by the Brizo server running locally

    cons_ocn = Ocean(Config(path_config))
    acc = get_account_from_config(ocn.config, 'parity.address1', 'parity.password1')
    cons_ocn.set_main_account(acc.address, acc.password)

    consumer = cons_ocn.main_account.address

    # sign agreement using the registered asset did above
    service = ddo.get_service(service_type=ServiceTypes.ASSET_ACCESS)
    assert ServiceAgreement.SERVICE_DEFINITION_ID in service.as_dictionary()
    sa = ServiceAgreement.from_service_dict(service.as_dictionary())
    # This will send the purchase request to Brizo which in turn will execute the agreement on-chain
    service_agreement_id, signature = cons_ocn.sign_service_agreement(
        ddo.did, sa.sa_definition_id, consumer)
    cons_ocn.initialize_service_agreement(
        ddo.did, sa.sa_definition_id, service_agreement_id, signature, consumer)
    print('got new service agreement id:', service_agreement_id)
    filter1 = {'serviceAgreementId': w3.toBytes(hexstr=service_agreement_id)}
    filter2 = {'serviceId': w3.toBytes(hexstr=service_agreement_id)}

    EventListener('ServiceAgreement', 'ExecuteAgreement', filters=filter1).listen_once(
        _log_event('ExecuteAgreement'),
        10,
        blocking=True
    )
    EventListener('AccessConditions', 'AccessGranted', filters=filter2).listen_once(
        _log_event('AccessGranted'),
        10,
        blocking=True
    )
    event = EventListener('ServiceAgreement', 'AgreementFulfilled', filters=filter1).listen_once(
        _log_event('AgreementFulfilled'),
        10,
        blocking=True
    )

    assert event, 'No event received for ServiceAgreement Fulfilled.'


if __name__ == '__main__':
    consume_service()
