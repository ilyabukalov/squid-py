import logging

from squid_py import Ocean, ServiceTypes, ServiceAgreement
from squid_py.config import Config
from tests.resources.helper_functions import get_account_from_config, get_registered_ddo


def sign_service_agreement():
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

    logging.info(f'service agreement id: {service_agreement_id}')
    logging.info(f'service agreement signature: {signature}')