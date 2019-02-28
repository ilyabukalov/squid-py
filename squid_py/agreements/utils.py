import json
import os

from squid_py.agreements.service_types import ServiceTypes
from squid_py.ddo.authentication import Authentication
from squid_py.ddo.public_key_hex import AUTHENTICATION_TYPE_HEX, PUBLIC_KEY_TYPE_HEX, PublicKeyHex
from squid_py.utils.utilities import get_public_key_from_address


def get_sla_template_path(service_type=ServiceTypes.ASSET_ACCESS):
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
    with open(path) as template_file:
        return json.load(template_file)


# def get_conditions_data_from_keeper_contracts(conditions, template_id):
#     """Helper function to generate conditions data that is typically used together in a
#     service agreement.
#
#     :param conditions: list of ServiceAgreementCondition instances
#     :param template_id:
#     :return:
#     """
#     names = {cond.contract_name for cond in conditions}
#     name_to_contract = {
#         name: ContractHandler.get(name)
#         for name in names
#     }
#     contract_addresses = [
#         Web3Provider.get_web3().toChecksumAddress(name_to_contract[cond.contract_name].address)
#         for cond in conditions
#     ]
#     fingerprints = [
#         hexstr_to_bytes(Web3Provider.get_web3(), get_fingerprint_by_name(
#             name_to_contract[cond.contract_name].abi,
#             cond.function_name
#         ))
#         for i, cond in enumerate(conditions)
#     ]
#     fulfillment_indices = [i for i, cond in enumerate(conditions) if cond.is_terminal]
#     return contract_addresses, fingerprints, fulfillment_indices


def make_public_key_and_authentication(did, publisher_address, web3):
    """Create a public key and authentication sections to include in a DDO (DID document).
    The public key is derived from the ethereum address by signing an arbitrary message
    then using ec recover to extract the public key.
    Alternatively, the public key can be generated from a private key if provided by the publisher.

    :param did:
    :param publisher_address:
    :param web3:
    :return:
    """
    # set public key
    public_key_value = get_public_key_from_address(web3, publisher_address).to_hex()
    pub_key = PublicKeyHex('keys-1', **{'value': public_key_value, 'owner': publisher_address,
                                        'type': PUBLIC_KEY_TYPE_HEX})
    pub_key.assign_did(did)
    # set authentication
    auth = Authentication(pub_key, AUTHENTICATION_TYPE_HEX)
    return pub_key, auth
