import os
import time
import logging
import threading


logger = logging.getLogger(__name__)


class CustomTerminal:

    def __init__(self):
        self._prev_cstr = ''
        self._bprint_disable = False

        self._proxy_list = []
        self._current_proxy = None
        self._custom_proxy = False
        self._apikey_list = []
        self._current_apikey = None

        # Block print display messages and values
        self._bprint_messages = None
        # Block print display order (only items listed here will be displayed)
        self._bprint_order = None

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
            print(cstr + " " * num_spaces, end='\r')
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
            print(self.bprint_messages[item][0] + ": " + str(self.bprint_messages[item][1]))

        if self.bprint_disable is not True:
            # Update terminal every n seconds
            t_reload = threading.Timer(.5, self._bprint_display)
            t_reload.setDaemon(True)
            t_reload.start()
