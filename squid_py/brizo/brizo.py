"""Brizo module."""

#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import json
import logging
import os

from tqdm import tqdm

from squid_py.agreements.service_agreement import ServiceAgreement
from squid_py.exceptions import OceanInitializeServiceAgreementError
from squid_py.http_requests.requests_session import get_requests_session

logger = logging.getLogger(__name__)


class Brizo:
    """
    `Brizo` is the name chosen for the asset service provider.

    The main functions available are:
    - initialize_service_agreement
    - consume_service
    - run_compute_service (not implemented yet)

    """
    _http_client = get_requests_session()

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

        :param did: id of the asset includes the `did:op:` prefix, str
        :param agreement_id: id of the agreement, hex str
        :param service_definition_id: identifier of the service inside the asset DDO, str
        :param signature: signed agreement hash, hex str
        :param account_address: ethereum address of the consumer signing this agreement, hex str
        :param purchase_endpoint: url of the service provider, str
        :return: bool
        """
        payload = Brizo._prepare_purchase_payload(
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

            logger.info(
                f'Service agreement initialized successfully, service agreement id {agreement_id},'
                f' purchaseEndpoint {purchase_endpoint}')
            return True

    @staticmethod
    def consume_service(service_agreement_id, service_endpoint, account_address, files,
                        destination_folder):
        """
        Call the brizo endpoint to get access to the different files that form the asset.

        :param service_agreement_id: Service Agreement Id, str
        :param service_endpoint: Url to consume, str
        :param account_address: ethereum address of the consumer signing this agreement, hex-str
        :param files: List containing the files to be consumed, list
        :param destination_folder: Path, str
        """
        for file in files:
            url = file['url']
            if url.startswith('"') or url.startswith("'"):
                url = url[1:-1]

            consume_url = (f'{service_endpoint}?url={url}&serviceAgreementId='
                           f'{service_agreement_id}&consumerAddress={account_address}'
                           )
            logger.info(f'invoke consume endpoint with this url: {consume_url}')
            response = Brizo._http_client.get(consume_url, stream=True)

            file_name = os.path.basename(url)
            total_size = response.headers.get('content-length', 0)

            logger.info(f'Total size of {file_name}: {total_size} bytes.')
            bar = tqdm(total=int(total_size), unit='KB', leave=False, smoothing=0.1)
            if response.status_code == 200:
                with open(os.path.join(destination_folder, file_name), 'wb') as f:
                    for chunk in response.iter_content():
                        f.write(chunk)
                        bar.update(len(chunk))
                logger.info(f'Saved downloaded file in {f.name}')
            else:
                logger.warning(f'consume failed: {response.reason}')

    @staticmethod
    def _prepare_purchase_payload(did, service_agreement_id, service_definition_id, signature,
                                  consumer_address):
        """Prepare a payload to send to `Brizo`.

        :param did: DID, str
        :param service_agreement_id: Service Agreement Id, str
        :param service_definition_id: identifier of the service inside the asset DDO, str
        service in the DDO (DID document)
        :param signature: the signed agreement message hash which includes
         conditions and their parameters values and other details of the agreement, str
        :param consumer_address: ethereum address of the consumer signing this agreement, hex-str
        :return: dict
        """
        return json.dumps({
            'did': did,
            'serviceAgreementId': service_agreement_id,
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
