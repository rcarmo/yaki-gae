#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
wiki.py
"""

import os, sys, logging

log = logging.getLogger()

from bottle import route, redirect, view, static_file, abort
from config import settings

from utils import path_for
from yaki import Store
from yaki.decorators import render

from decorators import timed, cache_memory, cache_control, cache_results, memoize

from controllers.wiki import *

@route('/')
@route(settings.wiki.base)
def root():
    log.debug(settings)
    redirect(os.path.join(settings.wiki.base,settings.wiki.home))


@route(settings.wiki.base + '/<page:path>')
@timed
@cache_results(settings.cache.worker_timeout)
@cache_memory('html', settings.cache.cache_timeout)
@cache_control(settings.cache.cache_control)
@view('wiki')
@render(settings.wiki.markup_overrides)
def wiki(page):
    """Render a wiki page"""

    # should fallback to index/aliases/levensheim
    try:
        p = get_page(page)
        return {'headers': p.headers, 'data': p.body, 'content-type': p.mime_type}
    except Exception, e:
        original = resolve_alias(page)
        if original:
            redirect("%s/%s" % (settings.wiki.base, original))
        close = get_close_matches_for_page(page)
        log.info("Close matches: %s" % close)
        if len(close):
            redirect("%s/%s" % (settings.wiki.base, close[0]))
            return
        abort(404, "Page not found")
    return result


@route(settings.wiki.media + '/<item:path>')
@timed
@cache_memory('media', settings.cache.cache_timeout)
@cache_control(settings.cache.cache_control)
def media_asset(item):
    """Return page attachments"""

    return static_file(item, root=path_for(settings.content.path))
