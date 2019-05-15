"""Ocean module."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0
import logging
from datetime import datetime

from squid_py.data_store.auth_tokens import AuthTokensStorage
from squid_py.keeper.web3_provider import Web3Provider


class OceanAuth:
    """Ocean auth class."""
    DEFAULT_TOKEN_VALID_TIME = 30 * 24 * 60 * 60  # in seconds
    SHARED_MESSAGE = "Ocean Protocol authentication"

    def __init__(self, keeper, storage_path):
        self._keeper = keeper
        self._tokens_storage = AuthTokensStorage(storage_path)

    @staticmethod
    def hash_message(message):
        return Web3Provider.get_web3().sha3(text=message)

    @property
    def shared_message(self):
        return self.SHARED_MESSAGE

    def get_timestamp(self):
        return int(datetime.now().timestamp())

    def get_message(self, timestamp):
        return f'{self.SHARED_MESSAGE}\n{timestamp}'

    def get_message_and_time(self):
        timestamp = self.get_timestamp()
        return self.get_message(timestamp), timestamp

    def get(self, signer):
        """

        :param signer:
        :return:
        """
        _message, _time = self.get_message_and_time()
        try:
            return f'{self._keeper.sign_hash(_message, signer)}-{_time}'
        except Exception as e:
            logging.error(f'Error signing token: {str(e)}')

    def check(self, token):
        """

        :param token:
        :return:
        """
        parts = token.split('-')
        if len(parts) < 2:
            return '0x0'

        sig, timestamp = parts
        if self.get_timestamp() > (int(timestamp) + self.DEFAULT_TOKEN_VALID_TIME):
            return '0x0'

        message = self.get_message(timestamp)
        address = self._keeper.ec_recover(message, sig)
        return Web3Provider.get_web3().toChecksumAddress(address)

    def store(self, signer):
        """

        :param signer:
        :return:
        """
        token = self.get(signer)
        signature, timestamp = token.split('-')
        self._tokens_storage.write_token(signer.address, token, timestamp)
        return token

    def restore(self, signer):
        """

        :param signer:
        :return:
        """
        token, timestamp = self._tokens_storage.read_token(signer.address)
        if not token:
            return None

        address = self.check(token)

        return token if address == signer.address else None

    def is_stored(self, account):
        """

        :param account:
        :return:
        """
        return self.restore(account) is not None
