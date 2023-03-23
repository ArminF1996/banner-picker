import configparser
import os
import logging
from distutils.util import strtobool


class EnvInterpolation(configparser.BasicInterpolation):
    """Interpolation which expands environment variables in values."""

    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)
        envvar = os.getenv(option)
        if envvar:
            return process_string_var(envvar)
        else:
            return value


def process_string_var(value):
    if value == "":
        return None

    if value.isdigit():
        return int(value)
    elif value.replace(".", "", 1).isdigit():
        return float(value)

    try:
        return bool(strtobool(value))
    except ValueError:
        return value


class Config(object):
    def __setattr__(self, name, value):
        self.__dict__[name] = value


def get_config(config_path):
    config_ini = configparser.ConfigParser(interpolation=EnvInterpolation())
    config_ini.optionxform = str  # Makes the key value case-insensitive
    config_ini.read(config_path)
    config = Config()
    for k, v in config_ini.items("extra"):
        setattr(config, k, process_string_var(v))
    logging.basicConfig(level=config.LOG_LEVEL, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    logger.info("Configs for api module: {}".format(config.__dict__))

    return config
