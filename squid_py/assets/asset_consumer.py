import logging
import json
import os

from squid_py.service_agreement.service_agreement import ServiceAgreement
from squid_py.did import did_to_id

logger = logging.getLogger(__name__)


class AssetConsumer:
    # TODO: asset consumer should be a `callable` to handle consuming an asset after it has
    #   been purchased.

    @staticmethod
    def download(
            service_agreement_id,
            service_definition_id,
            ddo,
            consumer_account,
            destination,
            brizo,
            secret_store
    ):
        """
        Download asset data files or result files from a compute job

        :return:
        """
        did = ddo.did
        files = ddo.metadata['base']['encryptedFiles']
        files = files if isinstance(files, str) else files[0]
        sa = ServiceAgreement.from_ddo(service_definition_id, ddo)
        service_url = sa.service_endpoint
        if not service_url:
            logger.error(
                'Consume asset failed, service definition is missing the "serviceEndpoint".')
            raise AssertionError(
                'Consume asset failed, service definition is missing the "serviceEndpoint".')

        # decrypt the contentUrls
        decrypted_content_urls = json.loads(
            secret_store.decrypt_document(did_to_id(did), files)
        )
        if isinstance(decrypted_content_urls, str):
            decrypted_content_urls = [decrypted_content_urls]
        logger.debug(f'got decrypted contentUrls: {decrypted_content_urls}')

        asset_folder = os.path.join(destination, f'datafile.{did_to_id(did)}.{service_definition_id}')
        if not os.path.exists(asset_folder):
            os.mkdir(asset_folder)

        brizo.consume_service(
            service_agreement_id,
            service_url,
            consumer_account.address,
            decrypted_content_urls,
            asset_folder
        )
