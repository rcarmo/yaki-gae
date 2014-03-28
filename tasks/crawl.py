import os, sys, logging, urllib, json, time
from datetime import datetime
from google.appengine.ext import deferred
from google.appengine.api import memcache
from models import DropboxToken, Page
from utils import Struct
from utils.urlkit import fetch
from utils.timekit import parse_date
from decorators import memoize
from yaki.store import parse_page
from email.utils import parsedate_tz
from config import settings
from controllers.wiki import *

log = logging.getLogger()

@memoize
def get_token():
    access_token = memcache.get("dropbox:access_token")
    if not access_token:
        try:
            token = DropboxToken.get_by_id('default')
            access_token = token.access_token
            memcache.set("dropbox:access_token", access_token)
        except:
            log.warn("No access token.")
    return access_token


def get_single_file(path):
    access_token = get_token()
    get_url = "https://api-content.dropbox.com/1/files/dropbox/%s?%s" % (path, urllib.urlencode({"access_token": access_token}))
    r = fetch(get_url)
    if r['status'] == 200:
        metadata = json.loads(r['x-dropbox-metadata'])
        try:
            headers, body, mime_type = parse_page(r['data'])
        except:
            log.error("Could not parse %s" % path)
            return
        # mtime is taken from cloud store metadata
        mtime = datetime.fromtimestamp(time.mktime((parsedate_tz(metadata['modified'])[:9])))
        ctime = headers.get('created', None)
        if ctime:
            ctime = datetime.fromtimestamp(parse_date(ctime))
        path = os.path.relpath(os.path.dirname(path), settings.dropbox.root_path)
        id   = path.lower()
        params = {
            "id"       : id,
            "path"     : path,
            "ctime"    : ctime,
            "ctime"    : ctime,
            "mtime"    : mtime,
            "title"    : headers.get('title', 'Untitled'),
            "tags"     : headers.get('tags', None),
            "body"     : body,
            "mime_type": mime_type,
            "headers"  : headers
        }
        p = Page(**params)
        p.put()
        memcache.set("meta:%s" % params['id'], params['headers'])

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

deferred.defer(get_files)

