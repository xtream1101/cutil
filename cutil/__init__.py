from cutil.database import Database  # noqa: F401
from cutil.config import Config  # noqa: F401
from cutil.custom_terminal import CustomTerminal  # noqa: F401
from cutil.repeating_timer import RepeatingTimer  # noqa: F401

import os
import re
import sys
import uuid
import time
import pytz
import json
import queue
import random
import socket
import urllib
import hashlib
import logging
import datetime
import threading
from hashids import Hashids
from functools import wraps


logger = logging.getLogger(__name__)


####
# Time related functions
####
def get_epoch():
    """
    :return: time as epoch
    """
    return int(time.time())


def get_datetime():
    """
    :return: datetime object
    """
    return datetime.datetime.now()


def datetime_to_str(timestamp):
    # The script is set to use UTC, so all times are in UTC
    return timestamp.isoformat() + "+0000"


def datetime_to_utc(timestamp):
    return timestamp.astimezone(pytz.timezone('UTC'))


def str_to_date(timestamp, formats=["%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"]):
    rdata = None
    if timestamp is None:
        return None

    for time_format in formats:
        try:
            rdata = datetime.datetime.strptime(timestamp, time_format)
        except ValueError:
            rdata = None
        else:
            # If we did not raise an exception
            break

    return rdata


###
# Threading
###
def threads(num_threads, data, callback, *args, **kwargs):
    q = queue.Queue()
    item_list = []

    def _thread_run():
        while True:
            item = q.get()
            try:
                item_list.append(callback(item, *args, **kwargs))
            except Exception:
                logger.exception("Error in _thread_run callback {} with item:\n{}".format(callback.__name__, item))
            q.task_done()

    for i in range(num_threads):
        t = threading.Thread(target=_thread_run)
        t.daemon = True
        t.start()

    # Fill the Queue with the data to process
    for item in data:
        q.put(item)

    # Start processing the data
    q.join()

    return item_list


####
# Other functions
####
def get_internal_ip():
    return socket.gethostbyname(socket.gethostname())


def generate_key(value=None, salt=None, size=8):
    if value is None:
        value = random.randint(0, 999999)

    if salt is None:
        salt = random.randint(0, 999999)

    if not isinstance(size, int):
        # Enforce that size must be an int
        size = 8

    hashids = Hashids(salt=str(salt), min_length=size)
    return hashids.encode(value)


def create_uid():
    # Named uid and not uuid because this function does not have to use uuid's
    uid = uuid.uuid4().hex
    logger.debug("Created new uid: {}".format(uid))
    return uid


def get_default_header():
    default_header = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
    return default_header


def get_value(key, object, default_val=None):
    """
    Pass in object with a key to get its value, if it can not, it will return `default_val`
    """
    try:
        return object[key]
    except KeyError:
        return default_val


def make_url_safe(string):
    # Convert special chars to % chars
    return urllib.parse.quote_plus(string)


def sanitize(string):
    """
    Catch and replace invalid path chars
    [replace, with]
    """
    replace_chars = [
        ['\\', '-'], [':', '-'], ['/', '-'],
        ['?', ''], ['<', ''], ['>', ''],
        ['`', '`'], ['|', '-'], ['*', '`'],
        ['"', '\''], ['.', ''], ['&', 'and']
    ]
    for ch in replace_chars:
        string = string.replace(ch[0], ch[1])
    return string


def rreplace(s, old, new, occurrence):
    """
    Taken from: http://stackoverflow.com/a/2556252
    """
    li = s.rsplit(old, occurrence)
    return new.join(li)


def get_script_name(ext=True):
    name = os.path.basename(sys.argv[0])
    if ext is False:
        name = name.split('.')[0]
    return name


####
# File/filesystem related function
####
def get_file_ext(url):
    file_name, file_extension = os.path.splitext(url)
    return file_extension


def norm_path(path):
    """
    :return: Proper path for os with vars expanded out
    """
    # path = os.path.normcase(path)
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.normpath(path)
    return path


def create_hashed_path(base_path, name):
    """
    Create a directory structure using the hashed filename
    :return: string of the path to save to not including filename/ext
    """
    name_hash = hashlib.md5(name.encode('utf-8')).hexdigest()
    if base_path.endswith('/') or base_path.endswith('\\'):
        save_path = base_path
    else:
        save_path = base_path + "/"
    depth = 2  # will have depth of n dirs (MAX of 16 because length of md5 hash)
    for i in range(1, depth + 1):
        end = i * 2
        start = end - 2
        save_path += name_hash[start:end] + "/"
    return save_path, name_hash


def create_path(path, is_dir=False):
    """
    Check if path exists, if not create it
    :param path: path or file to create directory for
    :param is_dir: pass True if we are passing in a directory, default = False
    :return: os safe path from `path`
    """
    path = norm_path(path)
    path_check = path
    if not is_dir:
        path_check = os.path.dirname(path)

    does_path_exists = os.path.exists(path_check)

    if does_path_exists:
        return path

    try:
        os.makedirs(path_check)
    except OSError:
        pass

    return path


def dump_json(file_, data):
    create_path(file_)
    if not file_.endswith('.json'):
        file_ += '.json'

    with open(file_, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4)


# Lets only do this once
price_pattern = re.compile('([\d,.]+)(\D*([\d,.]+))?')


def parse_price(price):
    price_raw = re.search(price_pattern, price)
    price = {'low': price_raw.group(1),
             'high': price_raw.group(3)
             }

    for key, value in price.items():
        if value is not None:
            new_value = value.replace(',', '').replace('.', '')
            try:
                # Check if price has cents
                if value[-3] in [',', '.']:
                    # Add . for cents back
                    new_value = new_value[:-2] + '.' + new_value[-2:]
            except IndexError:
                # Price is 99 or less with no cents
                pass
            price[key] = float(new_value)

    return price


def get_image_dimension(url):
    import requests
    from PIL import Image  # pip install pillow
    from io import BytesIO
    size = {'width': None,
            'height': None}
    try:
        if url.startswith('//'):
            url = "http:" + url
        data = requests.get(url, timeout=15).content
        im = Image.open(BytesIO(data))

        size['width'], size['height'] = im.size
    except Exception:
        logger.debug("Error getting image size {}".format(url), exc_info=True)
        logger.warning("Error getting image size {}".format(url))

    return size


def crop_image(image_file, output_file=None, height=None, width=None, x=None, y=None):
    from PIL import Image  # pip install pillow
    if output_file is None or height is None or width is None or x is None or y is None:
        logger.error("Must pass in all params: output_file, height, width, x, and y as named args")
        return None

    if width <= 0 or height <= 0:
        logger.warning("Width and height must be 1 or greater")
        raise ValueError

    image = Image.open(image_file)
    image.crop((x, y, width + x, height + y)).save(output_file)

    return output_file


####
# Decorators
####
def rate_limited(max_per_second):
    """
    Source: https://gist.github.com/gregburek/1441055
    """
    lock = threading.Lock()
    min_interval = 1.0 / max_per_second

    def decorate(func):
        last_time_called = time.perf_counter()

        @wraps(func)
        def rate_limited_function(*args, **kwargs):
            lock.acquire()
            nonlocal last_time_called
            elapsed = time.perf_counter() - last_time_called
            left_to_wait = min_interval - elapsed

            if left_to_wait > 0:
                time.sleep(left_to_wait)

            ret = func(*args, **kwargs)
            last_time_called = time.perf_counter()
            lock.release()
            return ret

        return rate_limited_function

    return decorate
