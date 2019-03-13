"""
    Authentication Class
    To handle embedded public keys
"""

#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import json
import re

from .public_key_base import PublicKeyBase


class Authentication:
    """DDO Authentication"""

    def __init__(self, key_id, authentication_type):
        """Init an authentication based on it's key_id and authentication type.

        :param key_id:
        :param authentication_type:
        """
        self._public_key = None
        self._public_key_id = None
        if isinstance(key_id, PublicKeyBase):
            self._public_key = key_id
        else:
            self._public_key_id = key_id
        self._type = authentication_type

    def assign_did(self, did):
        """
        Assign a DID to the authentitacation, if the DID does not end with a `#.*`
        then add an automatic key value.

        :param did: DID, str
        """
        if self._public_key_id:
            if re.match('^#.*', self._public_key_id):
                self._public_key_id = did + self._public_key_id
        if self._public_key:
            self._public_key.assign_did(did)

    def get_type(self):
        """Get the authentication type."""
        return self._type

    def get_public_key_id(self):
        """Get the authentication key id used to validate this authentication."""
        if self._public_key_id:
            return self._public_key_id
        if self._public_key:
            return self._public_key.get_id()
        return None

    def get_public_key(self):
        """Get the authentication public key."""
        return self._public_key

    def as_text(self, is_pretty=False):
        """Return the authentication as a JSON text.

        :param is_pretty: If True return dictionary in a prettier way, bool
        :return: str
        """
        values = {
            'type': self._type
        }
        if self._public_key:
            values['publicKey'] = self._public_key.as_text(is_pretty)
        elif self._public_key_id:
            values['publicKey'] = self._public_key_id

        if is_pretty:
            return json.dumps(values, indent=4, separators=(',', ': '))

        return json.dumps(values)

    def as_dictionary(self):
        """Return the authentication as a dictionary.

        :return: dict
        """
        values = {
            'type': self._type
        }
        if self._public_key:
            values['publicKey'] = self._public_key.as_dictionary()
        elif self._public_key_id:
            values['publicKey'] = self._public_key_id

        return values

    def is_valid(self):
        """Return true if this authentication has valid structure.

        :return: bool
        """
        return self.get_public_key_id() is not None and self._type is not None

    def is_public_key(self):
        """Return true if this authentication has an embedded public key.

        :return: bool
        """
        return self._public_key is not None

    def is_key_id(self, key_id):
        """Return True if the `key_id` is the same as this key_id.

        :param key_id: str
        :return: bool
        """
        if self.get_public_key_id() and self.get_public_key_id() == key_id:
            return True
        return False
