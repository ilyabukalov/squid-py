from squid_py.secret_store.secret_store import SecretStore


class SecretStoreProvider(object):
    """Provides the SecretStore instance."""
    _secret_store = None

    @staticmethod
    def get_secret_store():
        """ Get an SecretStore instance."""
        if not SecretStoreProvider._secret_store:
            SecretStoreProvider._secret_store = SecretStore()
        return SecretStoreProvider._secret_store

    @staticmethod
    def set_secret_store(secret_store):
        """
         Set an SecretStore instance.

        :param secret_store: SecretStore
        :return:  New SecretStore instance.
        """
        SecretStoreProvider._secret_store = secret_store
