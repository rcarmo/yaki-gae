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

from decorators import timed, redis_cache, cache_control, cache_results, memoize

from controllers.wiki import WikiController

c = WikiController(settings)

@route('/')
@route(settings.wiki.base)
def root():
    log.debug(settings)
    redirect(settings.content.homepage)


@route(settings.wiki.base + '/<page:path>')
@timed
@cache_results(settings.cache.worker_timeout)
@redis_cache(c.redis, 'html', settings.cache.redis_timeout)
@cache_control(settings.cache.cache_control)
@view('wiki')
@render(settings.wiki.markup_overrides)
def wiki(page):
    """Render a wiki page"""

    # should fallback to index/aliases/levensheim
    try:
        result = c.get_page(page)
    except Exception, e:
        original = c.resolve_alias(page)
        if original:
            redirect("%s/%s" % (settings.wiki.base, original))
        close = c.get_close_matches_for_page(page)
        if len(close):
            redirect("%s/%s" % (settings.wiki.base, close[0]))
            return
        abort(404, "Page not found")
    return result
    

@route(settings.wiki.media + '/<item:path>')
@timed
@cache_control(settings.cache.cache_control)
def media_asset(item):
    """Return page attachments"""

    return static_file(item, root=path_for(settings.content.path))
