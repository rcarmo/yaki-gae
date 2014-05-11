#!/usr/bin/env python
# encoding: utf-8
"""
Pygments syntax highligthing

Created by Rui Carmo on 2007-01-11.
Published under the MIT license.
"""

import os, sys, logging

log = logging.getLogger()

import urlparse, re, cgi, codecs
from bs4 import BeautifulSoup
from controllers.wiki import WikiController as wc
from gettext import gettext as _
from plugins import plugin
from pygments import highlight
from pygments.formatters import *
from pygments.lexers import *
from utils.core import Singleton

@plugin
class SyntaxHighlight:
    __metaclass__ = Singleton

    category = 'markup'
    tags     = ['pre']
    attrs    = ['syntax']


    def __init__(self):
        log.debug(self)
    

    def run(self, serial, tag, tagname, pagename, soup, request, response):
        try:
            source = tag['src']
            (schema,host,path,parameters,query,fragment) = urlparse.urlparse(source)
            if schema == 'cid' or wc.is_attachment(pagename,path):
                attachment = wc.get_attachment(pagename,path)
                if attachment:
                    buffer = attachment.data
                else:
                    tag.replaceWith(_('error_include_file'))
                    return False
            else:
                tag.replaceWith(_('error_reference_format'))
                return False
        except KeyError:
            buffer = u''.join(tag.find_all(text=re.compile('.+'))).strip()
        try:
            lexer = tag['syntax'].lower()
        except KeyError:
            lexer = 'text'

        # TODO: find a way to do inline styles with the correct color scheme when formatting for RSS
        if request is False: # we're formatting for RSS
            lexer = 'text'

        lexer = get_lexer_by_name(lexer)
        formatter = HtmlFormatter(linenos=False, cssclass='syntax')
        result = highlight(buffer, lexer, formatter)
        tag.replace_with(BeautifulSoup(result.strip()))

        return False # no other plugin should process this tag
