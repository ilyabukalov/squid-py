"""Ocean module."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0
import logging
from datetime import datetime

from squid_py.data_store import auth_tokens
from squid_py.keeper.web3_provider import Web3Provider


class OceanAuth:
    """Ocean auth class."""
    DEFAULT_TOKEN_VALID_TIME = 30 * 24 * 60 * 60  # in seconds
    SHARED_MESSAGE = "Ocean Protocol authentication"

    def __init__(self, keeper, storage_path):
        self._keeper = keeper
        self._storage_path = storage_path

    @staticmethod
    def hash_message(self, message):
        return Web3Provider.get_web3().sha3(text=message)

    @property
    def shared_message(self):
        return self.SHARED_MESSAGE

    @property
    def timestamp(self):
        return datetime.now().timestamp()

    def get_message(self, timestamp):
        return f'{self.SHARED_MESSAGE}\n{timestamp}'

    def get_message_and_time(self):
        timestamp = datetime.now().timestamp()
        return f'{self.SHARED_MESSAGE}\n{timestamp}', timestamp

    def get(self, signer):
        """

        :param signer:
        :return:
        """
        _hash, _time = self.get_message_and_time()
        try:
            return f'{self._keeper.sign_hash(_hash, signer)}-{_time}'
        except Exception as e:
            logging.error(f'Error signing token: {str(e)}')

    def check(self, token):
        """

        :param token:
        :return:
        """
        sig, timestamp = token.split('-')
        message = self.get_message(timestamp)
        message_hash = self.hash_message(message)
        if timestamp + self.DEFAULT_TOKEN_VALID_TIME > self.timestamp:
            return '0x0'

        address = self._keeper.ec_recover(message_hash, sig)
        return Web3Provider.get_web3().toChecksumAddress(address)

    def store(self, signer):
        """

        :param signer:
        :return:
        """
        token = self.get(signer)
        signature, timestamp = token.split('-')
        auth_tokens.write_token(self._storage_path, signer.address, token, timestamp)
        return token

    def restore(self, signer):
        """

        :param signer:
        :return:
        """
        token, timestamp = auth_tokens.read_token(self._storage_path, signer.address)
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
