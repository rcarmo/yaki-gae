from google.appengine.ext import ndb

class Page(ndb.Model):

    @classmethod
    def get(cls, key):
        return cls.get_by_key_name(key)

    @classmethod
    def set(cls, key, val):
        entity = cls(key_name = key,
                     mtime    = mtime,
                     ctime    = ctime,
                     title    = title,
                     tags     = tags,
                     headers  = headers,
                     body     = body)
        entity.put()
        return entity

    mtime   = ndb.DateTimeProperty()
    ctime   = ndb.DateTimeProperty()
    title   = ndb.StringProperty()   # for indexing
    tags    = ndb.StringProperty()   # tags, for indexing
    headers = ndb.JsonProperty()     # all other headers, preserved for posterity
    body    = ndb.TextProperty()     # raw markup
