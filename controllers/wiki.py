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
from utils.timekit import datetime_to_epoch
from config import settings, NS_PAGE_METADATA, ALIASING_CHARS
from bs4 import BeautifulSoup
import HTMLParser

RECENT_CHANGES = "recent_changes"
MTIMES         = "mtimes"
HEADERS        = "headers"
WIKI_ALIASES   = "wiki_aliases" # aliases defined in wiki meta/Aliases
PAGE_ALIASES   = "page_aliases" # autogenerated aliases from page names
INTERWIKI_MAP  = "interwiki"    # custom URL schemas that expand to separate sites
ACRONYM_MAP    = "acronyms"     # acronym expansions

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
                result[i.path] = datetime_to_epoch(i.mtime)
            memcache.set(MTIMES, result, namespace=NS_PAGE_METADATA)
        return result


    @staticmethod
    @memoize
    def get_page_headers():
        result = memcache.get(HEADERS, namespace=NS_PAGE_METADATA)
        if not result:
            result = {}
            for i in ndb.gql("SELECT path, headers FROM Page"):
                result[i.path] = i.headers
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
        log.debug("%s:%s" % (path, filename))

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
        wiki_aliases = WikiController.get_wiki_aliases()
        alias = wiki_aliases.get(path)
        if alias:
            return alias
        page_aliases = WikiController.get_page_aliases()
        alias = page_aliases.get(path)
        if alias:
            return alias
        # most common case that may not be in our caches yet
        if "_" in path:
            return path.replace("_"," ")
        return None


    @staticmethod
    @memoize
    def get_page_aliases():
        result = memcache.get(PAGE_ALIASES, namespace=NS_PAGE_METADATA)
        if not result:
            result = {}
            mtimes = WikiController.get_page_mtimes()
            pages = mtimes.keys()
            for p in pages:
                for c in ALIASING_CHARS:
                    result[p.replace(" ",c)] = p
            memcache.set(PAGE_ALIASES, result, namespace=NS_PAGE_METADATA)
        return result


    @staticmethod
    def parse_mapping_page(page, transform):
        result = {}
        try:
            page = WikiController.get_page(page)
        except Exception as e:
            log.warn("Could not load %s: %s" % (page, e))
            return result

        # prepare to parse only <pre> tags (so that we can have multiple maps organized by sections)
        soup = BeautifulSoup(render_markup(page.body, page.mime_type))

        all_sections = u''.join(map(lambda t: str(t.string), soup.find_all('pre'))).strip()
        # now that we have the full map, let's build the schema hash
        for line in all_sections.split('\n'):
            try:
                (link, replacement) = line.strip().split(' ',1)
                for item in transform(link, replacement):
                    result.update(item)
            except ValueError:
                log.warn("skipping line '%s'" % line)
                pass
        return result


    @staticmethod
    def get_wiki_aliases():
        def genalias(k, v):
            return [{k: v}, {k.replace('_', ' '), v}]

        result = memcache.get(WIKI_ALIASES, namespace=NS_PAGE_METADATA)
        if not result:
            result = WikiController.parse_mapping_page(settings.wiki.aliases, genalias)
            memcache.set(WIKI_ALIASES, result, namespace=NS_PAGE_METADATA)
        return result


    @staticmethod
    def get_interwiki_map():
        def genschema(k, v):
            h = HTMLParser.HTMLParser()
            return [{k.lower(): h.unescape(v)}]

        result = memcache.get(INTERWIKI_MAP, namespace=NS_PAGE_METADATA)
        if not result:
            result = WikiController.parse_mapping_page(settings.wiki.interwiki, genschema)
            memcache.set(INTERWIKI_MAP, result, namespace=NS_PAGE_METADATA)
        return result
    

    @staticmethod
    def get_acronym_map():
        def lowerkey(k, v):
            return [{k.lower(): v}]

        result = memcache.get(ACRONYM_MAP, namespace=NS_PAGE_METADATA)
        if not result:
            result = WikiController.parse_mapping_page(settings.wiki.interwiki, lowerkey)
            memcache.set(ACRONYM_MAP, result, namespace=NS_PAGE_METADATA)
        return result
