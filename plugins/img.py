#!/usr/bin/env python
# encoding: utf-8
"""
media.py

Created by Rui Carmo on 2007-01-11.
Published under the MIT license.
"""

import os, os.path, sys, logging, cgi, urlparse
from config import settings
from plugins import plugin
from utils.core import Singleton

log = logging.getLogger()

@plugin
class ImageWikiPlugin:
    __metaclass__ = Singleton

    category  = 'markup'
    tags      = ['img']


    def __init__(self):
        log.debug(self)


    def run(self, serial, tag, tagname, pagename, soup, request, response):
        log.debug("%s %s" % (pagename, tag))
        try:
            uri = tag['src']
            schema, _, path, _, _, _ = urlparse.urlparse(uri)
        except Exception, e:
            log.debug(e)
            return True

        if schema: # TODO: deal with cid: schema
            return True
            
        tag['src'] = unicode(cgi.escape(os.path.join(settings.wiki.media, pagename, path)))
        return False # no further processing required
