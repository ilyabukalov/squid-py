"""DID Lib to do DID's and DDO's."""
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

import hashlib
import json
import logging
from base64 import b64decode, b64encode
from datetime import datetime

from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5
from eth_utils import add_0x_prefix

from squid_py.agreements.service_types import ServiceTypes
from squid_py.ddo.public_key_hex import PublicKeyHex
from squid_py.did import did_to_id
from squid_py.keeper.web3_provider import Web3Provider
from .authentication import Authentication
from .constants import DID_DDO_CONTEXT_URL, KEY_PAIR_MODULUS_BIT, PROOF_TYPE
from .public_key_base import PUBLIC_KEY_STORE_TYPE_PEM, PublicKeyBase
from .public_key_rsa import AUTHENTICATION_TYPE_RSA, PUBLIC_KEY_TYPE_RSA, PublicKeyRSA
from .service import Service

logger = logging.getLogger('ddo')


class DDO:
    """DDO class to create, import, export, validate DDO objects."""

    def __init__(self, did='', json_text=None, json_filename=None, created=None, dictionary=None):
        """Clear the DDO data values."""
        self._did = did
        self._public_keys = []
        self._authentications = []
        self._services = []
        self._proof = None
        self._created = None

        if created:
            self._created = created
        else:
            self._created = DDO._get_timestamp()

        if not json_text and json_filename:
            with open(json_filename, 'r') as file_handle:
                json_text = file_handle.read()

        if json_text:
            self._read_dict(json.loads(json_text))
        elif dictionary:
            self._read_dict(dictionary)

    @property
    def did(self):
        """ Get the DID."""
        return self._did

    @property
    def asset_id(self):
        """The asset id part of the DID"""
        return add_0x_prefix(did_to_id(self._did))

    @property
    def services(self):
        """Get the list of services."""
        return self._services[:]

    @property
    def proof(self):
        """Get the static proof, or None."""
        return self._proof

    @property
    def metadata(self):
        """Get the metadata service."""
        metadata_service = self.find_service_by_type(ServiceTypes.METADATA)
        return metadata_service.values['metadata']

    def add_public_key(self, public_key):
        """
        Add a public key object to the list of public keys.

        :param public_key: Public key, PublicKeyHex
        """
        logger.debug(f'Adding public key {public_key}')
        self._public_keys.append(public_key)

    def add_authentication(self, key_id, authentication_type=None):
        """
        Add a authentication public key id and type to the list of authentications.

        :param key_id: Key id, Authentication
        :param authentication_type: Authentication type, str
        """
        if isinstance(key_id, Authentication):
            # adding an authentication object
            authentication = key_id
        elif isinstance(key_id, PublicKeyBase):
            public_key = key_id
            # this is going to be a embedded public key
            authentication = Authentication(public_key, public_key.get_authentication_type())
        else:
            # with key_id as a string, we also need to provide the authentication type
            if authentication_type is None:
                raise ValueError
            authentication = Authentication(key_id, authentication_type)

        logger.debug(f'Adding authentication {authentication}')
        self._authentications.append(authentication)

    def add_signature(self, public_key_store_type=PUBLIC_KEY_STORE_TYPE_PEM, is_embedded=False):
        """
        Add signature.

        Add a signature with a public key and authentication entry for validating this DDO
        returns the private key as part of the private/public key pair.

        :param public_key_store_type: Public key store type, str
        :param is_embedded: bool
        :return Private key pem, str
        """

        key_pair = RSA.generate(KEY_PAIR_MODULUS_BIT, e=65537)
        public_key_raw = key_pair.publickey()
        private_key_pem = key_pair.exportKey("PEM")

        # find the current public key count
        next_index = self._get_public_key_count() + 1
        key_id = f'{self._did}#keys={next_index}'

        public_key = PublicKeyRSA(key_id, owner=key_id)

        public_key.set_encode_key_value(public_key_raw, public_key_store_type)

        if is_embedded:
            # also add the authentication key as embedded key with the authentication
            self.add_authentication(public_key)
        else:
            # add the public key to the DDO list of public keys
            self.add_public_key(public_key)

            # add the public key id and type for this key to the authentication
            self.add_authentication(public_key.get_id(), public_key.get_authentication_type())

        logger.debug('Adding signature to the ddo object.')
        return private_key_pem

    def add_service(self, service_type, service_endpoint=None, values=None):
        """
        Add a service to the list of services on the DDO.

        :param service_type: Service
        :param service_endpoint: Service endpoint, str
        :param values: Python dict with serviceDefinitionId, templateId, serviceAgreementContract,
        list of conditions and purchase endpoint.
        """
        if isinstance(service_type, Service):
            service = service_type
        else:
            service = Service(service_endpoint, service_type, values, did=self._did)
        logger.debug(f'Adding service with service type {service_type} with did {self._did}')
        self._services.append(service)

    def as_text(self, is_proof=True, is_pretty=False):
        """Return the DDO as a JSON text.

        :param if is_proof: if False then do not include the 'proof' element.
        :param is_pretty: If True return dictionary in a prettier way, bool
        :return: str
        """
        data = self.as_dictionary(is_proof)
        if is_pretty:
            return json.dumps(data, indent=2, separators=(',', ': '))

        return json.dumps(data)

    def as_dictionary(self, is_proof=True):
        """
        Return the DDO as a JSON dict.

        :param if is_proof: if False then do not include the 'proof' element.
        :return: dict
        """
        if self._created is None:
            self._created = DDO._get_timestamp()

        data = {
            '@context': DID_DDO_CONTEXT_URL,
            'id': self._did,
            'created': self._created,
        }
        if self._public_keys:
            values = []
            for public_key in self._public_keys:
                values.append(public_key.as_dictionary())
            data['publicKey'] = values
        if self._authentications:
            values = []
            for authentication in self._authentications:
                values.append(authentication.as_dictionary())
            data['authentication'] = values
        if self._services:
            values = []
            for service in self._services:
                values.append(service.as_dictionary())
            data['service'] = values
        if self._proof and is_proof:
            data['proof'] = self._proof

        return data

    def _read_dict(self, dictionary):
        """Import a JSON dict into this DDO."""
        values = dictionary
        self._did = values['id']
        self._created = values.get('created', None)
        if 'publicKey' in values:
            self._public_keys = []
            for value in values['publicKey']:
                if isinstance(value, str):
                    value = json.loads(value)
                self._public_keys.append(DDO.create_public_key_from_json(value))
        if 'authentication' in values:
            self._authentications = []
            for value in values['authentication']:
                if isinstance(value, str):
                    value = json.loads(value)
                self._authentications.append(DDO.create_authentication_from_json(value))
        if 'service' in values:
            self._services = []
            for value in values['service']:
                if isinstance(value, str):
                    value = json.loads(value)
                service = Service.from_json(value)
                service.set_did(self._did)
                self._services.append(service)
        if 'proof' in values:
            self._proof = values['proof']

    def add_proof(self, authorization_index, publisher_address, private_key=None,
                  signature_text=None):
        """Add a proof to the DDO, based on the public_key id/index and signed with the private key
        add a static proof to the DDO, based on one of the public keys."""

        # find the key using an index, or key name
        if isinstance(authorization_index, dict):
            self._proof = authorization_index
            return

        if private_key is None:
            raise ValueError

        authentication = self._authentications[authorization_index]
        if not authentication:
            raise IndexError
        if authentication.is_public_key():
            sign_key = authentication.get_public_key()
        else:
            sign_key = self.get_public_key(authentication.get_public_key_id())

        if sign_key is None:
            raise IndexError

        # get the signature text if not provided

        if signature_text is None:
            hash_text_list = self._hash_text_list()
            signature_text = "".join(hash_text_list)

        # just incase clear out the current static proof property
        self._proof = None

        signature = DDO.sign_text(signature_text, private_key, sign_key.get_type())

        self._proof = {
            'type': PROOF_TYPE,
            'created': DDO._get_timestamp(),
            'creator': publisher_address,
            'signatureValue': b64encode(signature).decode('utf-8'),
        }

    def validate_proof(self, signature_text=None):
        """Validate the static proof created with this DDO, return True if valid
        if no static proof exists then return False."""

        if not signature_text:
            hash_text_list = self._hash_text_list()
            signature_text = "".join(hash_text_list)
        if self._proof is None:
            return False
        if not isinstance(self._proof, dict):
            return False

        if 'creator' in self._proof and 'signatureValue' in self._proof:
            signature = b64decode(self._proof['signatureValue'])
            return self.validate_from_key(self._proof['creator'], signature_text, signature)
        return False

    def is_proof_defined(self):
        """Return true if a static proof exists in this DDO."""
        return self._proof is not None

    def validate_from_key(self, key_id, signature_text, signature_value):
        """Validate a signature based on a given public_key key_id/name."""

        public_key = self.get_public_key(key_id, True)
        if public_key is None:
            return False

        key_value = public_key.get_decode_value()
        if key_value is None:
            return False

        authentication = self._get_authentication_from_public_key_id(public_key.get_id())
        if authentication is None:
            return False

        # if public_key.get_store_type() != PUBLIC_KEY_STORE_TYPE_PEM:
        # key_value = key_value.decode()

        return DDO.validate_signature(signature_text, key_value, signature_value,
                                      authentication.get_type())

    def get_public_key(self, key_id, is_search_embedded=False):
        """Key_id can be a string, or int. If int then the index in the list of keys."""
        if isinstance(key_id, int):
            return self._public_keys[key_id]

        for item in self._public_keys:
            if item.get_id() == key_id:
                return item

        if is_search_embedded:
            for authentication in self._authentications:
                if authentication.get_public_key_id() == key_id:
                    return authentication.get_public_key()
        return None

    def _get_public_key_count(self):
        """Return the count of public keys in the list and embedded."""
        index = len(self._public_keys)
        for authentication in self._authentications:
            if authentication.is_public_key():
                index += 1
        return index

    def _get_authentication_from_public_key_id(self, key_id):
        """Return the authentication based on it's id."""
        for authentication in self._authentications:
            if authentication.is_key_id(key_id):
                return authentication
        return None

    def get_service(self, service_type=None):
        """Return a service using."""
        for service in self._services:
            if service.type == service_type and service_type:
                return service
        return None

    def find_service_by_id(self, service_id):
        """
        Get service for a given service_id.

        :param service_id: Service id, str
        :return: Service
        """
        service_id_key = 'serviceDefinitionId'
        service_id = str(service_id)
        for service in self._services:
            if service_id_key in service.values and str(
                    service.values[service_id_key]) == service_id:
                return service

        try:
            # If service_id is int or can be converted to int then we couldn't find it
            int(service_id)
            return None
        except ValueError:
            pass

        # try to find by type
        return self.find_service_by_type(service_id)

    def find_service_by_type(self, service_type):
        """
        Get service for a given service type.

        :param service_type: Service type, ServiceType
        :return: Service
        """
        for service in self._services:
            if service_type == service.type:
                return service
        return None

    def validate(self):
        """Validate the ddo data structure."""
        if self._public_keys and self._authentications:
            for authentication in self._authentications:
                if not authentication.is_valid():
                    return False
                if authentication.is_public_key():
                    public_key = authentication.get_public_key()
                else:
                    key_id = authentication.get_public_key_id()
                    public_key = self.get_public_key(key_id)
                if not public_key.is_valid():
                    return False
        if self._services:
            for service in self._services:
                if not service.is_valid():
                    return False

        # validate if proof defined in this DDO
        if self.is_proof_defined:
            if not self.validate_proof:
                return False
        return True

    def _hash_text_list(self):
        """Return a list of all of the hash text."""
        hash_text = []
        if self._created:
            hash_text.append(self._created)

        if self._public_keys:
            for public_key in self._public_keys:
                if public_key.get_type():
                    hash_text.append(public_key.get_type())
                if public_key.get_value():
                    hash_text.append(public_key.get_value())

        if self._authentications:
            for authentication in self._authentications:
                if authentication.is_public_key():
                    public_key = authentication.get_public_key()
                    if public_key.get_type():
                        hash_text.append(public_key.get_type())
                    if public_key.get_value():
                        hash_text.append(public_key.get_value())

        if self._services:
            for service in self._services:
                hash_text.append(service.type)
                hash_text.extend(service.endpoints)

        # if no data can be found to hash then raise an error
        if not hash_text:
            raise ValueError
        return hash_text

    def calculate_hash(self):
        """Return a sha3 hash of important bits of the DDO, excluding any DID portion,
        as this hash can be used to generate the DID."""
        hash_text_list = self._hash_text_list()
        return Web3Provider.get_web3().sha3(text="".join(hash_text_list))

    def _is_did_assigend(self):
        """Return true if a DID is assigned to this DDO."""
        return self._did != '' and self._did is not None

    @property
    def public_keys(self):
        """Get the list of public keys."""
        return self._public_keys[:]

    @property
    def authentications(self):
        """Get the list authentication records."""
        return self._authentications[:]

    @property
    def is_valid(self):
        """Return True if this DDO is valid."""
        return self.validate()

    @staticmethod
    def sign_text(text, private_key, sign_type=PUBLIC_KEY_TYPE_RSA):
        """Sign some text using the private key provided."""
        if sign_type == PUBLIC_KEY_TYPE_RSA:
            signer = PKCS1_v1_5.new(RSA.import_key(private_key))
            text_hash = SHA256.new(text.encode('utf-8'))
            signed_text = signer.sign(text_hash)
            return signed_text

        raise NotImplementedError

    @staticmethod
    def validate_signature(text, key, signature, sign_type=AUTHENTICATION_TYPE_RSA):
        """Validate a signature based on some text, public key and signature."""
        result = False
        try:
            if sign_type == AUTHENTICATION_TYPE_RSA:
                rsa_key = RSA.import_key(key)
                verifier = PKCS1_v1_5.new(rsa_key)
                if verifier:
                    text_hash = SHA256.new(text.encode('utf-8'))
                    result = verifier.verify(text_hash, signature)
            else:
                raise NotImplementedError
        except (ValueError, TypeError):
            result = False

        return result

    @staticmethod
    def create_public_key_from_json(values):
        """Create a public key object based on the values from the JSON record."""
        # currently we only support RSA public keys
        _id = values.get('id')
        if not _id:
            # Make it more forgiving for now.
            _id = ''
            # raise ValueError('publicKey definition is missing the "id" value.')

        if values.get('type') == PUBLIC_KEY_TYPE_RSA:
            public_key = PublicKeyRSA(_id, owner=values.get('owner'))
        else:
            public_key = PublicKeyHex(_id, owner=values.get('owner'))

        public_key.set_key_value(values)
        return public_key

    @staticmethod
    def create_authentication_from_json(values):
        """Create authentitaciton object from a JSON string."""
        key_id = values.get('publicKey')
        authentication_type = values.get('type')
        if not key_id:
            raise ValueError(
                f'Invalid authentication definition, "publicKey" is missing: {values}')
        if isinstance(key_id, dict):
            public_key = DDO.create_public_key_from_json(key_id)
            authentication = Authentication(public_key, public_key.get_authentication_type())
        else:
            authentication = Authentication(key_id, authentication_type)

        return authentication

    @staticmethod
    def _get_timestamp():
        """Return the current system timestamp."""
        return f'{datetime.utcnow().replace(microsecond=0).isoformat()}Z'

    @staticmethod
    def generate_checksum(did, metadata):
        files_checksum = ''
        for file in metadata['base']['files']:
            if 'checksum' in file:
                files_checksum = files_checksum + file['checksum']
        return hashlib.sha3_256((files_checksum +
                                 metadata['base']['name'] +
                                 metadata['base']['author'] +
                                 metadata['base']['license'] +
                                 did).encode('UTF-8')).hexdigest()
