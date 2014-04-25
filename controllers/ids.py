#!/usr/bin/env python
# encoding: utf-8
"""
ids.py

Created by Rui Carmo on 2014-03-30
Published under the MIT license.
"""

import os, sys, logging
from bottle import request
from google.appengine.api import memcache
from constants import *

log = logging.getLogger()

class IDSController:

    def __init__(self, threshold = 10):
        self.threshold = 10
        pass

    def flag(self, request):
        """Flags a specific request as suspicious for some reason"""

        addr = request.remote_addr

        # not going to use compare and set because we need expiry and atomicity isn't critical
        count = memcache.get(addr, namespace=NS_IDS)
        if count:
            count = count + 1
        else:
            count = 1
        memcache.set(request.remote_addr, count, namespace=NS_IDS, time=60)

    def is_suspicious(self, request):
        addr = request.remote_addr
        count = memcache.get(addr, namespace=NS_IDS)
        if count:
            if count > self.threshold:
                return True
        return False



