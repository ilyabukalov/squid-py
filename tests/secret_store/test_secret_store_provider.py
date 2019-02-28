from squid_py import Account
from squid_py.secret_store import SecretStoreProvider
from squid_py.secret_store.secret_store import SecretStore


class SSMock:
    def __init__(self, ss_url, keeper_url, account):
        self.ss_url = ss_url
        self.keeper_url = keeper_url
        self.account = account


def test_secret_store_provider():
    account = Account('0x00000000000000000', 'psw')
    ss = SecretStoreProvider.get_secret_store('localhost:12000', 'localhost:8545', account)
    assert isinstance(ss, SecretStore), ''
    sss = SecretStoreProvider.get_secret_store('localhost:12000', 'localhost:8545', account)
    assert ss != sss, ''
    assert ss._secret_store_url == 'localhost:12000', ''
    assert ss._parity_node_url == 'localhost:8545', ''
    assert ss._account == account, ''

    SecretStoreProvider.set_secret_store_class(SSMock)
    ss = SecretStoreProvider.get_secret_store('ss/url', 'keeper/url', account)
    sss = SecretStoreProvider.get_secret_store('ss/url', 'keeper/url', account)
    assert ss != sss, ''
    assert isinstance(ss, SSMock)
    assert ss.ss_url == 'ss/url', ''
    assert ss.keeper_url == 'keeper/url', ''
    assert ss.account == account, ''
