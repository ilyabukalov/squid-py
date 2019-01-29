"""Keeper module to call keeper-contracts."""

import json
import os
from json import JSONDecodeError

from squid_py.keeper.web3_provider import Web3Provider


def get_contract_abi_by_address(contract_path, address):
    """

    :param contract_path:
    :param address:
    :return:
    """
    contract_tree = os.walk(contract_path)
    address = address.lower()
    while True:
        dirname, _, files = next(contract_tree)
        for entry in files:
            with open(os.path.join(dirname, entry)) as f:
                try:
                    definition = json.loads(f.read())
                except (JSONDecodeError, TypeError):
                    continue

                if address != definition['address'].lower():
                    continue

                return definition['abi']


def get_event_def_from_abi(abi, event_name):
    """

    :param abi:
    :param event_name:
    :return:
    """
    for item in abi:
        if item.get('type') == 'event' and item.get('name') == event_name:
            return item

    raise ValueError(f'event {event_name} not found in the given ABI')


def compute_function_fingerprint(function_abi):
    web3 = Web3Provider.get_web3()
    function_args = [_input['type'] for _input in function_abi['inputs']]
    args_str = ','.join(function_args)
    signature = web3.sha3(text=f'{function_abi["name"]}({args_str})').hex()[:10]
    return signature


def get_fingerprint_by_name(abi, name):
    """

    :param abi:
    :param name:
    :return:
    """
    for item in abi:
        if item.get('name') == name:
            fingerprint = item.get('signature')
            if not fingerprint:
                fingerprint = compute_function_fingerprint(item)

            return fingerprint

    raise ValueError(f'{name} not found in the given ABI')


def get_fingerprint_bytes_by_name(web3, abi, name):
    """

    :param web3:
    :param abi:
    :param name:
    :return:
    """
    return hexstr_to_bytes(web3, get_fingerprint_by_name(abi, name))


def hexstr_to_bytes(web3, hexstr):
    """

    :param web3:
    :param hexstr:
    :return:
    """
    return web3.toBytes(int(hexstr, 16))


def generate_multi_value_hash(types, values):
    """
    Return the hash of the given list of values.
    This is equivalent to packing and hashing values in a solidity smart contract
    hence the use of `soliditySha3`.

    :param types: list of solidity types expressed as strings
    :param values: list of values matching the `types` list
    :return: bytes
    """
    assert len(types) == len(values)
    return Web3Provider.get_web3().soliditySha3(
        types,
        values
    )
