#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, os.path, sys, logging
from bottle import app, route, redirect, static_file, view

from utils import path_for
from utils.decorators import timed, cache_control
from config import settings

log = logging.getLogger()


@route('/')
def index():
    redirect(os.path.join(settings.wiki.base, settings.wiki.home))

# this is actually overridden in YAML and handled internally by GAE
@route('/static/<filepath:path>')
@timed
@cache_control(settings.cache.cache_control)
def static(filepath):
    """Handles static files"""

    log.debug(path_for(os.path.join('themes',settings.theme,'static')))
    return static_file(filepath, root=path_for(os.path.join('themes',settings.theme,'static')))

