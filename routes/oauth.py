#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, logging

log = logging.getLogger()

import time, hashlib, hmac, json, urllib, traceback
from bottle import post, get, abort, request, response, redirect
from config import settings
from google.appengine.api import memcache
from utils import Struct
from utils.urlkit import fetch
from models import DropboxToken

# TODO: proper auth, stronger key, etc.


@get('/dump')
def dump_key():
    return str(DropboxToken.get_by_id('default'))


@get('/authorize')
def begin_auth():
    h = hmac.new(settings.dropbox.app_secret)
    auth_url = "https://www.dropbox.com/1/oauth2/authorize"
    h.update(str(request.cookies))
    state = h.hexdigest()
    memcache.set("oauth:%s" % state, "session_id", 15)

    params = {
        "response_type": "code",
        "client_id"    : settings.dropbox.app_key,
        "redirect_uri" : request.url + '/confirmation',
        "state"        : state
    }
    log.info("%s" % params)
    redirect(auth_url + "?" + urllib.urlencode(params))


@get('/authorize/confirmation')
def get_token():
    log.info("%s" % dict(request.query))
    code = request.query.get('code','')
    if memcache.get("oauth:%s" % request.query.get('state','')) != "session_id":
        abort(500, "Invalid state")
    token_url = "https://api.dropbox.com/1/oauth2/token"

    log.info(request.url)
    result = Struct(fetch(token_url, urllib.urlencode({
        "code"         : code,
        "grant_type"   : "authorization_code",
        "client_id"    : settings.dropbox.app_key,
        "client_secret": settings.dropbox.app_secret,
        "redirect_uri" : "http://localhost:8080/authorize/confirmation"
    })))
    if result.status == 200:
        try:
            r = Struct(json.loads(result.data))
            r.id = "default"
            log.info(r)
            t = DropboxToken(**r)
            t.put()
        except:
            log.error("%s", traceback.format_exc())

    return result
