import os

from secret_store_client.client import RPCError

from squid_py.agreements.service_agreement import ServiceAgreement
from squid_py.agreements.service_types import ServiceTypes
from squid_py.config_provider import ConfigProvider
from squid_py.ddo.ddo import DDO
from squid_py.examples.example_config import ExampleConfig
from squid_py.keeper.event_listener import EventListener
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.secret_store.secret_store import SecretStore
from squid_py.secret_store.secret_store_provider import SecretStoreProvider
from tests.resources.helper_functions import (
    get_account_from_config,
    get_registered_ddo,
    get_publisher_account
)


def _log_event(event_name):
    def _process_event(event):
        print(f'Received event {event_name}: {event}')

    return _process_event


def test_buy_asset(consumer_ocean_instance, publisher_ocean_instance):
    config = ExampleConfig.get_config()
    ConfigProvider.set_config(config)
    SecretStoreProvider.set_secret_store_class(SecretStore)
    w3 = Web3Provider.get_web3()
    pub_acc = get_publisher_account(config)

    # Register ddo
    ddo = get_registered_ddo(publisher_ocean_instance, pub_acc)
    assert isinstance(ddo, DDO)
    # ocn here will be used only to publish the asset. Handling the asset by the publisher
    # will be performed by the Brizo server running locally

    cons_ocn = consumer_ocean_instance
    # restore the http client because we want the actual Brizo server to do the work
    # not the BrizoMock.
    # Brizo.set_http_client(requests)
    consumer_account = get_account_from_config(cons_ocn._config, 'parity.address1',
                                               'parity.password1')

    downloads_path_elements = len(
        os.listdir(consumer_ocean_instance._config.downloads_path)) if os.path.exists(
        consumer_ocean_instance._config.downloads_path) else 0
    # sign agreement using the registered asset did above
    service = ddo.get_service(service_type=ServiceTypes.ASSET_ACCESS)
    assert ServiceAgreement.SERVICE_DEFINITION_ID in service.as_dictionary()
    sa = ServiceAgreement.from_service_dict(service.as_dictionary())
    # This will send the purchase request to Brizo which in turn will execute the agreement on-chain
    cons_ocn.accounts.request_tokens(consumer_account, 100)
    agreement_id = cons_ocn.assets.order(
        ddo.did, sa.service_definition_id, consumer_account)

    _filter = {'agreementId': w3.toBytes(hexstr=agreement_id)}

    EventListener('ServiceExecutionAgreement', 'AgreementInitialized', filters=_filter).listen_once(
        _log_event('AgreementInitialized'),
        20,
        blocking=True
    )
    EventListener('AccessConditions', 'AccessGranted', filters=_filter).listen_once(
        _log_event('AccessGranted'),
        20,
        blocking=True
    )
    event = EventListener('ServiceExecutionAgreement', 'AgreementFulfilled', filters=_filter).listen_once(
        _log_event('AgreementFulfilled'),
        20,
        blocking=True
    )

    assert event, 'No event received for ServiceAgreement Fulfilled.'
    assert w3.toHex(event.args['agreementId']) == agreement_id
    assert len(os.listdir(config.downloads_path)) == downloads_path_elements + 1

    # decrypt the contentUrls using the publisher account instead of consumer account.
    # if the secret store is working and ACL check is enabled, this should fail
    # since SecretStore decrypt will fail the checkPermissions check
    try:
        cons_ocn.assets.consume(
            agreement_id, ddo.did, service.service_definition_id, pub_acc, config.downloads_path
        )
    except RPCError:
        print('hooray, secret store is working as expected.')
