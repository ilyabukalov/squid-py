#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import os

from squid_py.brizo.brizo import Brizo


class BrizoMock(object):
    def __init__(self, ocean_instance=None, account=None):
        if not ocean_instance:
            from tests.resources.helper_functions import get_publisher_ocean_instance
            ocean_instance = get_publisher_ocean_instance(
                init_tokens=False, use_ss_mock=False, use_brizo_mock=True
            )

        self.ocean_instance = ocean_instance
        self.account = account
        if not account:
            from tests.resources.helper_functions import get_publisher_account
            self.account = get_publisher_account()

        # ocean_instance.agreements.watch_provider_events(self.account)

    def initialize_service_agreement(self, did, agreement_id, service_definition_id,
                                     signature, account_address, purchase_endpoint):
        print(f'BrizoMock.initialize_service_agreement: purchase_endpoint={purchase_endpoint}')
        self.ocean_instance.agreements.create(
            did,
            service_definition_id,
            agreement_id,
            signature,
            account_address,
            self.account
        )
        return True

    @staticmethod
    def consume_service(service_agreement_id, service_endpoint, account_address, files,
                        destination_folder, *_, **__):
        for f in files:
            with open(os.path.join(destination_folder, os.path.basename(f['url'])), 'w') as of:
                of.write(f'mock data {service_agreement_id}.{service_endpoint}.{account_address}')

    @staticmethod
    def execute_service(agreement_id, service_endpoint, consumer_account, workflow_ddo):
        return True

    @staticmethod
    def get_brizo_url(config):
        return Brizo.get_brizo_url(config)

    @staticmethod
    def get_purchase_endpoint(config):
        return f'{Brizo.get_brizo_url(config)}/services/access/initialize'

    @staticmethod
    def get_consume_endpoint(config):
        return f'{Brizo.get_brizo_url(config)}/services/consume'

    @staticmethod
    def get_execute_endpoint(config):
        return f'{Brizo.get_brizo_url(config)}/services/exec'
