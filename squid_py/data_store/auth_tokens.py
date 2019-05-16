
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0
import logging

import sqlite3


logger = logging.getLogger(__name__)


AUTH_TOKENS_TABLE = 'auth_tokens'


class AuthTokensStorage:
    def __init__(self, storage_path):
        self._storage_path = storage_path
        self.conn = sqlite3.connect(self._storage_path)

    def _run_query(self, query, args=None):
        cursor = self.conn.cursor()
        result = cursor.execute(query, args or ())
        self.conn.commit()
        return result

    def write_token(self, address, signed_token, created_at):
        """
        Store signed token for session management.

        :param storage_path: storage path for the internal db, str
        :param address: hex str the ethereum address that signed the token
        :param signed_token: hex str the signed token
        :param created_at: date-time of token creation

        """

        self._run_query(
            f'''CREATE TABLE IF NOT EXISTS {AUTH_TOKENS_TABLE}
               (address VARCHAR PRIMARY KEY, signed_token VARCHAR, created VARCHAR);'''
        )
        self._run_query(
            f'''INSERT OR REPLACE 
                INTO {AUTH_TOKENS_TABLE} 
                VALUES (?,?,?)''',
            [address, signed_token, created_at],
        )

    def update_token(self, address, signed_token, created_at):
        """
        Update/replace the stored signed token for the given ethereum address

        :param storage_path: storage path for the internal db, str
        :param address: hex str the ethereum address that signed the token
        :param signed_token: hex str the signed token
        :param created_at: date-time of token creation

        """
        self._run_query(
            f'''UPDATE {AUTH_TOKENS_TABLE} 
                SET signed_token=?, created=? 
                WHERE address=?''',
            (signed_token, created_at, address),
        )

    def read_token(self, address):
        """
        Retrieve stored signed token for the given ethereum address

        :param storage_path: storage path for the internal db, str
        :param address: hex str the ethereum address that signed the token
        :return: tuple (signed_token, created_at)
        """
        try:
            rows = [row for row in self._run_query(
                f'''SELECT signed_token, created 
                    FROM {AUTH_TOKENS_TABLE}  
                    WHERE address=?;''',
                (address,))
            ]

            return rows[0] if rows else (None, None)

        except Exception as e:
            logging.error(f'Error reading token: {e}')
            return None, None
