from cutil.database import Database  # noqa: F401
from cutil.config import Config  # noqa: F401
from cutil.custom_terminal import CustomTerminal  # noqa: F401
from cutil.repeating_timer import RepeatingTimer  # noqa: F401

import os
import re
import sys
import uuid
import math
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
import collections
from hashids import Hashids
from functools import wraps
from operator import itemgetter
from functools import cmp_to_key


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
def multikey_sort(items, columns):
    """Source: https://stackoverflow.com/questions/1143671/python-sorting-list-of-dictionaries-by-multiple-keys
    """
    comparers = [
        ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1))
        for col in columns
    ]

    def cmp(a, b):
        return (a > b) - (a < b)

    def comparer(left, right):
        comparer_iter = (
            cmp(fn(left), fn(right)) * mult
            for fn, mult in comparers
        )
        return next((result for result in comparer_iter if result), 0)
    return sorted(items, key=cmp_to_key(comparer))


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
    logger.debug("Created new uid: {uid}".format(uid=uid))
    return uid


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


def flatten(dict_obj, prev_key='', sep='_'):
    items = {}
    for key, value in dict_obj.items():
        new_key = prev_key + sep + key if prev_key != '' else key

        if isinstance(value, dict):
            items.update(flatten(value, new_key))
        else:
            items[new_key] = value

    return items


def update_dict(d, u):
    """
    Source: https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    """
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update_dict(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def get_script_name(ext=False):
    name = os.path.basename(sys.argv[0])
    if ext is False:
        name = name.split('.')[0]
    return name


def chunks_of(max_chunk_size, list_to_chunk):
    """
    Yields the list with a max size of max_chunk_size
    """
    for i in range(0, len(list_to_chunk), max_chunk_size):
        yield list_to_chunk[i:i + max_chunk_size]


def split_into(max_num_chunks, list_to_chunk):
    """
    Yields the list with a max total size of max_num_chunks
    """
    max_chunk_size = math.ceil(len(list_to_chunk) / max_num_chunks)
    return chunks_of(max_chunk_size, list_to_chunk)


####
# File/filesystem related function
####
def get_file_ext(file):
    file_name, file_extension = os.path.splitext(file)
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


def create_hashed_path(base_path, name, depth=2):
    """
    Create a directory structure using the hashed filename
    :return: string of the path to save to not including filename/ext
    """
    if depth > 16:
        logger.warning("depth cannot be greater then 16, setting to 16")
        depth = 16

    name_hash = hashlib.md5(str(name).encode('utf-8')).hexdigest()
    if base_path.endswith(os.path.sep):
        save_path = base_path
    else:
        save_path = base_path + os.path.sep
    for i in range(1, depth + 1):
        end = i * 2
        start = end - 2
        save_path += name_hash[start:end] + os.path.sep

    return {'path': save_path,
            'hash': name_hash,
            }


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
price_pattern = re.compile('(?P<low>[\d,.]+)(?:\D*(?P<high>[\d,.]+))?')


def parse_price(price):
    found_price = {'low': None,
                   'high': None
                   }
    price_raw = re.search(price_pattern, price)
    if price_raw:
        matched = price_raw.groupdict()
        found_price['low'] = matched.get('low')
        found_price['high'] = matched.get('high')

    for key, value in found_price.items():
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
            found_price[key] = float(new_value)

    return found_price


def get_image_dimension(url):
    import requests
    from PIL import Image  # pip install pillow
    from io import BytesIO
    size = {'width': None,
            'height': None,
            }
    try:
        if url.startswith('//'):
            url = "http:" + url
        data = requests.get(url, timeout=15).content
        im = Image.open(BytesIO(data))

        size['width'], size['height'] = im.size
    except Exception:
        logger.debug("Error getting image size {url}".format(url=url), exc_info=True)
        logger.warning("Error getting image size {url}".format(url=url))

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
            try:
                elapsed = time.perf_counter() - last_time_called
                left_to_wait = min_interval - elapsed
                if left_to_wait > 0:
                    time.sleep(left_to_wait)

                return func(*args, **kwargs)
            finally:
                last_time_called = time.perf_counter()
                lock.release()

        return rate_limited_function

    return decorate


def timeit(stat_tracker_func, name):
    """
    Pass in a function and the name of the stat
    Will time the function that this is a decorator to and send
    the `name` as well as the value (in seconds) to `stat_tracker_func`

    `stat_tracker_func` can be used to either print out the data or save it
    """
    def _timeit(func):
        def wrapper(*args, **kw):
            start_time = time.time()
            result = func(*args, **kw)
            stop_time = time.time()
            stat_tracker_func(name, stop_time - start_time)

            return result
        return wrapper

    return _timeit


####
# Regex
####
# Keep re.compile's outside of fn as to only create it once
proxy_parts_pattern = re.compile('^(?:(?P<schema>\w+):\/\/)(?:(?P<user>.*):(?P<password>.*)@)?(?P<host>[^:]*)(?::(?P<port>\d+))?$')


def get_proxy_parts(proxy):
    """
    Take a proxy url and break it up to its parts
    """
    proxy_parts = {'schema': None,
                   'user': None,
                   'password': None,
                   'host': None,
                   'port': None,
                   }
    # Find parts
    results = re.match(proxy_parts_pattern, proxy)
    if results:
        matched = results.groupdict()
        for key in proxy_parts:
            proxy_parts[key] = matched.get(key)

    else:
        logger.error("Invalid proxy format `{proxy}`".format(proxy=proxy))

    if proxy_parts['port'] is None:
        proxy_parts['port'] = '80'

    return proxy_parts


def remove_html_tag(input_str='', tag=None):
    """
    Returns a string with the html tag and all its contents from a string
    """
    result = input_str
    if tag is not None:
        pattern = re.compile('<{tag}[\s\S]+?/{tag}>'.format(tag=tag))
        result = re.sub(pattern, '', str(input_str))

    return result
