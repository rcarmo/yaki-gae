#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2012, Rui Carmo
Description: Shared configuration data
License: MIT (see LICENSE.md for details)
"""

import os, sys, platform, logging
from utils import Struct, get_config, path_for, tb

settings = Struct({
    "loglevel": logging.DEBUG,
    "content": {
        "path": "data/main",
    },
    "cache": {
        "#": "In-worker memory cache",
        "worker_timeout": 60,
        "#": "memcache timeout",
        "cache_timeout": 300,
        "#":"HTTP Cache control",
        "cache_control": 3600
    },
    "theme": "ink",
    "wiki": {
        "#"       : "Paths",
        "base"    : "/space",
        "home"    : "HomePage",
        "media"   : "/media",
        "plugins": {
        },
        "markup_overrides": { "text/plain": "text/x-textile" }
    },
    "dropbox": {
        "preload": {
            "meta" : 100,
            "blog" : 100,
            "links": 100
        },
        "app_key": "********",
        "app_secret": "********",
        "root_path": ""
    }
})

try:
    from _config import overrides
    settings.update(overrides)
    settings = Struct(settings)
except:
    pass


# memcache keys for shared metadata
NS_PAGES          = 'pages'
NS_ALIASES        = 'aliases'
NS_PAGE_METADATA  = 'page_metadata'
NS_TOKEN          = 'token'
NS_IDS            = 'ids'
NS_CLOUD_METADATA = 'cloud_metadata'

# Characters used as separators/aliasing generation
ALIASING_CHARS = ['','.','-','_']

BASE_TYPES={
    "txt"     : "text/plain",
    "html"    : "text/html",
    "htm"     : "text/html",
    "md"      : "text/x-markdown",
    "mkd"     : "text/x-markdown",
    "mkdn"    : "text/x-markdown",
    "markdown": "text/x-markdown",
    "textile" : "text/x-textile"
}

BASE_FILENAMES=["index.%s" % x for x in BASE_TYPES.keys()]
BASE_PAGE = """From: %(author)s
Date: %(date)s
Content-Type: %(markup)s
Content-Encoding: utf-8
Title: %(title)s
Keywords: %(keywords)s
Categories: %(categories)s
Tags: %(tags)s
%(_headers)s

%(content)s
"""

IGNORED_FOLDERS = ['CVS', '.hg', '.svn', '.git', '.AppleDouble']
