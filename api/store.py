#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API calls for users

Created by: Rui Carmo
"""

import logging

log = logging.getLogger()

from bottle import get
import api

from utils.decorators import timed, jsonp, cache_results, cache_control

# local context
prefix = api.prefix + '/pages'

# Collection URI - List
@get(prefix)
@timed
@cache_results(30)
@cache_control(300)
@jsonp
def list_pages():
    pass
