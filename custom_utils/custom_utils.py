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
from custom_utils.log import DataLoggingIO


class CustomUtils:

    def __init__(self, proxies=[], apikeys=[]):
        self._prev_cstr = ''
        self.bprint_disable = False


         self._proxy_list = []
        self._current_proxy = None
        self._apikey_list = []
        self._current_apikey = None

        # Block print display messages and values
        self.bprint_messages = None
        # Block print display order (only items listed here will be displayed)
        self.bprint_order = None

        # If we have proxies then add them
        if len(proxies) > 0:
            self.set_proxies(proxies)
            self.log("Using Proxy: " + self.get_current_proxy())

        # If we have apikeys then add them
        if len(apikeys) > 0:
            self.set_apikeys(apikeys)
            self.log("Using API Key: " + self.get_current_apikey())

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

    def enable_bprint(self, bprint_msg={}, bprint_order=[]):
        # Block print display messages and values
        self.bprint_messages = bprint_msg

        # Block print display order (only items listed here will be displayed)
        self.bprint_order = bprint_order

        # Start instance of block print
        self._bprint_display()

    def disable_bprint(self):
        self.bprint_disable = True

    def bprint(self, bmsg, line):
        """
        bprint: Block Print
        self.bprint_messages[line][0] is always the display text
        self.bprint_messages[line][1] is always the value
        """
        self.bprint_messages[line][1] = bmsg

    def _bprint_display(self):
        self.bprint_messages['title'][1] = time.time()

        os.system('cls' if os.name == 'nt' else 'clear')
        for item in self.bprint_order:
            print(self.bprint_messages[item][0] + ": " +
                  str(self.bprint_messages[item][1]))

        if self.bprint_disable is not True:
            # Update terminal every n seconds
            t_reload = threading.Timer(.5, self._bprint_display)
            t_reload.setDaemon(True)
            t_reload.start()

    def log(self, message):
        print(str(message) + '\n')

    ####
    # Time related functions
    ####
    def get_epoch(self):
        """
        :return: time as epoch
        """
        return int(time.time())

    def get_datetime(self):
        """
        :return: datetime object
        """
        return datetime.datetime.now()

    ####
    # Other functions
    ####
    def get_default_header(self):
        default_header = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
        return default_header

    def get_value(self, key, object, default_val=None):
        """
        Pass in object with a key to get its value, if it can not, it will return `default_val`
        """
        try:
            return object[key]
        except KeyError:
            return default_val

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

    ###
    # Proxies
    ###
    # TODO: Combine the proxy and apikey functions into one
    #         Do not combine the gets
    # TODO: Notify client when all proxies or apikeys have been used/tried
    def set_proxies(self, proxy_list):
        for proxy in proxy_list:
            self._proxy_list.append(proxy)
        # Now start using one
        self.rotate_proxy()

    def get_current_proxy(self):
        return self._current_proxy

    def rotate_proxy(self):
        # Used for get_site() (requests)
        self._current_proxy = self.get_next_proxy()

        # Used for download() (urllib)
        proxy_support = urllib.request.ProxyHandler(self._current_proxy)
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)

        return self.get_current_proxy()

    def get_next_proxy(self):
        if self.get_current_proxy() is None:
            idx = 0
        else:
            idx = self._proxy_list.index(self.get_current_proxy())
            idx += 1
            if idx >= len(self._proxy_list):
                # Start at first key again
                idx = 0
        try:
            return self._proxy_list[idx]
        except IndexError:
            return None

    ###
    # API Keys
    ###
    def set_apikeys(self, apikey_list):
        for apikey in apikey_list:
            self._apikey_list.append(apikey)
        # Now start using one
        self.rotate_apikey()

    def get_current_apikey(self):
        return self._current_apikey

    def rotate_apikey(self):
        self._current_apikey = self.get_next_apikey()
        return self.get_current_apikey()

    def get_next_apikey(self):
        if self.get_current_apikey() is None:
            idx = 0
        else:
            idx = self._apikey_list.index(self.get_current_apikey())
            idx += 1
            if idx >= len(self._apikey_list):
                # Start at first key again
                idx = 0
        try:
            return self._apikey_list[idx]
        except IndexError:
            return None

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

    ####
    # BeautifulSoup Related functions
    ####
    def get_soup(self, raw_content, input_type='html'):
        rdata = None
        if input_type == 'html':
            rdata = BeautifulSoup(raw_content, "html.parser")  # html5lib
        elif input_type == 'xml':
            rdata = BeautifulSoup(raw_content, "lxml")
        return rdata

    def get_site(self, url, cookies={}, page_format='html', return_on_error=[], num_tries=0,
                 header={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}):
        """
        Try and return soup or json content, if not throw a RequestsError
        """
        num_tries += 1
        if not url.startswith('http'):
            url = "http://" + url
        try:
            self.response = requests.get(url, headers=header, cookies=cookies, proxies=self._current_proxy)
            if self.response.status_code == requests.codes.ok:
                # Return the correct format
                if page_format == 'html':
                    data = self.get_soup(self.response.text, input_type='html')
                elif page_format == 'json':
                    data = self.response.json()
                elif page_format == 'xml':
                    data = self.get_soup(self.response.text, input_type='xml')
                elif page_format == 'raw':
                    # Return unparsed html
                    data = self.response.text

                return data

            self.response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            response_code = str(e.response.status_code)

            # If the client wants to handle the error
            if int(response_code) in return_on_error:
                raise RequestsError(e, self.response.text)

            if response_code == '401' and num_tries < 4:
                # Fail after 3 tries
                self.log("HTTP 401 error, try #" + str(num_tries) + " on url: " + url, level='info')
                # self.log("Switching API Keys...")
                # self.rotate_apikey()
                # return self.get_site(url, header=header, page_format=page_format,
                #                      cookies=cookies, num_tries=num_tries)
            elif response_code == '403' and num_tries < 4:
                # Fail after 3 tries
                self.log("HTTP 403 error, try #" + str(num_tries) + " on url: " + url, level='info')
                # self.log("Switching proxies...")
                # self.rotate_proxy()
                # return self.get_site(url, header=header, page_format=page_format,
                #                      cookies=cookies, num_tries=num_tries)
            elif response_code == '504' and num_tries < 4:
                # Wait a second and try again, fail after 3 tries
                self.log("HTTP 504 error, try #" + str(num_tries) + " on url: " + url, level='info')
                time.sleep(1)
                return self.get_site(url, header=header, page_format=page_format,
                                     cookies=cookies, num_tries=num_tries)
            elif response_code == '520' and num_tries < 4:
                # Wait a second and try again, fail after 3 tries
                self.log("HTTP 520 error, try #" + str(num_tries) + " on url: " + url, level='info')
                time.sleep(1)
                return self.get_site(url, header=header, page_format=page_format,
                                     cookies=cookies, num_tries=num_tries)
            else:
                self.log("HTTPError [get_site]: " + response_code + " " + url, level='error')

        except requests.exceptions.ConnectionError as e:
            if num_tries < 4:
                self.log("ConnectionError [get_site] try #" + str(num_tries) + " Error" + str(e) + " " + url, level='warning')
                time.sleep(5)
                return self.get_site(url, header=header, page_format=page_format,
                                     cookies=cookies, num_tries=num_tries)
            else:
                self.log("ConnectionError [get_site]: " + str(e) + " " + url, level='error')
        except requests.exceptions.TooManyRedirects as e:
            self.log("TooManyRedirects [get_site]: " + str(e) + " " + url, level='error')
        except Exception as e:
            self.log("Exception [get_site]: " + str(e) + " " + url + "\n" + str(traceback.format_exc()), level='critical')
