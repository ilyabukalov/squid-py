"""DID Lib to do DID's and DDO's."""

#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

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
from squid_py.ddo.public_key_base import PublicKeyBase
from squid_py.ddo.public_key_hex import PublicKeyHex
from squid_py.did import did_to_id
from .constants import DID_DDO_CONTEXT_URL, KEY_PAIR_MODULUS_BIT, PROOF_TYPE
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

    def add_public_key(self, did, public_key):
        """
        Add a public key object to the list of public keys.

        :param public_key: Public key, PublicKeyHex
        """
        logger.debug(f'Adding public key {public_key} to the did {did}')
        self._public_keys.append(
            PublicKeyBase(did, **{"owner": public_key, "type": "EthereumECDSAKey"}))

    def add_authentication(self, public_key, authentication_type=None):
        """
        Add a authentication public key id and type to the list of authentications.

        :param key_id: Key id, Authentication
        :param authentication_type: Authentication type, str
        """
        authentication = {}
        if public_key:
            authentication = {'type': authentication_type, 'publicKey': public_key}
        logger.debug(f'Adding authentication {authentication}')
        self._authentications.append(authentication)

    @staticmethod
    def get_private_key():
        """
        Get your private key.

        Add a signature with a public key and authentication entry for validating this DDO
        returns the private key as part of the private/public key pair.

        :return Private key pem, str
        """
        key_pair = RSA.generate(KEY_PAIR_MODULUS_BIT, e=65537)
        private_key_pem = key_pair.exportKey("PEM")
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
                values.append(authentication)
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

    def add_proof(self, text, publisher_address, private_key=None):
        """Add a proof to the DDO, based on the public_key id/index and signed with the private key
        add a static proof to the DDO, based on one of the public keys."""

        # just incase clear out the current static proof property
        self._proof = None

        signature = DDO.sign_text(text, private_key, 'RsaSignatureAuthentication2018')

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

    @property
    def public_keys(self):
        """Get the list of public keys."""
        return self._public_keys[:]

    @property
    def authentications(self):
        """Get the list authentication records."""
        return self._authentications[:]

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
            public_key = PublicKeyBase(_id, owner=values.get('owner'), type='EthereumECDSAKey')

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

        authentication = {'type': authentication_type, 'publicKey': key_id}

        return authentication

    @staticmethod
    def _get_timestamp():
        """Return the current system timestamp."""
        return f'{datetime.utcnow().replace(microsecond=0).isoformat()}Z'

    @staticmethod
    def generate_checksum(did, metadata):
        """
        Generation of the hash for integrity checksum.

        :param did: DID, str
        :param metadata: conforming to the Metadata accepted by Ocean Protocol, dict
        :return: hex str
        """
        files_checksum = ''
        for file in metadata['base']['files']:
            if 'checksum' in file:
                files_checksum = files_checksum + file['checksum']
        return hashlib.sha3_256((files_checksum +
                                 metadata['base']['name'] +
                                 metadata['base']['author'] +
                                 metadata['base']['license'] +
                                 did).encode('UTF-8')).hexdigest()
