import sys
import logging
import requests


class CustomLogger(logging.Logger):

    def __init__(self, name):
        super().__init__(name)
        self.data_io = None
        self.error_table = None

    def _log(self, level, msg, *args, **kwargs):
        super(CustomLogger, self)._log(level, msg, *args, **kwargs)
        # Map level value to level text
        log_lvl = {10: 'debug',
                   20: 'info',
                   30: 'warning',
                   40: 'error',
                   50: 'critical',
                   }

        extra = {'datalogging_io': True,
                 }
        if 'extra' in kwargs:
            extra.update(kwargs['extra'])

        # Handle traceback if needed
        traceback_value = None
        if 'exc_info' in kwargs:
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename
            traceback_value = exc_type.__name__ + ": " + str(exc_obj) + " on line " + str(lineno) + " in " + filename

        if traceback_value is not None:
            msg += "\n" + traceback_value

        # If dataloggingIO is setup
        if self.data_io is not None and extra['datalogging_io'] is True:
            self.data_io.message(msg, log_lvl[level])


    #########################
    # DataLogging.io Service
    #########################
    def datalogging_io_config(self, dl_config):
        self.data_io = DataLoggingIO(dl_config['host'], dl_config['apikey'], dl_config['group_key'])

    def datalogging_io_start(self):
        if self.data_io is not None:
            self.data_io.start_scrape()

    def datalogging_io_stop(self):
        if self.data_io is not None:
            self.data_io.stop_scrape()

    def datalogging_io_item_count(self, count):
        if self.data_io is not None:
            self.data_io.scrape_count(count)


# Use our custom logging class, will use any settings already set
logging.setLoggerClass(CustomLogger)
logger = logging.getLogger('custom_logger')


class DataLoggingIO:
    """
    dev.datalogging.io
    """
    def __init__(self, domain, apikey, group):
        self.apikey = apikey
        self.domain = '{}/api/v1/add/group?apikey={}&key={}'.format(domain, apikey, group)

    def start_scrape(self):
        data = [{'sensor_name': 'Running', 'value': True}]
        self._send(data)

    def stop_scrape(self):
        data = [{'sensor_name': 'Running', 'value': False}]
        self._send(data)

    def scrape_count(self, count):
        try:
            data = [{'sensor_name': 'Item Count', 'value': int(count)}]
            self._send(data)
        except ValueError:
            # Log message
            self.message("Invalid count: " + str(count), level='warning')

    def message(self, message, level=None):
        if level == 'critical':
            sensor_name = 'Log Critical'
        elif level == 'error':
            sensor_name = 'Log Errors'
        elif level == 'warning':
            sensor_name = 'Log Warnings'
        elif level == 'info':
            sensor_name = 'Log Info'
        else:
            sensor_name = 'Log Debug'

        data = [{'sensor_name': sensor_name, 'value': str(message)}]
        self._send(data)

    def _send(self, data):
        r = requests.post(self.domain, json=data).json()
        try:
            if r['success'] is not True:
                print("Error: " + r['message'])
        except KeyError:
            print("Error: " + r['message'])
