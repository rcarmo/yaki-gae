from google.appengine.ext.ndb import Model, StringProperty, DateTimeProperty, JsonProperty, TextProperty, BlobProperty

class DropboxToken(Model):
    access_token = StringProperty()
    token_type   = StringProperty()
    uid          = StringProperty()


class Page(Model):
    mtime     = DateTimeProperty()
    ctime     = DateTimeProperty()
    path      = StringProperty()   # for later writeback to cloud store
    title     = StringProperty()   # for indexing
    tags      = StringProperty()   # tags, for indexing
    headers   = JsonProperty()     # all other headers, preserved for posterity
    body      = TextProperty()     # raw markup
    plaintext = TextProperty()     # plaintext, for indexing
    mime_type = TextProperty()


class Attachment(Model):
    mtime     = DateTimeProperty()
    path      = StringProperty()   # for later writeback to cloud store
    filename  = StringProperty()   # for later writeback to cloud store
    data      = BlobProperty()     # raw data
    mime_type = TextProperty()

