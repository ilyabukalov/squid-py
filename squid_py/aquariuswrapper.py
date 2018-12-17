import json
import logging

import requests


class AquariusWrapper(object):

    def __init__(self, aquarius_url):
        """
        The Metadata class is a wrapper on the Metadata Store, which has exposed a REST API

        :param aquarius_url: Url of the aquarius instance.
        """
        if '/api/v1/aquarius/assets' in aquarius_url:
            aquarius_url = aquarius_url[:aquarius_url.find('/api/v1/aquarius/assets')]

        self._base_url = '{}/api/v1/aquarius/assets'.format(aquarius_url)
        self._headers = {'content-type': 'application/json'}

        logging.debug("Metadata Store connected at {}".format(aquarius_url))
        logging.debug("Metadata Store API documentation at {}/api/v1/docs".format(aquarius_url))
        logging.debug("Metadata assets at {}".format(self._base_url))

    @property
    def url(self):
        """Base URL of the aquarius instance"""
        return self._base_url + '/ddo/'

    def get_service_endpoint(self, did):
        """
        Retrieve the endpoint with the ddo for a given did.

        :param did: Asset did.
        :return: Return the url where find the ddo.
        """
        return self._base_url + '/ddo/%s' % did

    def list_assets(self):
        """
        List all the assets registered in the aquarius instance.

        :return: List of dids.
        """
        asset_list = json.loads(requests.get(self._base_url).content)
        if asset_list and 'ids' in asset_list:
            return asset_list['ids']
        return []

    def get_asset_metadata(self, did):
        """
        Retrieve asset ddo for a given did.

        :param did: Asset did
        :return: Asset ddo.
        """
        response = requests.get(self._base_url + '/ddo/%s' % did).content
        if not response:
            return {}

        try:
            parsed_response = json.loads(response)
        except TypeError:
            parsed_response = None

        if parsed_response is None:
            return {}
        return parsed_response

    def list_assets_metadata(self):
        """
        List all the ddos registered in the aquarius instance.

        :return: List of ddos.
        """
        return json.loads(requests.get(self._base_url + '/ddo').content)

    def publish_asset_metadata(self, ddo):
        """
        Register asset ddo in aquarius.

        :param ddo: Asset ddo.
        :return: Json response.
        """
        asset_did = ddo.did
        response = requests.post(self._base_url + '/ddo', data=ddo.as_text(), headers=self._headers)
        if response.status_code == 500:
            raise ValueError("This Asset ID already exists! \n\tHTTP Error message: \n\t\t{}".format(response.text))
        elif response.status_code != 201:
            raise Exception("{} ERROR Full error: \n{}".format(response.status_code, response.text))
        elif response.status_code == 201:
            response = json.loads(response.content)
            logging.debug("Published asset DID {}".format(asset_did))
            return response
        else:
            raise Exception(
                "Unhandled ERROR: status-code {}, error message {}".format(response.status_code, response.text))

    def update_asset_metadata(self, did, ddo):
        """
        Update the ddo of a did already registered.

        :param did: Asset did.
        :param ddo: Asset ddo.
        :return: Json response.
        """
        return json.loads(
            requests.put(self._base_url + '/ddo/%s' % did, data=ddo.as_text(),
                         headers=self._headers).content)

    def text_search(self, text, sort=None, offset=100, page=0):
        """
        Search in aquarius using text query. Given the string aquarius will do a full-text query using an index
        to search in all the documents.
        In this way using mongodb driver https://docs.mongodb.com/manual/reference/operator/query/text/ and in this
        one using elastic driver https://www.elastic.co/guide/en/elasticsearch/guide/current/full-text-search.html.
        If you use a different driver you have to take care that this functionality is already implemented.

        :param text: String to be search.
        :param sort: 1/-1 to sort ascending or descending.
        :param offset: Integer with the number of elements displayed per page.
        :param page: Integer with the number of page.
        :return: List of ddos.
        """
        payload = {"text": text, "sort": sort, "offset": offset, "page": page}
        response = requests.get(
            self._base_url + '/ddo/query',
            params=payload,
            headers=self._headers
        ).content

        if not response:
            return {}

        try:
            parsed_response = json.loads(response)
        except TypeError:
            parsed_response = None

        if parsed_response is None:
            return []
        elif isinstance(parsed_response, list):
            return parsed_response
        else:
            raise ValueError('Unknown search response, expecting a list got "%s.' % type(parsed_response))

    def query_search(self, search_query):
        """
        Search using a query. We are using the mongodb query model to search for documents
        https://docs.mongodb.com/manual/tutorial/query-documents/
        If you use the elastic driver we are doing a parser to convert the query into elastic search format,
        but this could be in a early stage.

        Example: query_search({"service.metadata.base.name":"London Weather 2011"})

        :param search_query: Json query following mongodb syntax.
        :return: List of ddos.
        """
        response = requests.post(
            self._base_url + '/ddo/query',
            data=json.dumps(search_query),
            headers=self._headers
        ).content

        if not response:
            return {}

        try:
            parsed_response = json.loads(response)
        except TypeError:
            parsed_response = None

        if parsed_response is None:
            return []
        elif isinstance(parsed_response, list):
            return parsed_response
        else:
            raise ValueError('Unknown search response, expecting a list got "%s.' % type(parsed_response))

    def retire_asset_metadata(self, did):
        """
        Retire asset ddo of Aquarius

        :param did: Asset did
        :return: Json response.
        """
        response = requests.delete(self._base_url + '/ddo/%s' % did, headers=self._headers)
        logging.debug("Removed asset DID: {} from metadata store".format(did))
        return response
