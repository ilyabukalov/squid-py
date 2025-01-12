#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import json
import logging
import os

from ocean_utils.agreements.service_agreement import ServiceAgreement
from ocean_utils.agreements.service_types import ServiceTypes
from ocean_utils.did import did_to_id

logger = logging.getLogger(__name__)


class AssetConsumer:

    @staticmethod
    def download(service_agreement_id, service_index, ddo, consumer_account, destination,
                 brizo, secret_store, index=None):
        """
        Download asset data files or result files from a compute job.

        :param service_agreement_id: Service agreement id, str
        :param service_index: identifier of the service inside the asset DDO, str
        :param ddo: DDO
        :param consumer_account: Account instance of the consumer
        :param destination: Path, str
        :param brizo: Brizo instance
        :param secret_store: SecretStore instance
        :param index: Index of the document that is going to be downloaded, int
        :return: Asset folder path, str
        """
        did = ddo.did
        encrypted_files = ddo.metadata['encryptedFiles']
        encrypted_files = (
            encrypted_files if isinstance(encrypted_files, str)
            else encrypted_files[0]
        )
        sa = ServiceAgreement.from_ddo(ServiceTypes.ASSET_ACCESS, ddo)
        consume_url = sa.service_endpoint
        if not consume_url:
            logger.error(
                'Consume asset failed, service definition is missing the "serviceEndpoint".')
            raise AssertionError(
                'Consume asset failed, service definition is missing the "serviceEndpoint".')

        if ddo.get_service('authorization'):
            secret_store_service = ddo.get_service(service_type=ServiceTypes.AUTHORIZATION)
            secret_store_url = secret_store_service.service_endpoint
            secret_store.set_secret_store_url(secret_store_url)

        # decrypt the contentUrls
        decrypted_content_urls = json.loads(
            secret_store.decrypt_document(did_to_id(did), encrypted_files)
        )

        if isinstance(decrypted_content_urls, str):
            decrypted_content_urls = [decrypted_content_urls]
        logger.debug(f'got decrypted contentUrls: {decrypted_content_urls}')

        if not os.path.isabs(destination):
            destination = os.path.abspath(destination)
        if not os.path.exists(destination):
            os.mkdir(destination)

        asset_folder = os.path.join(destination,
                                    f'datafile.{did_to_id(did)}.{service_index}')
        if not os.path.exists(asset_folder):
            os.mkdir(asset_folder)
        if index is not None:
            assert isinstance(index, int), logger.error('index has to be an integer.')
            assert index >= 0, logger.error('index has to be 0 or a positive integer.')
            assert index < len(decrypted_content_urls), logger.error(
                'index can not be bigger than the number of files')
        brizo.consume_service(
            service_agreement_id,
            consume_url,
            consumer_account,
            decrypted_content_urls,
            asset_folder,
            index
        )
        return asset_folder
