#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: et:ts=4:sw=4:
"""
Main application script

Created by: Rui Carmo
License: MIT (see LICENSE.md for details)
"""

import os, sys, json, logging, gettext
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Make sure our bundled libraries take precedence
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'lib'))

import utils, bottle
from config import settings

bottle.TEMPLATE_PATH = [os.path.join("themes", settings.theme, "views")]
bottle.DEBUG = True

# Initialize translations
english = gettext.translation('yaki', os.path.join(os.path.dirname(__file__), 'locale'), languages=['en'])
english.install()
log.info(_('translation_applied'))

import api, routes, controllers, tasks

app = bottle.default_app()
bottle.run(app=app, server='gae')
