#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
wiki.py
"""

import os, sys, logging

log = logging.getLogger()

from bottle import request, response, get, redirect, view, static_file, abort
from config import settings
from google.appengine.api import memcache
from .decorators import render

from utils import path_for
from utils.decorators import timed, cache_memory, cache_control, cache_results

from controllers.wiki import WikiController
from controllers.store import CloudStoreController
from controllers.ids import IDSController

w = WikiController()
s = CloudStoreController()
ids = IDSController()


@get('/')
@get(settings.wiki.base)
def root():
    log.debug(settings)
    redirect(os.path.join(settings.wiki.base,settings.wiki.home))


@get(settings.wiki.base + '/<page:path>')
@timed
@cache_results(settings.cache.worker_timeout)
@cache_memory('html', settings.cache.cache_timeout)
@cache_control(settings.cache.cache_control)
@view('wiki')
@render(settings.wiki.markup_overrides)
def wiki(page):
    """Render a wiki page"""
    if ids.is_suspicious(request):
        abort(403, "Temporarily blocked due to suspicious activity")

    # should fallback to index/aliases/levensheim
    p = w.get_page(page)
    if not p:
        log.debug("Attempting to retrieve %s from cloud store" % page)
        p = s.get_page(page)
    try:
        return {'headers': p.headers, 'data': p.body, 'content-type': p.mime_type}
    except Exception as e:
        log.debug("Attempting to resolve aliases for %s" % page)
        original = w.resolve_alias(page)
        if original:
            redirect("%s/%s" % (settings.wiki.base, original))
        log.debug("Attempting to find close matches for %s" % page)
        close = w.get_close_matches_for_page(page)
        if len(close):
            redirect("%s/%s" % (settings.wiki.base, close[0]))
        ids.flag(request)
        abort(404, "Page not found")
    return result


@get(settings.wiki.media + '/<item:path>')
@timed
@cache_memory('media', settings.cache.cache_timeout)
@cache_control(settings.cache.cache_control)
def media_asset(item):
    """Return page attachments"""

    a = w.get_attachment(os.path.dirname(item), os.path.basename(item))
    if not a:
        a = s.get_attachment(os.path.dirname(item), os.path.basename(item))
        if not a:
            abort(404, "File not found")
            
    response.content_type = a.mime_type
    return a.data
