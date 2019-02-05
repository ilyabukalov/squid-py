from squid_py.accounts.account import Account
from squid_py.secret_store.secret_store import SecretStore


class SecretStoreProvider(object):
    """Provides the SecretStore instance."""
    _secret_store_class = SecretStore

    @staticmethod
    def get_args_from_config(config):
        return (
            config.secret_store_url,
            config.parity_url,
            Account(config.parity_address, config.parity_password)
        )

    @staticmethod
    def get_secret_store(secret_store_url, keeper_url, account):
        """ Get an SecretStore instance."""
        return SecretStoreProvider._secret_store_class(secret_store_url, keeper_url, account)

    @staticmethod
    def set_secret_store_class(secret_store_class):
        """
         Set a SecretStore class

        :param secret_store_class: SecretStore class
        :return:  New SecretStore instance.
        """
        SecretStoreProvider._secret_store_class = secret_store_class
