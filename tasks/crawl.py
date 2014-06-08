import json
import os
import urllib

from config import settings, NS_BATCH
from controllers.store import CloudStoreController
from controllers.wiki import WikiController as wc
from google.appengine.ext import deferred
from google.appengine.api import memcache
from bottle import get
import logging

log = logging.getLogger()

store = CloudStoreController()

QUEUED_KEY = "queued"

@get("/_ah/warmup")
def start():
    deferred.defer(scan_preloads, ["meta"])


def scan_preloads(prefixes):
    if not prefixes:
        prefixes = settings.dropbox.preload.keys();
    for prefix in prefixes:
        queued = memcache.get(prefix, namespace=NS_BATCH)
        if not queued:
            memcache.set(prefix, True, namespace=NS_BATCH)
        else:
            return
        pages = store.scan_subtree(prefix)
        pages.sort(reverse=True)
        deferred.defer(preload_pages, pages, prefix)

def preload_pages(pages, prefix):
    for p in pages:
        log.warn(p)
        wc.get_page(p["page_name"])
    memcache.delete(prefix, namespace=NS_BATCH)

