import json
import os
import urllib

from config import settings
from controllers.wiki import *
from google.appengine.ext import deferred
import logging
from utils.urlkit import fetch

log = logging.getLogger()



def get_files():
    log.info("starting run")
    access_token = get_token()
    if not access_token:
        return
    lock = memcache.get("tasks:dropbox")
    if not lock:
        memcache.set("tasks:dropbox", "unique_id_placeholder", 15)
    else:
        return

    search_url = "https://api.dropbox.com/1/search/dropbox?%s" % urllib.urlencode({
        "query": "index.txt",
        "access_token": access_token
    })
    res = fetch(search_url)
    data = json.loads(res['data'])
    known = get_page_mtimes()
    for f in data:
        log.info(f)
        path = os.path.relpath(os.path.dirname(f['path']), settings.dropbox.root_path).lower()
        if path in known.keys():
            # TODO: check mtime here as well
            continue
        deferred.defer(get_single_file, f['path'])

#deferred.defer(get_files)

