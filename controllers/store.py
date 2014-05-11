#!/usr/bin/env python
# encoding: utf-8
"""
store.py

Created by Rui Carmo on 2014-03-29.
Published under the MIT license.
"""

import os, sys, logging, urllib, json, time
from config import settings, BASE_TYPES, NS_TOKEN, NS_CLOUD_METADATA, NS_PAGE_METADATA
from datetime import datetime
from email.utils import parsedate_tz
from google.appengine.api import memcache
from models import DropboxToken, Page, Attachment
from utils import Struct
from utils.urlkit import fetch
from utils.timekit import parse_date
from utils.decorators import memoize
from utils.markup import parse_rfc822

log = logging.getLogger()

TOKEN_KEY = "default"

_urls = Struct({
    "files"   : "https://api-content.dropbox.com/1/files/dropbox/%s?%s",
    "metadata": "https://api.dropbox.com/1/metadata/dropbox/%s?%s",
    "auth"    : "https://www.dropbox.com/1/oauth2/authorize",
    "token"   : "https://api.dropbox.com/1/oauth2/token"
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
        self.valid_indexes = ["index." + ext for ext in BASE_TYPES.keys()]


    @staticmethod
    @memoize
    def get_token():
        access_token = memcache.get(TOKEN_KEY, namespace=NS_TOKEN)
        if not access_token:
            log.warn("Access token not in memcache")
            try:
                token = DropboxToken.get_by_id(TOKEN_KEY)
                access_token = token.access_token
                memcache.set(TOKEN_KEY, access_token, namespace=NS_TOKEN)
                log.info("Access token in memcache")
            except Exception as e:
                log.error("Unable to retrieve token from NDB: %s" % e)

        return access_token


    @memoize
    def get_metadata(self, path):
        if not self.token:
            log.debug("No token")
            return None

        metadata = memcache.get(path, namespace=NS_CLOUD_METADATA)
        params = {"access_token": self.token}
        if metadata:
            params["hash"] = metadata["hash"]
        metadata_url = _urls.metadata % (os.path.normpath(os.path.join(settings.dropbox.root_path, path)),
                                         urllib.urlencode(params))
        log.debug(metadata_url)
        r = fetch(metadata_url)
        
        if r['status'] == 200:
            metadata = json.loads(r["data"])
            memcache.set(path, metadata, namespace=NS_CLOUD_METADATA)

        return metadata # also valid for 304/404 return values


    @memoize
    def get_page(self, page):
        """Return a single page from the cloud store, storing it locally"""

        if not self.token:
            log.debug("No token")
            return None

        # get the folder contents
        metadata = self.get_metadata(page)
        if not metadata:
            return None

        markup = None
        for i in metadata['contents']:
            if not i['is_dir']:
                if os.path.basename(i['path']) in self.valid_indexes:
                    markup = i['path']
                    break

        if not markup:
            return None
        
        get_url = _urls.files % (markup, urllib.urlencode({"access_token": self.token}))
        log.debug(get_url)
        r = fetch(get_url)

        if r['status'] == 200:
            metadata = json.loads(r['x-dropbox-metadata'])
            try:
                headers, body, mime_type = parse_rfc822(r['data'])
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
                "mtime"    : mtime,
                "title"    : headers.get('title', 'Untitled'),
                "tags"     : headers.get('tags', None),
                "body"     : body,
                "mime_type": mime_type,
                "headers"  : headers
            }
            p = Page(**params)
            p.put()
            memcache.set(params['id'], params['headers'], namespace=NS_PAGE_METADATA)
            return p
        return None


    @memoize
    def is_attachment(self, page, filename):
        """Check if a given file exists inside a page folder"""

        if not self.token:
            log.debug("No token")
            return None

        # get the folder contents
        metadata = self.get_metadata(page)
        if not metadata:
            return None

        target = None
        for i in metadata['contents']:
            if not i['is_dir']:
                if os.path.basename(i['path']) == filename:
                    target = i['path']
                    break

        if not target:
            return False
        return True


    @memoize
    def get_attachment(self, page, filename):
        """Return an attachment from the cloud store, storing it locally"""

        if not self.token:
            log.debug("No token")
            return None

        # get the folder contents
        metadata = self.get_metadata(page)
        if not metadata:
            return None

        target = None
        for i in metadata['contents']:
            if not i['is_dir']:
                if os.path.basename(i['path']) == filename:
                    target = i['path']
                    break

        if not target:
            return None

        get_url = _urls.files % (target, urllib.urlencode({"access_token": self.token}))
        log.debug(get_url)
        r = fetch(get_url)

        if r['status'] == 200:
            metadata = json.loads(r['x-dropbox-metadata'])

            # mtime is taken from cloud store metadata
            mtime = parse_dropbox_date(metadata['modified'])

            id   = os.path.join(page.lower(),filename.lower())
            params = {
                "id"       : id,
                "path"     : page,
                "filename" : filename,
                "mtime"    : mtime,
                "data"     : r['data'],
                "mime_type": metadata['mime_type'],
            }
            a = Attachment(**params)
            a.put()
            return a
        return None

