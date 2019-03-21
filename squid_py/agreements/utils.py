"""Agreements module."""

#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import json
import os

from squid_py.agreements.service_types import ServiceTypes
from squid_py.ddo.authentication import Authentication
from squid_py.ddo.public_key_hex import AUTHENTICATION_TYPE_HEX, PUBLIC_KEY_TYPE_HEX, PublicKeyHex
from squid_py.utils.utilities import get_public_key_from_address


def get_sla_template_path(service_type=ServiceTypes.ASSET_ACCESS):
    """
    Get the template for a ServiceType.

    :param service_type: ServiceTypes
    :return: Path of the template, str
    """
    if service_type == ServiceTypes.ASSET_ACCESS:
        name = 'access_sla_template.json'
    elif service_type == ServiceTypes.CLOUD_COMPUTE:
        name = 'compute_sla_template.json'
    elif service_type == ServiceTypes.FITCHAIN_COMPUTE:
        name = 'fitchain_sla_template.json'
    else:
        raise ValueError(f'Invalid/unsupported service agreement type {service_type}')

    return os.path.join(os.path.sep, *os.path.realpath(__file__).split(os.path.sep)[1:-1], name)


def get_sla_template_dict(path):
    """
    Return a dictionary with the template.

    :param path: Template path, str
    :return: dict
    """
    with open(path) as template_file:
        return json.load(template_file)


def make_public_key_and_authentication(did, publisher_account, web3):
    """Create a public key and authentication sections to include in a DDO (DID document).
    The public key is derived from the ethereum address by signing an arbitrary message
    then using ec recover to extract the public key.
    Alternatively, the public key can be generated from a private key if provided by the publisher.

    :param did: DID, str
    :param publisher_account: Account instance of the publisher
    :param web3: Web3 instance
    :return: Tuple(str, str)
    """
    # set public key
    public_key_value = get_public_key_from_address(web3, publisher_account).to_hex()
    pub_key = PublicKeyHex('keys-1', **{'value': public_key_value, 'owner': publisher_account.address,
                                        'type': PUBLIC_KEY_TYPE_HEX})
    pub_key.assign_did(did)
    # set authentication
    auth = Authentication(pub_key, AUTHENTICATION_TYPE_HEX)
    return pub_key, auth
