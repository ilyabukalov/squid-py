
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0
import logging

from squid_py.data_store.storage_base import StorageBase

logger = logging.getLogger(__name__)


class AgreementsStorage(StorageBase):

    def record_service_agreement(self, service_agreement_id, did, service_definition_id, price,
                                 files, start_time, status='pending'):
        """
        Records the given pending service agreement.

        :param service_agreement_id:
        :param did: DID, str
        :param service_definition_id: identifier of the service inside the asset DDO, str
        :param price: Asset price, int
        :param files:
        :param start_time:
        :param status:
        :return:
        """
        self._run_query(
            '''CREATE TABLE IF NOT EXISTS service_agreements
               (id VARCHAR PRIMARY KEY, did VARCHAR, service_definition_id INTEGER,
                price INTEGER, files VARCHAR, start_time INTEGER, status VARCHAR(10));'''
        )
        self._run_query(
            'INSERT OR REPLACE INTO service_agreements VALUES (?,?,?,?,?,?,?)',
            (service_agreement_id, did, service_definition_id,
             price, files, start_time, status),
        )

    def update_status(self, service_agreement_id, status):
        """
        Update the service agreement status.

        :param service_agreement_id:
        :param status:
        :return:
        """
        self._run_query(
            'UPDATE service_agreements SET status=? WHERE id=?',
            (status, service_agreement_id),
        )

    def get_service_agreements(self, status='pending'):
        """
        Get service agreements pending to be executed.

        :param status:
        :return:
        """
        return [
            row for row in
            self._run_query(
                '''
                    SELECT id, did, service_definition_id, price, files, start_time, status
                    FROM service_agreements 
                    WHERE status=?;
                ''',
                (status,))
        ]

    def get_agreement_ids(self, status=None):
        try:
            query, args = "SELECT id FROM service_agreements", ()
            if status is not None:
                args = (status,)
                query += " WHERE status=?"

            agreement_ids = {row[0] for row in self._run_query(query, args)}
            return agreement_ids
        except Exception as e:
            logger.error(f'db error getting agreement ids: {e}')
            return []
