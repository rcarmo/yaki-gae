#!/usr/bin/env python
# encoding: utf-8
"""
wiki.py

Created by Rui Carmo on 2013-12-10.
Published under the MIT license.
"""

import os, sys, logging

log = logging.getLogger()

from yaki import Store
from yaki.constants import *
from google.appengine.ext import ndb
from google.appengine.api import memcache
from difflib import get_close_matches
from models import Page
from decorators import *
from yaki.constants import META_RECENT, META_MTIMES

class WikiController:

    def __init__(self):
        pass

    @staticmethod
    @memoize_function
    def get_recent_changes(limit = 100):
        """Get (limit) last modified pages, assuming they're in the local store"""

        result = memcache.get(META_RECENT)
        if not result:
            result = []
            for i in ndb.gql("SELECT path, mtime FROM Page ORDER BY mtime DESC LIMIT %d" % limit):
                result.append(i.path.lower())
            memcache.set(META_RECENT, result)
        return result


    @staticmethod
    @memoize_function
    def get_page_mtimes():
        """Return modification times for all known pages""" 

        result = memcache.get(META_MTIMES)
        if not result:
            result = {}
            for i in ndb.gql("SELECT path, mtime FROM Page"):
                result[i.path.lower()] = i.mtime
            memcache.set(META_MTIMES, result)
        return result


    @staticmethod
    @memoize_function
    def get_page_headers():
        result = memcache.get(META_HEADERS)
        if not result:
            result = {}
            for i in ndb.gql("SELECT path, headers FROM Page"):
                result[i.path.lower()] = i.headers
            memcache.set(META_HEADERS, result)
        return result


    @staticmethod
    @memoize_function
    def get_close_matches_for_page(path):
        """Get a list of close matches for a given page/path"""

        pages = WikiController.get_page_mtimes()
        return get_close_matches(path, pages.keys())


    @staticmethod
    @memoize_function
    def get_page(path):
        """Returns a single page"""

        return Page.get_by_id(path.lower())


    @staticmethod
    @memoize_function
    def resolve_alias(path):
        return None
