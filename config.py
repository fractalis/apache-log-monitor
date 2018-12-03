import yaml


class Config(object):

    def __init__(self, config_file):
        f = open(config_file)
        lines = f.readlines()
        self._config = yaml.load("\n".join(lines))

    def getConfigValue(self, config_value):
        if config_value in self._config.keys():
            return self._config[config_value]
        else:
            return None
