"""
Aquarius module.
Help to communicate with the metadata store.
"""
#                                   Apache License
#                             Version 2.0, January 2004
#                          http://www.apache.org/licenses/
#
#     TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
#
#     1. Definitions.
#
#        "License" shall mean the terms and conditions for use, reproduction,
#        and distribution as defined by Sections 1 through 9 of this document.
#
#        "Licensor" shall mean the copyright owner or entity authorized by
#        the copyright owner that is granting the License.
#
#        "Legal Entity" shall mean the union of the acting entity and all
#        other entities that control, are controlled by, or are under common
#        control with that entity. For the purposes of this definition,
#        "control" means (i) the power, direct or indirect, to cause the
#        direction or management of such entity, whether by contract or
#        otherwise, or (ii) ownership of fifty percent (50%) or more of the
#        outstanding shares, or (iii) beneficial ownership of such entity.
#
#        "You" (or "Your") shall mean an individual or Legal Entity
#        exercising permissions granted by this License.
#
#        "Source" form shall mean the preferred form for making modifications,
#        including but not limited to software source code, documentation
#        source, and configuration files.
#
#        "Object" form shall mean any form resulting from mechanical
#        transformation or translation of a Source form, including but
#        not limited to compiled object code, generated documentation,
#        and conversions to other media types.
#
#        "Work" shall mean the work of authorship, whether in Source or
#        Object form, made available under the License, as indicated by a
#        copyright notice that is included in or attached to the work
#        (an example is provided in the Appendix below).
#
#        "Derivative Works" shall mean any work, whether in Source or Object
#        form, that is based on (or derived from) the Work and for which the
#        editorial revisions, annotations, elaborations, or other modifications
#        represent, as a whole, an original work of authorship. For the purposes
#        of this License, Derivative Works shall not include works that remain
#        separable from, or merely link (or bind by name) to the interfaces of,
#        the Work and Derivative Works thereof.
#
#        "Contribution" shall mean any work of authorship, including
#        the original version of the Work and any modifications or additions
#        to that Work or Derivative Works thereof, that is intentionally
#        submitted to Licensor for inclusion in the Work by the copyright owner
#        or by an individual or Legal Entity authorized to submit on behalf of
#        the copyright owner. For the purposes of this definition, "submitted"
#        means any form of electronic, verbal, or written communication sent
#        to the Licensor or its representatives, including but not limited to
#        communication on electronic mailing lists, source code control systems,
#        and issue tracking systems that are managed by, or on behalf of, the
#        Licensor for the purpose of discussing and improving the Work, but
#        excluding communication that is conspicuously marked or otherwise
#        designated in writing by the copyright owner as "Not a Contribution."
#
#        "Contributor" shall mean Licensor and any individual or Legal Entity
#        on behalf of whom a Contribution has been received by Licensor and
#        subsequently incorporated within the Work.
#
#     2. Grant of Copyright License. Subject to the terms and conditions of
#        this License, each Contributor hereby grants to You a perpetual,
#        worldwide, non-exclusive, no-charge, royalty-free, irrevocable
#        copyright license to reproduce, prepare Derivative Works of,
#        publicly display, publicly perform, sublicense, and distribute the
#        Work and such Derivative Works in Source or Object form.
#
#     3. Grant of Patent License. Subject to the terms and conditions of
#        this License, each Contributor hereby grants to You a perpetual,
#        worldwide, non-exclusive, no-charge, royalty-free, irrevocable
#        (except as stated in this section) patent license to make, have made,
#        use, offer to sell, sell, import, and otherwise transfer the Work,
#        where such license applies only to those patent claims licensable
#        by such Contributor that are necessarily infringed by their
#        Contribution(s) alone or by combination of their Contribution(s)
#        with the Work to which such Contribution(s) was submitted. If You
#        institute patent litigation against any entity (including a
#        cross-claim or counterclaim in a lawsuit) alleging that the Work
#        or a Contribution incorporated within the Work constitutes direct
#        or contributory patent infringement, then any patent licenses
#        granted to You under this License for that Work shall terminate
#        as of the date such litigation is filed.
#
#     4. Redistribution. You may reproduce and distribute copies of the
#        Work or Derivative Works thereof in any medium, with or without
#        modifications, and in Source or Object form, provided that You
#        meet the following conditions:
#
#        (a) You must give any other recipients of the Work or
#            Derivative Works a copy of this License; and
#
#        (b) You must cause any modified files to carry prominent notices
#            stating that You changed the files; and
#
#        (c) You must retain, in the Source form of any Derivative Works
#            that You distribute, all copyright, patent, trademark, and
#            attribution notices from the Source form of the Work,
#            excluding those notices that do not pertain to any part of
#            the Derivative Works; and
#
#        (d) If the Work includes a "NOTICE" text file as part of its
#            distribution, then any Derivative Works that You distribute must
#            include a readable copy of the attribution notices contained
#            within such NOTICE file, excluding those notices that do not
#            pertain to any part of the Derivative Works, in at least one
#            of the following places: within a NOTICE text file distributed
#            as part of the Derivative Works; within the Source form or
#            documentation, if provided along with the Derivative Works; or,
#            within a display generated by the Derivative Works, if and
#            wherever such third-party notices normally appear. The contents
#            of the NOTICE file are for informational purposes only and
#            do not modify the License. You may add Your own attribution
#            notices within Derivative Works that You distribute, alongside
#            or as an addendum to the NOTICE text from the Work, provided
#            that such additional attribution notices cannot be construed
#            as modifying the License.
#
#        You may add Your own copyright statement to Your modifications and
#        may provide additional or different license terms and conditions
#        for use, reproduction, or distribution of Your modifications, or
#        for any such Derivative Works as a whole, provided Your use,
#        reproduction, and distribution of the Work otherwise complies with
#        the conditions stated in this License.
#
#     5. Submission of Contributions. Unless You explicitly state otherwise,
#        any Contribution intentionally submitted for inclusion in the Work
#        by You to the Licensor shall be under the terms and conditions of
#        this License, without any additional terms or conditions.
#        Notwithstanding the above, nothing herein shall supersede or modify
#        the terms of any separate license agreement you may have executed
#        with Licensor regarding such Contributions.
#
#     6. Trademarks. This License does not grant permission to use the trade
#        names, trademarks, service marks, or product names of the Licensor,
#        except as required for reasonable and customary use in describing the
#        origin of the Work and reproducing the content of the NOTICE file.
#
#     7. Disclaimer of Warranty. Unless required by applicable law or
#        agreed to in writing, Licensor provides the Work (and each
#        Contributor provides its Contributions) on an "AS IS" BASIS,
#        WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
#        implied, including, without limitation, any warranties or conditions
#        of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
#        PARTICULAR PURPOSE. You are solely responsible for determining the
#        appropriateness of using or redistributing the Work and assume any
#        risks associated with Your exercise of permissions under this License.
#
#     8. Limitation of Liability. In no event and under no legal theory,
#        whether in tort (including negligence), contract, or otherwise,
#        unless required by applicable law (such as deliberate and grossly
#        negligent acts) or agreed to in writing, shall any Contributor be
#        liable to You for damages, including any direct, indirect, special,
#        incidental, or consequential damages of any character arising as a
#        result of this License or out of the use or inability to use the
#        Work (including but not limited to damages for loss of goodwill,
#        work stoppage, computer failure or malfunction, or any and all
#        other commercial damages or losses), even if such Contributor
#        has been advised of the possibility of such damages.
#
#     9. Accepting Warranty or Additional Liability. While redistributing
#        the Work or Derivative Works thereof, You may choose to offer,
#        and charge a fee for, acceptance of support, warranty, indemnity,
#        or other liability obligations and/or rights consistent with this
#        License. However, in accepting such obligations, You may act only
#        on Your own behalf and on Your sole responsibility, not on behalf
#        of any other Contributor, and only if You agree to indemnify,
#        defend, and hold each Contributor harmless for any liability
#        incurred by, or claims asserted against, such Contributor by reason
#        of your accepting any such warranty or additional liability.
#
#     END OF TERMS AND CONDITIONS
#
#     APPENDIX: How to apply the Apache License to your work.
#
#        To apply the Apache License to your work, attach the following
#        boilerplate notice, with the fields enclosed by brackets "[]"
#        replaced with your own identifying information. (Don't include
#        the brackets!)  The text should be enclosed in the appropriate
#        comment syntax for the file format. We also recommend that a
#        file or class name and description of purpose be included on the
#        same "printed page" as the copyright notice for easier
#        identification within third-party archives.
#
#   Copyright 2018 BigchainDB GmbH
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#

