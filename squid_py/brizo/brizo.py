import json
import logging
import os

import requests

from squid_py.exceptions import OceanInitializeServiceAgreementError
from squid_py.service_agreement.service_agreement import ServiceAgreement

logger = logging.getLogger(__name__)


class Brizo(object):
    """
    `Brizo` is the name chosen for the asset service provider.

    The main functions available are:
    - initialize_service_agreement
    - consume_service
    - run_compute_service (not implemented yet)

    """
    _http_client = requests

    @staticmethod
    def set_http_client(http_client):
        """Set the http client to something other than the default `requests`"""
        Brizo._http_client = http_client

    @staticmethod
    def initialize_service_agreement(did, agreement_id, service_definition_id, signature,
                                     account_address,
                                     purchase_endpoint):
        """
        Send a request to the service provider (purchase_endpoint) to initialize the service
        agreement for the asset identified by `did`.

        :param did: str -- id of the asset includes the `did:op:` prefix
        :param agreement_id: hex str
        :param service_definition_id: str -- identifier of the service inside the asset DDO
        :param signature: hex str -- signed agreement hash
        :param account_address: hex str -- ethereum address of the consumer signing this agreement
        :param purchase_endpoint: str -- url of the service provider
        :return:
        """
        payload = Brizo.prepare_purchase_payload(
            did, agreement_id, service_definition_id, signature, account_address
        )
        response = Brizo._http_client.post(
            purchase_endpoint, data=payload,
            headers={'content-type': 'application/json'}
        )
        if response and hasattr(response, 'status_code'):
            if response.status_code != 201:
                msg = (f'Initialize service agreement failed at the purchaseEndpoint '
                       f'{purchase_endpoint}, reason {response.text}, status {response.status_code}'
                       )
                logger.error(msg)
                raise OceanInitializeServiceAgreementError(msg)

            logger.debug(
                f'Service agreement initialized successfully, service agreement id {agreement_id},'
                f' purchaseEndpoint {purchase_endpoint}')
            return True

    @staticmethod
    def consume_service(service_agreement_id, service_endpoint, account_address, urls,
                        destination_folder):
        for url in urls:
            if url.startswith('"') or url.startswith("'"):
                url = url[1:-1]

            consume_url = (f'{service_endpoint}?url={url}&serviceAgreementId='
                           f'{service_agreement_id}&consumerAddress={account_address}'
                           )
            logger.info(f'invoke consume endpoint with this url: {consume_url}')
            response = Brizo._http_client.get(consume_url)
            if response.status_code == 200:
                download_url = response.url.split('?')[0]
                file_name = os.path.basename(download_url)
                with open(os.path.join(destination_folder, file_name), 'wb') as f:
                    f.write(response.content)
                    logger.info(f'Saved downloaded file in {f.name}')
            else:
                logger.warning(f'consume failed: {response.reason}')

    @staticmethod
    def prepare_purchase_payload(did, agreement_id, service_definition_id, signature,
                                 consumer_address):
        # Prepare a payload to send to `Brizo`
        return json.dumps({
            'did': did,
            'serviceAgreementId': agreement_id,
            ServiceAgreement.SERVICE_DEFINITION_ID: service_definition_id,
            'signature': signature,
            'consumerAddress': consumer_address
        })

    @staticmethod
    def get_brizo_url(config):
        """
        Return the Brizo component url.

        :param config: Config
        :return: Url, str
        """
        brizo_url = 'http://localhost:8030'
        if config.has_option('resources', 'brizo.url'):
            brizo_url = config.get('resources', 'brizo.url') or brizo_url

        brizo_path = '/api/v1/brizo'
        return f'{brizo_url}{brizo_path}'

    @staticmethod
    def get_purchase_endpoint(config):
        """
        Return the endpoint to purchase the asset.

        :param config:Config
        :return: Url, str
        """
        return f'{Brizo.get_brizo_url(config)}/services/access/initialize'

    @staticmethod
    def get_service_endpoint(config):
        """
        Return the url to consume the asset.

        :param config: Config
        :return: Url, str
        """
        return f'{Brizo.get_brizo_url(config)}/services/consume'
