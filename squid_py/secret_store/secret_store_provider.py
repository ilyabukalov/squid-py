from squid_py.secret_store.secret_store import SecretStore


class SecretStoreProvider(object):
    _secret_store = None

    @staticmethod
    def get_secret_store():
        if not SecretStoreProvider._secret_store:
            SecretStoreProvider._secret_store = SecretStore()
        return SecretStoreProvider._secret_store

    @staticmethod
    def set_secret_store(secret_store):
        SecretStoreProvider._secret_store = secret_store
