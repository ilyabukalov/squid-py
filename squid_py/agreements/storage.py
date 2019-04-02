
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import sqlite3


def record_service_agreement(storage_path, service_agreement_id, did, service_definition_id, price,
                             files, start_time,
                             status='pending'):
    """
    Records the given pending service agreement.

    :param storage_path: storage path for the internal db, str
    :param service_agreement_id:
    :param did: DID, str
    :param service_definition_id: identifier of the service inside the asset DDO, str
    :param price: Asset price, int
    :param files:
    :param start_time:
    :param status:
    :return:
    """
    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS service_agreements
               (id VARCHAR PRIMARY KEY, did VARCHAR, service_definition_id INTEGER, 
                price INTEGER, files VARCHAR, start_time INTEGER, status VARCHAR(10));'''
        )
        cursor.execute(
            'INSERT OR REPLACE INTO service_agreements VALUES (?,?,?,?,?,?,?)',
            [service_agreement_id, did, service_definition_id, price, files, start_time,
             status],
        )
        conn.commit()
    finally:
        conn.close()


def update_service_agreement_status(storage_path, service_agreement_id, status='pending'):
    """
    Update the service agreement status.

    :param storage_path: storage path for the internal db, str
    :param service_agreement_id:
    :param status:
    :return:
    """
    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE service_agreements SET status=? WHERE id=?',
            (status, service_agreement_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_service_agreements(storage_path, status='pending'):
    """
    Get service agreements pending to be executed.

    :param storage_path: storage path for the internal db, str
    :param status:
    :return:
    """
    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        return [
            row for row in
            cursor.execute(
                '''
                SELECT id, did, service_definition_id, price, files, start_time, status
                FROM service_agreements 
                WHERE status=?;
                ''',
                (status,))
        ]
    finally:
        conn.close()
