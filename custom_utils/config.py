import os
import sys
import yaml


class ScraperConfig:
    def __init__(self, config_file):
        # Load config values
        if not os.path.isfile(config_file):
            print("No config file found: " + config_file)
            sys.exit(0)

        config = _yaml_load(config_file)
        # Set default values
        self.config_values = {'save_dir': None,
                              'restart': None,
                              'proxies': [],
                              'apikeys': [],
                              'datalogging_io_host': None,
                              }

        if 'save_dir' in config:
            self.config_values['save_dir'] = config['save_dir']

        if 'restart' in config:
            self.config_values['restart'] = config['restart']

        if 'proxies' in config:
            self.config_values['proxies'] = config['proxies']

        if 'apikeys' in config:
            self.config_values['apikeys'] = config['apikeys']

        if 'datalogging_io_host' in config and 'datalogging_io_apikey' in config and 'datalogging_io_groupkey' in config:
            self.config_values['datalogging_io'] = {'host': config['datalogging_io_host'],
                                                    'apikey': config['datalogging_io_apikey'],
                                                    'group_key': config['datalogging_io_groupkey']
                                                    }

    def get_values(self):
        return self.config_values


def _yaml_load(config_file):
    """
    Generic loader for yaml config files
    :return: dict of values
    """
    with open(config_file, 'r') as stream:
        values = yaml.load(stream)
    return values
