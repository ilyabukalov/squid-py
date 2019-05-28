#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import os
from time import sleep

from squid_py.aquarius import AquariusProvider
from examples import ExampleConfig
from squid_py import ConfigProvider, Metadata, Ocean

if 'TEST_NILE' in os.environ and os.environ['TEST_NILE'] == '1':
    ASYNC_DELAY = 5  # seconds
else:
    ASYNC_DELAY = 1  # seconds


def update_asset():
    ConfigProvider.set_config(ExampleConfig.get_config())
    ocn = Ocean()
    account = ([acc for acc in ocn.accounts.list() if acc.password] or ocn.accounts.list())[0]
    did = ["did:op:6562dcdc05864a67ab7c8264ab5d3e5261d8bf076173430ebf1d3a18a2679132",
"did:op:e4e43272d62345b6ac3681ce3c05f5d83fcaece90f8b487a96c603dbb54b57b4",
"did:op:bdcf193da0744c1f8cdcfe4bd640a1884ab8b34d5d944ef1b9a5f15e92f229f5",
"did:op:7112cd948b6844b98063fb1e9006958eeeb6fa2814674fabae85fca30dda08e9",
"did:op:23241f0ee30946d1ba63f934a268820819cd80146a27467da72db8c41ef71d9e",
"did:op:0182b059a77c47d4ac7d347ff90dfcbd5e318cc8fb474d80b2b9fb4f440a7e0c",
"did:op:d3e2b02a20ff4e30bf2d696a85b14c91fded2b66f5c84c18b4d2075273b7b853",
"did:op:4cd225d1c9f54741a5c916646a6fa88ed679c75c81d047dcac47c701a7dc7ba0",
"did:op:6683b8252fcc47148f47147cd982d45f72844c6f18db43aaba84ac91137c147d",
"did:op:e4171a9cdfc14541819ff7ed97d30a65b94f1dead03849e49dc178e2333990a6",
"did:op:2eec8593c3bd4dcbb95c83766ded83609622161baf894ef0887dd2ee46ffbc09",
"did:op:5152c9e4767f43fb8067036685bc35fdce8f2887215e4903888da22956ec18e2",
"did:op:f557c303cb674898a8b5e611f2ec4e057a281febfb374ae3be5982e978ef1ee9",
"did:op:f24f90c202994a3f8f8a9037d54ac300fb032068115d41f4ad7c83b7f30d3f83",
"did:op:c4a41ccb88c2496ba4e517abf2c0f3a6a33a19d691c44efcae31fbe9928ac15e",
"did:op:f946b795f172497896771f0d3af40ed669ee647c3804456f9d7b3e3b290c70fe",
"did:op:8492e170e94d4fecaff7560d0e0998bad058ca9af7ff4be7af82716c8c1befab",
"did:op:74bc00330b664cc6a4f0e154543a047cfdec1b1972884179a87a923f54a0ae52"]
    for i in did:
        ddo = ocn.assets.resolve(i)
        ddo.metadata['base']['tags']=['ai-for-good']
    # # ddo.metadata['curation']['isListed'] = False
        AquariusProvider.get_aquarius("https://aquarius.marketplace.dev-ocean.com/").update_asset_ddo(
                i, ddo)


    # for result in AquariusProvider.get_aquarius("https://aquarius.marketplace.dev-ocean.com/").query_search(search_query={"query": {"price": [1,1000000000]}})['results']:
    #     did = result['id']
    #     ddo = ocn.assets.resolve(did)
    #     ddo.metadata['curation']['isListed'] = False
    #     AquariusProvider.get_aquarius("https://aquarius.marketplace.dev-ocean.com/").update_asset_ddo(
    #         did, ddo)

if __name__ == '__main__':
    update_asset()