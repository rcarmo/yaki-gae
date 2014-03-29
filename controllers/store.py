#!/usr/bin/env python
# encoding: utf-8
"""
Store.py

Created by Rui Carmo on 2014-03-29.
Published under the MIT license.
"""

import os, sys, logging, urllib
from config import settings
from datetime import datetime
from decorators import *
from email.utils import parsedate_tz
from google.appengine.api import memcache
from yaki.store import parse_page
from models import DropboxToken, Page
from utils.urlkit import fetch
from utils.timekit import parse_date
from utils import Struct
from yaki.constants import *

log = logging.getLogger()

_urls = Struct({
    "files": "https://api-content.dropbox.com/1/files/dropbox/%s?%s",
    "auth" : "https://www.dropbox.com/1/oauth2/authorize",
    "token": "https://api.dropbox.com/1/oauth2/token"
})


def parse_dropbox_date(date):
    return datetime.fromtimestamp(time.mktime((parsedate_tz(date)[:9])))


def relative_path(path):
    os.path.relpath(os.path.dirname(path), settings.dropbox.root_path)


class CloudStoreController:

    def __init__(self, token = None):
        if not token:
            token = CloudStoreController.get_token()
        self.token = token


    @staticmethod
    @memoize_function
    def get_token():
        access_token = memcache.get(META_TOKEN)
        if not access_token:
            log.warn("No access token.")
            try:
                token = DropboxToken.get_by_id('default')
                access_token = token.access_token
                memcache.set(META_TOKEN, access_token)
            except Exception as e:
                log.error("Unable to retrieve token from NDB: %s" % e)

        return access_token


    def get_page(self, page):
        """Return a single page from the cloud store, storing it locally"""

        if not self.token:
            log.debug("No token")
            return None
        
        get_url = _urls.files % (os.path.normpath(os.path.join(settings.dropbox.root_path, page, "index.txt")), urllib.urlencode({"access_token": self.token}))
        log.debug(get_url)
        r = fetch(get_url)

        if r['status'] == 200:
            metadata = json.loads(r['x-dropbox-metadata'])
            try:
                headers, body, mime_type = parse_page(r['data'])
            except Exception as e:
                log.error("Could not parse %s: %s" % (path, e))
                return None

            # mtime is taken from cloud store metadata
            mtime = parse_dropbox_date(metadata['modified'])
            ctime = headers.get('created', None)
            if ctime:
                ctime = datetime.fromtimestamp(parse_date(ctime))

            id   = page.lower()
            params = {
                "id"       : id,
                "path"     : page,
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
            return p
        return None
