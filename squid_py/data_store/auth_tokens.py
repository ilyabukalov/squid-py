
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0
import logging

import sqlite3


logger = logging.getLogger(__name__)


AUTH_TOKENS_TABLE = 'auth_tokens'


def write_token(storage_path, address, signed_token, created_at):
    """
    Store signed token for session management.

    :param storage_path: storage path for the internal db, str
    :param address: hex str the ethereum address that signed the token
    :param signed_token: hex str the signed token
    :param created_at: date-time of token creation

    """

    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            f'''CREATE TABLE IF NOT EXISTS {AUTH_TOKENS_TABLE}
               (address VARCHAR PRIMARY KEY, signed_token VARCHAR, created VARCHAR);'''
        )
        cursor.execute(
            f'''INSERT OR REPLACE 
                INTO {AUTH_TOKENS_TABLE} 
                VALUES (?,?,?)''',
            [address, signed_token, created_at],
        )
        conn.commit()
    finally:
        conn.close()


def update_token(storage_path, address, signed_token, created_at):
    """
    Update/replace the stored signed token for the given ethereum address

    :param storage_path: storage path for the internal db, str
    :param address: hex str the ethereum address that signed the token
    :param signed_token: hex str the signed token
    :param created_at: date-time of token creation

    """
    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            f'''UPDATE {AUTH_TOKENS_TABLE} 
                SET signed_token=?, created=? 
                WHERE address=?''',
            (signed_token, created_at, address),
        )
        conn.commit()
    finally:
        conn.close()


def read_token(storage_path, address):
    """
    Retrieve stored signed token for the given ethereum address

    :param storage_path: storage path for the internal db, str
    :param address: hex str the ethereum address that signed the token
    :return: tuple (signed_token, created_at)
    """
    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        rows = cursor.execute(
                f'''SELECT signed_token, created 
                    FROM {AUTH_TOKENS_TABLE}  
                    WHERE address=?;''',
                (address,)
        )
        if rows:
            return rows[0]
        return rows[0] if rows else (None, None)
    except Exception as e:
        logging.error(f'Error reading token: {e}')
        return None, None
    finally:
        conn.close()
