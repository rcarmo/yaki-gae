#!/usr/bin/env python
# encoding: utf-8
"""
Tag acronyms with `title` attributes

Created by Rui Carmo on 2007-01-11.
Published under the MIT license.
"""

import os, sys, logging

log = logging.getLogger()

import urlparse, re, time
from bs4 import BeautifulSoup, SoupStrainer
from plugins import plugin
from controllers.wiki import WikiController as wc
from utils.core import Singleton
from utils.markup import render_markup

meta_page = 'meta/Acronyms'

@plugin
class Acronyms:
    __metaclass__ = Singleton

    category  = 'markup'
    tags      = ['span','caps']
    acronyms  = {}

    def __init__(self):
        self.acronyms = wc.get_acronym_map()
        log.debug(self)


    def run(self, serial, tag, tagname, pagename, soup, request, response):
        if (self.mtime < wc.mtime(self.meta_page)):
            self.load()
        try:
            acronym = ''.join(tag.find_all(text=re.compile('.+'))).strip().lower()
        except:
            return True

        if acronym in self.acronyms.keys():
            meaning = self.acronyms[acronym]
            tag['title'] = meaning
            # this tag does not need to be re-processed
            return False
        return True
