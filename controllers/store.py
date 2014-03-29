#!/usr/bin/env python
# encoding: utf-8
"""
Store.py

Created by Rui Carmo on 2014-03-29.
Published under the MIT license.
"""

import os
import logging
from google.appengine.api import memcache
from utils.urlkit import fetch
from utils.timekit import parse_date
from yaki.store import parse_page
from email.utils import parsedate_tz
from decorators import memoize_method as memoize
from utils import Struct

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


def parse_dropbox_date(date):
    return datetime.fromtimestamp(time.mktime((parsedate_tz(date)[:9])))


def relative_path(path):
    os.path.relpath(os.path.dirname(path), settings.dropbox.root_path)


class CloudStoreController:

    def __init__(self, token):
        self.token = token
        self.urls = Struct({
            "files": "https://api-content.dropbox.com/1/files/dropbox/%s?%s"
        })


    def get_single_page(self, path):
        if not self.token:
            return None
        
        get_url = self.urls.files % (path, urllib.urlencode({"access_token": self.token}))
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

            path = relative_path(path)
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
            return p
        return None
