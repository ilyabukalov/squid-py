import json
from unittest.mock import Mock

from squid_py import ServiceAgreement


class BrizoMock(object):
    def __init__(self, ocean_instance, account):
        self.ocean_instance = ocean_instance
        self.account = account

    def get(self, url, *args, **kwargs):
        response = Mock()
        response.data = b'good luck squiddo.'
        response.status_code = 200
        response.url = 'http://mock.url/filename.mock?blahblah'
        response.content = b'asset data goes here.'
        return response

    def post(self, url, data=None, **kwargs):
        response = Mock()
        if url.endswith('initialize'):
            payload = json.loads(data)
            did = payload['did']
            sa_id = payload['serviceAgreementId']
            sa_def_id = payload[ServiceAgreement.SERVICE_DEFINITION_ID]
            signature = payload['signature']
            consumer = payload['consumerAddress']
            self.ocean_instance.execute_service_agreement(
                did,
                sa_def_id,
                sa_id,
                signature,
                consumer,
                self.account)
            response.status_code = 201
        else:
            response.status_code = 404

        return response
