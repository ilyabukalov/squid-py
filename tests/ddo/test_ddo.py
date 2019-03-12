"""
    Test did_lib
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

from squid_py.ddo.ddo import DDO
from squid_py.ddo.public_key_base import (
    PUBLIC_KEY_STORE_TYPE_BASE64,
    PUBLIC_KEY_STORE_TYPE_BASE85,
    PUBLIC_KEY_STORE_TYPE_HEX,
    PUBLIC_KEY_STORE_TYPE_PEM
)
from squid_py.did import DID
from tests.resources.helper_functions import get_resource_path
from tests.resources.tiers import unit_test

public_key_store_types = [
    PUBLIC_KEY_STORE_TYPE_PEM,
    PUBLIC_KEY_STORE_TYPE_HEX,
    PUBLIC_KEY_STORE_TYPE_BASE64,
    PUBLIC_KEY_STORE_TYPE_BASE85,
]

TEST_SERVICE_TYPE = 'ocean-meta-storage'
TEST_SERVICE_URL = 'http://localhost:8005'

TEST_METADATA = """
{
   "base": {
     "name": "UK Weather information 2011",
     "type": "dataset",
     "description": "Weather information of UK including temperature and humidity",
     "size": "3.1gb",
     "dateCreated": "2012-10-10T17:00:000Z",
     "author": "Met Office",
     "license": "CC-BY",
     "copyrightHolder": "Met Office",
     "encoding": "UTF-8",
     "compression": "zip",
     "contentType": "text/csv",
     "workExample": "423432fsd,51.509865,-0.118092,2011-01-01T10:55:11+00:00,7.2,68",
     "files": [
       {
         "url": "https://testocnfiles.blob.core.windows.net/testfiles/testzkp.pdf",
         "checksum": "efb2c764274b745f5fc37f97c6b0e761",
         "contentLength": "4535431",
         "resourceId": "access-log2018-02-13-15-17-29-18386C502CAEA932"
       }
     ],
     "links": [
       { "name": "Sample of Asset Data", "type": "sample", "url": "https://foo.com/sample.csv" },
       { "name": "Data Format Definition", "type": "format", "AssetID": 
       "4d517500da0acb0d65a716f61330969334630363ce4a6a9d39691026ac7908ea" }
     ],
     "inLanguage": "en",
     "tags": "weather, uk, 2011, temperature, humidity",
     "price": 10
   },
   "curation": {
     "rating": 0.93,
     "numVotes": 123,
     "schema": "Binary Voting"
   },
   "additionalInformation": {
     "updateFrequency": "yearly",
     "structuredMarkup": [
       {
         "uri": "http://skos.um.es/unescothes/C01194/jsonld",
         "mediaType": "application/ld+json"
       },
       {
         "uri": "http://skos.um.es/unescothes/C01194/turtle",
         "mediaType": "text/turtle"
       }
     ]
   }
}
"""

TEST_SERVICES = [
    {"type": "OpenIdConnectVersion1.0Service",
     "serviceEndpoint": "https://openid.example.com/"
     },
    {
        "type": "CredentialRepositoryService",
        "serviceEndpoint": "https://repository.example.com/service/8377464"
    },
    {
        "type": "XdiService",
        "serviceEndpoint": "https://xdi.example.com/8377464"
    },
    {
        "type": "HubService",
        "serviceEndpoint": "https://hub.example.com/.identity/did:op:0123456789abcdef/"
    },
    {
        "type": "MessagingService",
        "serviceEndpoint": "https://example.com/messages/8377464"
    },
    {
        "type": "SocialWebInboxService",
        "serviceEndpoint": "https://social.example.com/83hfh37dj",
        "values": {
            "description": "My public social inbox",
            "spamCost": {
                "amount": "0.50",
                "currency": "USD"
            }
        }
    },
    {
        "type": "BopsService",
        "serviceEndpoint": "https://bops.example.com/enterprise/"
    },
    {
        "type": "Consume",
        "serviceEndpoint": "http://mybrizo.org/api/v1/brizo/services/consume?pubKey=${"
                           "pubKey}&agreementId={agreementId}&url={url}"
    },
    {
        "type": "Compute",
        "serviceDefinitionId": "1",
        "serviceEndpoint": "http://mybrizo.org/api/v1/brizo/services/compute?pubKey=${"
                           "pubKey}&agreementId={agreementId}&algo={algo}&container={container}"
    },
    {
        "type": "Access",
        "purchaseEndpoint": "service",
        "serviceEndpoint": "consume",
        "serviceDefinitionId": "0",
        "templateId": "0x00000",
    }
]


def generate_sample_ddo():
    did = DID.did()
    assert did
    ddo = DDO(did)
    assert ddo
    private_key = ddo.add_signature()

    # add a proof signed with the private key
    ddo.add_proof(0, '0x00bd138abd70e2f00903268f3db08f2d25677c9e', private_key)

    metadata = json.loads(TEST_METADATA)
    ddo.add_service("Metadata", "http://myaquarius.org/api/v1/provider/assets/metadata/{did}",
                    values={'metadata': metadata})
    for test_service in TEST_SERVICES:
        if 'values' in test_service:
            values = test_service['values']
        else:
            values = test_service.copy()
            values.pop('type')
            values.pop('serviceEndpoint')

        ddo.add_service(test_service['type'], test_service['serviceEndpoint'], values=values)

    return ddo, private_key


@unit_test
def test_creating_ddo():
    did = DID.did()
    assert did
    ddo = DDO(did)
    assert ddo
    private_keys = []
    for public_key_store_type in public_key_store_types:
        private_keys.append(ddo.add_signature(public_key_store_type))

    assert len(private_keys) == len(public_key_store_types)
    ddo.add_service(TEST_SERVICE_TYPE, TEST_SERVICE_URL)

    assert len(ddo.public_keys) == len(public_key_store_types)
    assert len(ddo.authentications) == len(public_key_store_types)
    assert len(ddo.services) == 1

    ddo_text_no_proof = ddo.as_text()
    assert ddo_text_no_proof
    ddo_text_no_proof_hash = ddo.calculate_hash()

    # test getting public keys in the DDO record
    for index, private_key in enumerate(private_keys):
        assert ddo.get_public_key(index)
        signature_key_id = '{0}#keys={1}'.format(did, index + 1)
        assert ddo.get_public_key(signature_key_id)

    ddo_text_proof = ''
    ddo_text_proof_hash = ''
    # test validating static proofs
    for index, private_key in enumerate(private_keys):
        ddo.add_proof(index, '0x00bd138abd70e2f00903268f3db08f2d25677c9e', private_key)
        ddo_text_proof = ddo.as_text()
        # assert ddo.validate_proof()
        ddo_text_proof_hash = ddo.calculate_hash()

    ddo = DDO(json_text=ddo_text_proof)
    assert ddo.validate()
    assert ddo.is_proof_defined()
    # assert ddo.validate_proof()
    assert ddo.calculate_hash() == ddo_text_proof_hash

    ddo = DDO(json_text=ddo_text_no_proof)
    assert ddo.validate()
    # valid proof should be false since no static proof provided
    assert not ddo.is_proof_defined()
    # assert not ddo.validate_proof()
    assert ddo.calculate_hash() == ddo_text_no_proof_hash


@unit_test
def test_creating_ddo_embedded_public_key():
    did = DID.did()
    assert did
    ddo = DDO(did)
    assert ddo
    private_keys = []
    for public_key_store_type in public_key_store_types:
        private_keys.append(ddo.add_signature(public_key_store_type, is_embedded=True))

    assert len(private_keys) == len(public_key_store_types)
    ddo.add_service(TEST_SERVICE_TYPE, TEST_SERVICE_URL)
    # test validating static proofs
    for index, private_key in enumerate(private_keys):
        ddo.add_proof(index, '0x00bd138abd70e2f00903268f3db08f2d25677c9e', private_key)
        ddo_text_proof = ddo.as_text()
        assert ddo_text_proof
        # assert ddo.validate_proof()
        ddo_text_proof_hash = ddo.calculate_hash()
        assert ddo_text_proof_hash


@unit_test
def test_creating_did_using_ddo():
    # create an empty ddo
    ddo = DDO()
    assert ddo
    private_keys = []
    for public_key_store_type in public_key_store_types:
        private_keys.append(ddo.add_signature(public_key_store_type, is_embedded=True))
    assert len(private_keys) == len(public_key_store_types)
    ddo.add_service(TEST_SERVICE_TYPE, TEST_SERVICE_URL)
    # add a proof to the first public_key/authentication
    ddo.add_proof(0, '0x00bd138abd70e2f00903268f3db08f2d25677c9e', private_keys[0])
    ddo_text_proof = ddo.as_text()
    assert ddo_text_proof
    # assert ddo.validate_proof()


@unit_test
def test_load_ddo_json():
    # TODO: Fix
    sample_ddo_path = get_resource_path('ddo', 'ddo_sample1.json')
    assert sample_ddo_path.exists(), f'{sample_ddo_path} does not exist!'
    with open(sample_ddo_path) as f:
        sample_ddo_json_dict = json.load(f)

    sample_ddo_json_string = json.dumps(sample_ddo_json_dict)

    this_ddo = DDO(json_text=sample_ddo_json_string)
    service = this_ddo.get_service('Metadata')
    assert service
    assert service.type == 'Metadata'
    assert service.values['metadata']


@unit_test
def test_ddo_dict():
    sample_ddo_path = get_resource_path('ddo', 'ddo_sample1.json')
    assert sample_ddo_path.exists(), f'{sample_ddo_path} does not exist!'

    ddo1 = DDO(json_filename=sample_ddo_path)
    assert ddo1.is_valid
    assert len(ddo1.public_keys) == 3
    assert ddo1.did == 'did:op:3597a39818d598e5d60b83eabe29e337d37d9ed5af218b4af5e94df9f7d9783a'


@unit_test
def test_generate_test_ddo_files():
    for index in range(1, 3):
        ddo, private_key = generate_sample_ddo()

        json_output_filename = get_resource_path('ddo',
                                                 f'ddo_sample_generated_{index}.json')
        with open(json_output_filename, 'w') as fp:
            fp.write(ddo.as_text(is_pretty=True))

        private_output_filename = get_resource_path('ddo',
                                                    f'ddo_sample_generated_{index}_private_key.pem')
        with open(private_output_filename, 'w') as fp:
            fp.write(private_key.decode('utf-8'))


@unit_test
def test_find_service():
    ddo, pvk = generate_sample_ddo()
    service = ddo.find_service_by_id(0)
    assert service and service.type == 'Access', 'Failed to find service by integer id.'
    service = ddo.find_service_by_id('0')
    assert service and service.type == 'Access', 'Failed to find service by str(int) id.'

    service = ddo.find_service_by_id(1)
    assert service and service.type == 'Compute', 'Failed to find service by integer id.'
    service = ddo.find_service_by_id('1')
    assert service and service.type == 'Compute', 'Failed to find service by str(int) id.'

    service = ddo.find_service_by_id('Access')
    assert service and service.type == 'Access', 'Failed to find service by id using service type.'
    assert service.service_definition_id == '0', 'serviceDefinitionId not as expected.'

    service = ddo.find_service_by_id('Compute')
    assert service and service.type == 'Compute', 'Failed to find service by id using service type.'
    assert service.service_definition_id == '1', 'serviceDefinitionId not as expected.'
