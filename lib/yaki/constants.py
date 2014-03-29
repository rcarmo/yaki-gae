# memcache keys for shared metadata
META_PAGES   = 'meta:pages'
META_ALIASES = 'meta:aliases'
META_MTIMES  = 'meta:mtimes'
META_RECENT  = 'meta:recent_changes'
META_HEADERS = 'meta:headers'
META_TOKEN   = 'meta:token'

# Characters used as separators/aliasing generation
ALIASING_CHARS = ['','.','-','_']

BASE_TYPES={
    "txt"     : "text/plain",
    "html"    : "text/html",
    "htm"     : "text/html",
    "md"      : "text/x-markdown",
    "mkd"     : "text/x-markdown",
    "mkdn"    : "text/x-markdown",
    "markdown": "text/x-markdown",
    "textile" : "text/x-textile"
}

BASE_FILENAMES=["index.%s" % x for x in BASE_TYPES.keys()]
BASE_PAGE = """From: %(author)s
Date: %(date)s
Content-Type: %(markup)s
Content-Encoding: utf-8
Title: %(title)s
Keywords: %(keywords)s
Categories: %(categories)s
Tags: %(tags)s
%(_headers)s

%(content)s
"""

IGNORED_FOLDERS = ['CVS', '.hg', '.svn', '.git', '.AppleDouble']
