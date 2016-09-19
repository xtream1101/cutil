import itertools
import configparser


class Config:
    def __init__(self, conf_file=None):
        self._config = configparser.ConfigParser()
        self._config.optionxform = str  # Keep case of keys

        self.config_values = self.remove_quotes(self.load_configs(conf_file))

    def load_configs(self, conf_file):
        """
        Assumes that the config file does not have any sections, so throw it all in global
        """
        with open(conf_file) as stream:
            lines = itertools.chain(("[global]",), stream)
            self._config.read_file(lines)
        return self._config['global']

    def remove_quotes(self, configs):
        """
        Because some values are wraped in single quotes
        """
        for key in configs:
            value = configs[key]
            if value[0] == "'" and value[-1] == "'":
                configs[key] = value[1:-1]
        return configs
