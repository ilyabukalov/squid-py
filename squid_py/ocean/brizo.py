import os
import logging

import requests

from squid_py.exceptions import OceanInitializeServiceAgreementError
from squid_py.utils.utilities import prepare_purchase_payload


logger = logging.getLogger(__name__)


class Brizo(object):
    _http_client = requests

    @staticmethod
    def set_http_client(http_client):
        Brizo._http_client = http_client

    @staticmethod
    def initialize_service_agreement(did, agreement_id, service_index, signature, account_address, purchase_endpoint):
        payload = prepare_purchase_payload(did, agreement_id, service_index, signature, account_address)
        response = Brizo._http_client.post(
            purchase_endpoint, data=payload,
            headers={'content-type': 'application/json'}
        )
        if response and hasattr(response, 'status_code'):
            if response.status_code != 201:
                msg = (
                    'Initialize service agreement failed at the purchaseEndpoint {}, ' 
                    'reason {}, status {}'
                    .format(purchase_endpoint, response.text, response.status_code)
                )
                logger.error(msg)
                raise OceanInitializeServiceAgreementError(msg)

            logger.debug(
                'Service agreement initialized successfully, service agreement id %s,'
                ' purchaseEndpoint %s',
                agreement_id, purchase_endpoint)

            return True

    @staticmethod
    def consume_service(service_agreement_id, service_endpoint, account_address, urls, destination_folder):
        for url in urls:
            if url.startswith('"') or url.startswith("'"):
                url = url[1:-1]

            consume_url = (
                    '%s?url=%s&serviceAgreementId=%s&consumerAddress=%s' %
                    (service_endpoint, url, service_agreement_id, account_address)
            )
            logger.info('invoke consume endpoint with this url: %s', consume_url)
            response = Brizo._http_client.get(consume_url)
            if response.status_code == 200:
                download_url = response.url.split('?')[0]
                file_name = os.path.basename(download_url)
                with open(os.path.join(destination_folder, file_name), 'wb') as f:
                    f.write(response.content)
                    logger.info('Saved downloaded file in "%s"', f.name)
            else:
                logger.warning('consume failed: %s', response.reason)
