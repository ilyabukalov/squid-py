
class ConfigProvider:
    _config = None

    @staticmethod
    def get_config():
        assert ConfigProvider._config, 'set_config first.'
        return ConfigProvider._config

    @staticmethod
    def set_config(config):
        ConfigProvider._config = config
