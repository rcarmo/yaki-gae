#!/usr/bin/env python
# encoding: utf-8
"""
Tag acronyms with `title` attributes

Created by Rui Carmo on 2007-01-11.
Published under the MIT license.
"""

import logging

log = logging.getLogger()

import re
from controllers.wiki import WikiController as wc
from utils.core import Singleton
from plugins import plugin

meta_page = 'meta/Acronyms'


@plugin
class Acronyms:
    __metaclass__ = Singleton

    category = 'markup'
    tags     = ['span', 'caps']
    acronyms = {}

    def __init__(self):
        self.acronyms = wc.get_acronym_map()
        log.debug(self)


    def run(self, serial, tag, tagname, pagename, soup, request, response):
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
