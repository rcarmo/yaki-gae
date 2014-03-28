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
from decorators import memoize

@memoize
def get_recent_changes(limit):
    result = memcache.get("meta:recent_changes")
    if not result:
        result = []
        for i in ndb.gql("SELECT path, mtime FROM Page ORDER BY mtime DESC LIMIT %d" % limit):
            result.append(i.path.lower())
        memcache.set("meta:recent_changes", result)
    return result


def get_page_mtimes():
    result = memcache.get("meta:page_mtimes")
    if not result:
        result = {}
        for i in ndb.gql("SELECT path, mtime FROM Page"):
            result[i.path.lower()] = i.mtime
        memcache.set("meta:page_mtimes", result)
    return result


def get_page_headers():
    result = memcache.get("meta:page_headers")
    if not result:
        result = {}
        for i in ndb.gql("SELECT path, headers FROM Page"):
            result[i.path.lower()] = i.headers
        memcache.set("meta:page_headers", result)
    return result


@memoize
def get_close_matches_for_page(path):
    """Get a list of close matches for a given page/path"""

    pages = get_page_mtimes()
    return get_close_matches(path, pages.keys())


@memoize
def get_page(path):
    """Returns a single page"""

    return Page.get_by_id(path.lower())


@memoize
def resolve_alias(path):
    return None