import json
import logging

import requests

from squid_py.aquarius.exceptions import AquariusGenericError
from squid_py.assets.asset import Asset

logger = logging.getLogger('aquarius')


class Aquarius:
    """Aquarius wrapper to call different endpoint of aquarius component."""

    def __init__(self, aquarius_url):
        """
        The Metadata class is a wrapper on the Metadata Store, which has exposed a REST API.

        :param aquarius_url: Url of the aquarius instance.
        """
        # :HACK:
        if '/api/v1/aquarius/assets' in aquarius_url:
            aquarius_url = aquarius_url[:aquarius_url.find('/api/v1/aquarius/assets')]

        self._base_url = f'{aquarius_url}/api/v1/aquarius/assets'
        self._headers = {'content-type': 'application/json'}

        logging.debug(f'Metadata Store connected at {aquarius_url}')
        logging.debug(f'Metadata Store API documentation at {aquarius_url}/api/v1/docs')
        logging.debug(f'Metadata assets at {self._base_url}')

    @property
    def url(self):
        """Base URL of the aquarius instance."""
        return f'{self._base_url}/ddo'

    def get_service_endpoint(self, did):
        """
        Retrieve the endpoint with the ddo for a given did.

        :param did: Asset DID string
        :return: Return the url of the the ddo location
        """
        return f'{self.url}/{did}'

    def list_assets(self):
        """
        List all the assets registered in the aquarius instance.

        :return: List of DID string
        """
        response = requests.get(self._base_url).content
        if not response:
            return {}

        try:
            asset_list = json.loads(response)
        except TypeError:
            asset_list = None
        except ValueError:
            raise ValueError(response.decode('UTF-8'))

        if not asset_list:
            return []

        if 'ids' in asset_list:
            return asset_list['ids']
        return []

    def get_asset_ddo(self, did):
        """
        Retrieve asset ddo for a given did.

        :param did: Asset DID string
        :return: DDO instance
        """
        response = requests.get(f'{self.url}/{did}').content
        if not response:
            return {}
        try:
            parsed_response = json.loads(response)
        except TypeError:
            parsed_response = None
        except ValueError:
            raise ValueError(response.decode('UTF-8'))
        if parsed_response is None:
            return {}
        return Asset(dictionary=parsed_response)

    def get_asset_metadata(self, did):
        """
        Retrieve asset metadata for a given did.

        :param did: Asset DID string
        :return: metadata key of the DDO instance
        """
        response = requests.get(f'{self._base_url}/metadata/{did}').content
        if not response:
            return {}
        try:
            parsed_response = json.loads(response)
        except TypeError:
            parsed_response = None
        except ValueError:
            raise ValueError(response.decode('UTF-8'))
        if parsed_response is None:
            return {}
        return parsed_response['metadata']

    def list_assets_ddo(self):
        """
        List all the ddos registered in the aquarius instance.

        :return: List of DDO instance
        """
        return json.loads(requests.get(self.url).content)

    def publish_asset_ddo(self, ddo):
        """
        Register asset ddo in aquarius.

        :param ddo: DDO instance
        :return: API response (depends on implementation)
        """
        try:
            asset_did = ddo.did
            response = requests.post(self.url, data=ddo.as_text(),
                                     headers=self._headers)
        except AttributeError:
            raise AttributeError('DDO invalid. Review that all the required parameters are filled.')
        if response.status_code == 500:
            raise ValueError(
                f'This Asset ID already exists! \n\tHTTP Error message: \n\t\t{response.text}')
        elif response.status_code != 201:
            raise Exception(f'{response.status_code} ERROR Full error: \n{response.text}')
        elif response.status_code == 201:
            response = json.loads(response.content)
            logger.debug(f'Published asset DID {asset_did}')
            return response
        else:
            raise Exception(f'Unhandled ERROR: status-code {response.status_code}, '
                            f'error message {response.text}')

    def update_asset_ddo(self, did, ddo):
        """
        Update the ddo of a did already registered.

        :param did: Asset DID string
        :param ddo: DDO instance
        :return: API response (depends on implementation)
        """
        response = requests.put(f'{self.url}/{did}', data=ddo.as_text(),
                                headers=self._headers)
        if response.status_code == 200 or response.status_code == 201:
            return json.loads(response.content)
        else:
            raise Exception(f'Unable to update DDO: {response.content}')

    def text_search(self, text, sort=None, offset=100, page=0):
        """
        Search in aquarius using text query.

        Given the string aquarius will do a full-text query to search in all documents.

        Currently implemented are the MongoDB and Elastic Search drivers.

        For a detailed guide on how to search, see the MongoDB driver documentation:
        mongodb driverCurrently implemented in:
        https://docs.mongodb.com/manual/reference/operator/query/text/

        And the Elastic Search documentation:
        https://www.elastic.co/guide/en/elasticsearch/guide/current/full-text-search.html
        Other drivers are possible according to each implementation.

        :param text: String to be search.
        :param sort: 1/-1 to sort ascending or descending.
        :param offset: Integer with the number of elements displayed per page.
        :param page: Integer with the number of page.
        :return: List of DDO instance
        """
        payload = {"text": text, "sort": sort, "offset": offset, "page": page}
        response = requests.get(
            f'{self.url}/query',
            params=payload,
            headers=self._headers
        )
        if response.status_code == 200:
            return self._parse_search_response(response.content)
        else:
            raise Exception(f'Unable to search for DDO: {response.content}')

    def query_search(self, search_query):
        """
        Search using a query.

        Currently implemented is the MongoDB query model to search for documents according to:
        https://docs.mongodb.com/manual/tutorial/query-documents/

        And an Elastic Search driver, which implements a basic parser to convert the query into
        elastic search format.

        Example: query_search({"service.metadata.base.name":"London Weather 2011"})

        :param search_query: Python dictionary, query following mongodb syntax
        :return: List of DDO instance
        """
        response = requests.post(
            f'{self.url}/query',
            data=json.dumps(search_query),
            headers=self._headers
        )
        if response.status_code == 200:
            return self._parse_search_response(response.content)
        else:
            raise Exception(f'Unable to search for DDO: {response.content}')

    def retire_asset_ddo(self, did):
        """
        Retire asset ddo of Aquarius.

        :param did: Asset DID string
        :return: API response (depends on implementation)
        """
        response = requests.delete(f'{self.url}/{did}', headers=self._headers)
        if response.status_code == 200:
            logging.debug(f'Removed asset DID: {did} from metadata store')
            return response

        raise AquariusGenericError(f'Unable to remove DID: {response}')

    def validate_metadata(self, metadata):
        """
        Validate that the metadata of your ddo is valid.

        :param metadata: Json dict
        :return: bool
        """
        response = requests.post(
            f'{self.url}/validate',
            data=json.dumps(metadata),
            headers=self._headers
        )
        if response.content == b'true\n':
            return True
        else:
            logger.info(self._parse_search_response(response.content))
            return False

    @staticmethod
    def _parse_search_response(response):
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
            raise ValueError(
                f'Unknown search response, expecting a list got {type(parsed_response)}.')
