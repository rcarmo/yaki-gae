#!/usr/bin/env python
# encoding: utf-8
"""
Reformat links and page references

Created by Rui Carmo on 2006-09-12.
Published under the MIT license.
"""

import os
import logging

log = logging.getLogger()

import urlparse
import posixpath
from config import settings
from controllers.wiki import WikiController as wc
from utils.core import Singleton
from utils.timekit import time_since
from plugins import plugin

@plugin
class BaseURI:
    __metaclass__ = Singleton

    category = 'markup'
    tags     = ['a']

    schemas = {
        '*'      :{'title': u'unknown protocol linking to %(uri)s','class': u'generic'},
        'http'   :{'title': u'external link to %(uri)s','class': u'http'},
        'https'  :{'title': u'secure link to %(uri)s','class': u'https'},
        'ftp'    :{'title': u'file transfer link to %(uri)s','class': u'ftp'},
        'gopher' :{'title': u'(probably deprecated) link to %(uri)s','class': u'ftp'},
        'sftp'   :{'title': u'secure file transfer link to %(uri)s','class': u'ftp'},
        'ssh'    :{'title': u'secure shell session to %(uri)s','class': u'terminal'},
        'telnet' :{'title': u'(probably insecure) terminal session to %(uri)s','class': u'terminal'},
        'mailto' :{'title': u'e-mail to %(uri)s','class': u'mail'},
        'outlook':{'title': u'MAPI link to %(uri)s','class': u'mail'},
        'skype'  :{'title': u'call %(uri)s using Skype','class': u'call'},
        'sip'    :{'title': u'call %(uri)s using SIP','class': u'call'},
        'tel'    :{'title': u'call %(uri)s using SIP','class': u'call'},
        'callto' :{'title': u'call %(uri)s','class': u'call'},
        'cid'    :{'title': u'link to attached file %(uri)s', 'class': u'linkedfile'},
        'attach' :{'title': u'link to attached file %(uri)s', 'class': u'linkedfile'}
    }

    def __init__(self):
        log.debug(self)


    def run(self, serial, tag, tagname, pagename, soup, request, response):
        try:
            uri = tag['href']
        except KeyError:
            return True

        # Try to handle relative URIs
        if uri[0] == '.':
            uri = posixpath.normpath(os.path.join(pagename, uri))
        
        # Try to handle the uri as a schema/path pair
        schema = ''
        path = uri
        try:
            schema, path = uri.split(':',1)
        except:
            pass
        known = False

        if schema == '':
            alias = wc.resolve_alias(path)

            if alias and alias != path:
                path = tag['href'] = uri = alias

            if path in wc.get_page_mtimes().keys():
                known = True

        
        if(schema == ''):
            if wc.get_attachment(pagename, path):
                tag['href'] = unicode(settings.wiki.media + "/" + pagename + "/" + path)
                tag['title'] = self.schemas['attach']['title'] % {'uri':os.path.basename(path)}
                tag['class'] = self.schemas['attach']['class']
                return False

            if(known): # this is a known Wiki link, so there is no need to run it through more plugins
                if request is False:
                    # check for a direct outbound link
                    # TODO: check x-link handling
                    if path in wc.link_overrides:
                        uri = wc.link_overrides[path]
                        (schema,netloc,path,parameters,query,fragment) = urlparse.urlparse(uri)
                        tag['href'] = uri
                        tag['title'] = self.schemas[schema]['title'] % {'uri':uri}
                        tag['class'] = self.schemas[schema]['class']
                        return False
                tag['href'] = settings.wiki.base + '/' + uri
                tag['class'] = "wiki"
                try: # to use indexed metadata to annotate links
                    last = i.page_info[path]['last-modified']
                    tag['title'] = _('link_update_format') % (path,time_since(last))
                except:
                    tag['title'] = _('link_defined_notindexed_format') % path
            elif('#' == uri[0]):
                # this is an in-page anchor
                if request != False:
                    tag['href'] = request.path + uri
                tag['class'] = "anchor"
            else:
                if request is False:
                    # remove unknown wiki links for RSS feeds
                    tag.replace_with(tag.contents[0])
                    # format for online viewing
                try:
                    exists = tag['class']
                    return True #we're done here, but this tag may need handling elsewhere
                except:
                    tag['href'] = settings.wiki.base + '/' + uri
                    tag['class'] = "wikiunknown"
                    tag['title'] = _('link_undefined_format') % path

        elif(schema in self.schemas.keys()): # this is an external link, so reformat it
            tag['title'] = self.schemas[schema]['title'] % {'uri':uri}
            tag['class'] = self.schemas[schema]['class']
            #tag['target'] = '_blank'
        else: # assume this is an interwiki link (i.e., it seems to have a custom schema)
            tag['title'] =  _('link_interwiki_format') % uri
            tag['class'] = "interwiki"
            tag['target'] = '_blank'
            # Signal that this tag needs further processing
            return True
        # We're done
        return False
