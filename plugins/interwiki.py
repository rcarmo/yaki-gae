#!/usr/bin/env python
# encoding: utf-8
"""
Reformat custom schemas as references to exernal Wikis/sites

Created by Rui Carmo on 2007-01-11.
Published under the MIT license.
"""

import logging

log = logging.getLogger()

import urlparse
from controllers.wiki import WikiController as wc
from utils.core import Singleton
from plugins import plugin

@plugin
class InterWiki:
    __metaclass__ = Singleton

    category  = 'markup'
    tags      = ['a']
    schemas   = {}

    def __init__(self):
        self.schemas = wc.get_interwiki_map()
        log.debug(self)


    def run(self, serial, tag, tagname, pagename, soup, request, response):
        try:
            uri = tag['href']
        except KeyError:
            return True
        try:      
            (schema, link) = uri.split(':',1)
        except ValueError:
            return False

        schema = schema.lower()
        tag['rel'] = uri

        if schema in self.schemas.keys():
            if '%s' in self.schemas[schema]:
                try:
                    uri = self.schemas[schema] % link
                except:
                    log.error("Error in processing Interwiki link (%s,%s,%s)" % (schema, link, self.schemas[schema]))
                    uri = self.schemas[schema] + link
            else:
                uri = self.schemas[schema] + link
            (schema,netloc,path,parameters,query,fragment) = urlparse.urlparse(uri)
            tag['href'] = uri
            tag['title'] = "link to %s on %s" % (link, netloc)
            tag['class'] = "interwiki"
            # this tag does not need to be re-processed
            return False
