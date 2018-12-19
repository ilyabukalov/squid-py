"""
Class to setup the logging.
"""
import os
import logging
import logging.config
import yaml
import coloredlogs


def setup_logging(default_path='logging.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    Logging Setup
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as file:
            try:
                config = yaml.safe_load(file.read())
                logging.config.dictConfig(config)
                coloredlogs.install()
                logging.info("Logging configuration loaded from file: %s" % path)
            except Exception as ex:
                print(ex)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
                coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=default_level)
        print('Using default logging settings.')
