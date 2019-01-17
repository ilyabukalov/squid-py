import logging

from squid_py import Ocean, ServiceAgreement, ConfigProvider
from squid_py.examples.example_config import ExampleConfig
from tests.resources.helper_functions import get_account_from_config, get_registered_ddo


def sign_service_agreement():
    ConfigProvider.set_config(ExampleConfig.get_config())
    # make ocean instance and register an asset
    ocn = Ocean()
    acc = get_account_from_config(ocn.config, 'parity.address', 'parity.password')
    ddo = get_registered_ddo(ocn, acc)

    # sign agreement using the registered asset did above
    agreement_id = ServiceAgreement.create_new_agreement_id()
    service_agreement = ServiceAgreement.from_ddo('0', ddo)
    if not acc.unlock():
        logging.warning(f'Unlock of consumer account failed {acc.address}')

    agreement_hash = service_agreement.get_service_agreement_hash(agreement_id)
    signature = acc.sign_hash(agreement_hash)

    logging.info(f'service agreement signed: '
                 f'\nservice agreement id: {agreement_id}, '
                 f'\nagreement hash: {agreement_hash.hex()}, '
                 f'\nsignature: {signature}')


if __name__ == '__main__':
    sign_service_agreement()
