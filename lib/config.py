#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2012, Rui Carmo
Description: Shared configuration data
License: MIT (see LICENSE.md for details)
"""

import os, sys, platform, logging.config
from utils import Struct, get_config, path_for, tb

settings = Struct({
    "content": {
        "path": "data/main"
    },
    "cache": {
        "#": "In-worker memory cache",
        "worker_timeout": 60,
        "#": "Redis cache timeout",
        "redis_timeout": 300,
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
    }
})