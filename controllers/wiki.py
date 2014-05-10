#!/usr/bin/env python
# encoding: utf-8
"""
wiki.py

Created by Rui Carmo on 2013-12-10.
Published under the MIT license.
"""

import os, sys, logging

log = logging.getLogger()

from google.appengine.ext import ndb
from google.appengine.api import memcache
from difflib import get_close_matches
from models import Page, Attachment
from utils.core import Singleton
from utils.decorators import memoize
from utils.markup import render_markup
from config import settings, NS_PAGE_METADATA
from bs4 import BeautifulSoup
import HTMLParser

RECENT_CHANGES = "recent_changes"
MTIMES         = "mtimes"
HEADERS        = "headers"
ALIASES        = "aliases"

class WikiController:

    def __init__(self):
        pass

    @staticmethod
    @memoize
    def get_recent_changes(limit = 100):
        """Get (limit) last modified pages, assuming they're in the local store"""

        result = memcache.get(RECENT_CHANGES, namespace=NS_PAGE_METADATA)
        if not result:
            result = []
            for i in ndb.gql("SELECT path, mtime FROM Page ORDER BY mtime DESC LIMIT %d" % limit):
                result.append(i.path.lower())
            memcache.set(RECENT_CHANGES, result, namespace=NS_PAGE_METADATA)
        return result


    @staticmethod
    @memoize
    def get_page_mtimes():
        """Return modification times for all known pages""" 

        result = memcache.get(MTIMES, namespace=NS_PAGE_METADATA)
        if not result:
            result = {}
            for i in ndb.gql("SELECT path, mtime FROM Page"):
                result[i.path.lower()] = i.mtime
            memcache.set(MTIMES, result, namespace=NS_PAGE_METADATA)
        return result


    @staticmethod
    @memoize
    def get_page_headers():
        result = memcache.get(HEADERS, namespace=NS_PAGE_METADATA)
        if not result:
            result = {}
            for i in ndb.gql("SELECT path, headers FROM Page"):
                result[i.path.lower()] = i.headers
            memcache.set(HEADERS, result, namespace=NS_PAGE_METADATA)
        return result


    @staticmethod
    @memoize
    def get_close_matches_for_page(path):
        """Get a list of close matches for a given page/path"""

        pages = WikiController.get_page_mtimes()
        return get_close_matches(path, pages.keys())


    @staticmethod
    @memoize
    def get_page(path):
        """Returns a single page"""

        return Page.get_by_id(path.lower())


    @staticmethod
    @memoize
    def get_attachment(path, filename):
        """Returns a single page"""

        return Attachment.get_by_id(os.path.join(path,filename).lower())


    @staticmethod
    @memoize
    def mtime(path):
        """Returns a single page's modification time"""
        mtimes = WikiController.get_page_mtimes()
        if path in mtimes.keys():
            return mtimes[path]
        return 0


    @staticmethod
    @memoize
    def resolve_alias(path):
        aliases = WikiController.get_page_aliases()
        return aliases.get(path)


    @staticmethod
    def get_page_aliases():
        result = memcache.get(ALIASES, namespace=NS_PAGE_METADATA)
        if not result:
            result = {}
            try:
                page = WikiController.get_page(settings.wiki.aliases)
            except:
                log.warn("Aliases: no %s definitions" % settings.wiki.aliases)
                return result

            # prepare to parse only <pre> tags (so that we can have multiple maps organized by sections)
            soup = BeautifulSoup(render_markup(page.body, page.mime_type))
            h = HTMLParser.HTMLParser()

            all_sections = u''.join(map(lambda t: str(t.string), soup.find_all('pre'))).strip()
            # now that we have the full map, let's build the schema hash
            for line in all_sections.split('\n'):
                try:
                    (link, replacement) = line.strip().split(' ',1)
                    result[link] = replacement
                    result[link.replace('_',' ')] = replacement
                except ValueError:
                    log.warn("skipping line '%s'" % line)
                    pass
            memcache.set(ALIASES, result, namespace=NS_PAGE_METADATA)
        return result
