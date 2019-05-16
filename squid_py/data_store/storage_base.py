
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0
import sqlite3


class StorageBase:
    def __init__(self, storage_path):
        self._storage_path = storage_path
        self._conn = None
        if self._storage_path == ':memory:':
            self._conn = sqlite3.connect(self._storage_path)

    def _connect(self):
        if self._storage_path != ':memory:':
            self._conn = sqlite3.connect(self._storage_path)

    def _disconnect(self):
        if self._storage_path != ':memory:':
            self._conn.close()

    def _run_query(self, query, args=None):
        try:
            self._connect()
            cursor = self._conn.cursor()
            result = cursor.execute(query, args or ())
            self._conn.commit()
            return result
        finally:
            self._disconnect()
