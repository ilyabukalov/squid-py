import logging

from eth_utils import remove_0x_prefix
from secret_store_client.client import Client

from squid_py.config_provider import ConfigProvider

logger = logging.getLogger(__name__)


class SecretStore(object):
    """Wrapper around the secret store client."""
    _client_class = Client

    def __init__(self, url=None):
        config = ConfigProvider.get_config()
        self.secret_store_url = url if url is not None else config.secret_store_url
        self._secret_store_client = SecretStore._client_class(
            self.secret_store_url, config.parity_url, config.parity_address,
            config.parity_password
        )

    @staticmethod
    def set_client(secret_store_client):
        SecretStore._client_class = secret_store_client

    def encrypt_document(self, document_id, content, threshold=0):
        """
        encrypt string data using the DID as an secret store id,
        if secret store is enabled then return the result from secret store encryption

        None for no encryption performed

        :param document_id:
        :param content:
        :param threshold:
        :return:
            None -- if encryption failed
            hex str -- the encrypted document
        """
        return self._secret_store_client.publish_document(
            remove_0x_prefix(document_id), content, threshold
        )

    def decrypt_document(self, document_id, encrypted_content):
        """
        Decrypt a previously encrypted content using the secret store keys identified
        by document_id.

        Note that decryption requires permission already granted to the consumer account.

        :param document_id:
        :param encrypted_content: hex str -- the encrypted content from a previous
            `encrypt_document` operation
        :return:
            None -- if decryption failed
            str -- the original content that was encrypted previously
        """
        return self._secret_store_client.decrypt_document(remove_0x_prefix(document_id),
                                                          encrypted_content)
