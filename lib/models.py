from google.appengine.ext import ndb

class DropboxToken(ndb.Model):
    access_token = ndb.StringProperty()
    token_type   = ndb.StringProperty()
    uid          = ndb.StringProperty()


class Page(ndb.Model):
    mtime     = ndb.DateTimeProperty()
    ctime     = ndb.DateTimeProperty()
    path      = ndb.StringProperty()   # for later writeback to cloud store
    title     = ndb.StringProperty()   # for indexing
    tags      = ndb.StringProperty()   # tags, for indexing
    headers   = ndb.JsonProperty()     # all other headers, preserved for posterity
    body      = ndb.TextProperty()     # raw markup
    plaintext = ndb.TextProperty()     # plaintext, for indexing
    mime_type = ndb.TextProperty()
