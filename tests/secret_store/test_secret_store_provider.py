#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from ocean_keeper.account import Account

from squid_py.secret_store import SecretStoreProvider


class SSMock:
    def __init__(self, ss_url, keeper_url, account):
        self.ss_url = ss_url
        self.keeper_url = keeper_url
        self.account = account


def test_secret_store_provider():
    account = Account('0x00000000000000000', 'psw', encrypted_key='0x01010101101')
    SecretStoreProvider.set_secret_store_class(SSMock)
    ss = SecretStoreProvider.get_secret_store('ss/url', 'keeper/url', account)
    sss = SecretStoreProvider.get_secret_store('ss/url', 'keeper/url', account)
    assert ss != sss, ''
    assert isinstance(ss, SSMock)
    assert ss.ss_url == 'ss/url', ''
    assert ss.keeper_url == 'keeper/url', ''
    assert ss.account == account, ''
