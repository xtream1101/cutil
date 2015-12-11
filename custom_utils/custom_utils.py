import os
import time
import json
import urllib
import random
import hashlib
import logging
import requests
import traceback
from bs4 import BeautifulSoup
from datetime import datetime
from custom_utils.exceptions import *


class CustomUtils:

    def __init__(self):
        self._prev_cstr = ''
        self._proxy_list = []
        self._current_proxy = {}

    ####
    # Terminal/display related functions
    ####
    def cprint(self, cstr):
        """
        Clear line, then reprint on same line
        :param cstr: string to print on current line
        """
        cstr = str(cstr)  # Force it to be a string
        cstr_len = len(cstr)
        prev_cstr_len = len(self._prev_cstr)
        num_spaces = 0
        if cstr_len < prev_cstr_len:
            num_spaces = abs(prev_cstr_len - cstr_len)
        try:
            print(cstr + " "*num_spaces, end='\r')
            self._prev_cstr = cstr
        except UnicodeEncodeError:
            print('Processing...', end='\r')
            self._prev_cstr = 'Processing...'

    def log(self, message):
        print(str(message) + '\n')

    ####
    # Time related functions
    ####
    def get_utc_epoch(self):
        """
        :return: utc time as epoch
        """
        return int(time.time())

    ####
    # Other functions
    ####
    def get_default_header(self):
        default_header = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
        return default_header

    def set_url_header(self, url_header):
        if url_header is None:
            # Use default
            return self.get_default_header()
        else:
            return url_header

    def sanitize(self, string):
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

    def rreplace(self, s, old, new, occurrence):
        """
        Taken from: http://stackoverflow.com/a/2556252
        """
        li = s.rsplit(old, occurrence)
        return new.join(li)

    ####
    # File/filesystem related function
    ####
    def get_file_ext(self, url):
        file_name, file_extension = os.path.splitext(url)
        return file_extension

    def norm_path(self, path):
        """
        :return: Proper path for os
        """
        # path = os.path.normcase(path)
        path = os.path.normpath(path)
        return path

    def create_hashed_path(self, base_path, name):
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
        for i in range(1, depth+1):
            end = i*2
            start = end-2
            save_path += name_hash[start:end] + "/"
        return save_path, name_hash

    def create_path(self, path, is_dir=False):
        """
        Check if path exists, if not create it
        :param path: path or file to create directory for
        :param is_dir: pass True if we are passing in a directory, default = False
        :return: os safe path from `path`
        """
        path = self.norm_path(path)
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

    def save_props(self, data):
        self.create_path(data['save_path'])
        with open(data['save_path'] + ".json", 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4)

    def download(self, url, file_path, header={}, redownload=False):
        """
        :return: True/False
        """
        success = True

        if redownload is False:
            # See if we already have the file
            if os.path.isfile(file_path):
                return True

        self.create_path(file_path)

        if url.startswith('//'):
            url = "http:" + url
        try:
            with urllib.request.urlopen(
              urllib.request.Request(url, headers=header)) as response, \
                open(file_path, 'wb') as out_file:
                    data = response.read()
                    out_file.write(data)

        except urllib.error.HTTPError as e:
            success = False
            # We do not need to show the user 404 errors
            if e.code != 404:
                self.log("Download Error (" + url + "): " + str(e))

        except Exception as e:
            success = False
            self.log("Download Error (" + url + "): " + str(e))

        return success

    def set_proxies(self, proxy_list):
        for proxy in proxy_list:
            self._proxy_list.append({'http': proxy})

        # Now start using one
        self.rotate_proxy()

    def get_current_proxy(self):
        if 'http' in self._current_proxy:
            return self._current_proxy['http']
        return None

    def rotate_proxy(self):
        new_proxy = random.choice(self._proxy_list)

        # Used for get_html() (requests)
        self._current_proxy = new_proxy

        # Used for download() (urllib)
        proxy_support = urllib.request.ProxyHandler(self._current_proxy)
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)

        return self.get_current_proxy()

    ####
    # BeautifulSoup Related functions
    ####
    def get_site(self, url, header={}, page_format='html', return_error_page=False):
        """
        Try and return soup or json content, if not throw a RequestsError
        """
        if not url.startswith('http'):
            url = "http://" + url
        try:
            self.response = requests.get(url, headers=header, proxies=self._current_proxy)
            if self.response.status_code == requests.codes.ok:
                # Return the correct format
                if page_format == 'html':
                    data = BeautifulSoup(self.response.text, "html5lib")
                elif page_format == 'json':
                    data = self.response.json()
                elif page_format == 'xml':
                    data = BeautifulSoup(self.response.text, "lxml")
                elif page_format == 'raw':
                    # Return unparsed html
                    data = self.response.text

                return data

            self.response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # self.log("HTTPError [get_site]: " + str(e.response.status_code) + " " + url, level='error')
            raise RequestsError(str(e))

        except requests.exceptions.ConnectionError as e:
            # self.log("ConnectionError [get_site]: " + str(e) + " " + url, level='error')
            raise RequestsError(str(e))
        except requests.exceptions.TooManyRedirects as e:
            # self.log("TooManyRedirects [get_site]: " + str(e) + " " + url, level='error')
            raise RequestsError(str(e))
        except Exception as e:
            # self.log("Exception [get_site]: " + str(e) + " " + url + "\n" + str(traceback.format_exc()), level='critical')
            raise RequestsError(str(e))
