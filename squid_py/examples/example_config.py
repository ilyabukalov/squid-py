from squid_py import Config


class ExampleConfig:
    config_dict = {
        "keeper-contracts": {
            "keeper.url": "http://localhost:8545",
            "keeper.path": "artifacts",
            "secret_store.url": "http://localhost:12001",
            "parity.url": "http://localhost:8545",
            "parity.address": "0x00bd138abd70e2f00903268f3db08f2d25677c9e",
            "parity.password": "node0",
            "parity.address1": "0x068ed00cf0441e4829d9784fcbe7b9e26d4bd8d0",
            "parity.password1": "secret"
        },
        "resources": {
            "aquarius.url": "http://172.15.0.15:5000",
            "brizo.url": "http://localhost:8030",
            "storage.path": "squid_py.db",
            "downloads.path": "consume-downloads"
        }
    }

    @staticmethod
    def get_config():
        return Config(options_dict=ExampleConfig.config_dict)
