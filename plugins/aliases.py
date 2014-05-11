#!/usr/bin/env python
# encoding: utf-8
"""
Replace aliases in links

Created by Rui Carmo on 2007-01-11.
Published under the MIT license.
"""

import os, sys, logging

log = logging.getLogger()

from bs4 import BeautifulSoup
from controllers.wiki import WikiController as wc
from utils.core import Singleton
from plugins import plugin
import urlparse, re, time

@plugin
class Aliases:
    __metaclass__ = Singleton

    category  = 'markup'
    tags      = ['a']

    def __init__(self):
        self.aliases = wc.get_wiki_aliases()
        log.debug(self)


    def run(self, serial, tag, tagname, pagename, soup, request, response):
        try:
            link = tag['href']
        except KeyError:
            return True

        while True: # expand multiple aliases if required
            stack = [] # avoid loops
            try:
                alias = self.aliases[tag['href']]
                if alias not in stack:
                    stack.append(alias)
                    tag['href'] = alias
                else: # avoid loops
                    break
            except:
                break
        # this tag may need to be re-processed by another plugin
        return True
