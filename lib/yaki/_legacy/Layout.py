#!/usr/bin/env python
# encoding: utf-8
"""
Layout.py

Utility functions for formatting and layout (i.e., stuff that affects navigation, page look, etc.)

Created by Rui Carmo on 2006-09-23.
Published under the MIT license.
"""

import sys, os, string, hashlib
from yaki.Utils import *

def renderInfo(i18n, headers):
  """
  render page info
  """
  postinfo = i18n['created_on_format'] % (plainTime(i18n, headers['date']), headers['from'])
  if headers['date'] == headers['last-modified']:
    postinfo = postinfo + ", %s." % i18n['not_updated']
  elif headers['date'] < headers['last-modified']:
    postinfo = postinfo + ", %s." % (i18n['updated_ago_format'] % timeSince(i18n, headers['last-modified']))
  return postinfo  

def renderEntryMetaData(i18n, headers, short = True):
  """
  Render item metadata as a bulleted list
  
  Short format is for lists of items:
  * %(creation_date)s
  * %(tags)s
  
  Long format is for full page:
  * Created: %(creation_date)s
  * Updated:
  * Tags:
  """
  fields = ['created','updated','tags','references']
  items  = ['<li class="meta-%s">$%s</li>' % (x,x) for x in fields]
  format = '<b class="meta-color">%s</b><p class="meta-atom">%s</p>'
  if short == True:
    created = '<p class="meta-fuzzy"><b>%s</b></p>' % fuzzyTime(i18n, headers['date'])
    try:    
      tags = '<p class="meta-atom">%s</p>' % headers['tags'].lower()
    except:
      pass
  else:
    created = format % (i18n['Created'],plainTime(i18n, headers['date'], True))
    if headers['date'] != headers['last-modified']:
      updated = format % (i18n['Updated'],plainTime(i18n, headers['last-modified'], True))
    author = format % (i18n['By'],headers['from'])
    try:
      tags = format % (i18n['Tags'],headers['tags'].lower())
    except KeyError:
      # some entries might be untagged
      pass
  try:
    format = """
    <b class="meta-color">%s</b><br><a class="meta-atom" href="http://www.backtype.com/connect/%s/tweets">on backtype</a><br><div class="meta-atom delicious-placeholder" id="delicious-%s" template="%%d on delicious"></div>
    <div class="meta-atom delicious-placeholder" id="delicious-%s" template="(%%d alternate)"></div>
    """
    #format = """<b class="meta-color">%s</b>"""
    rawlink = headers['bookmark'].replace("http://","")
    backtypelink = rawlink.replace("/","%252f")
    permalink = headers['bookmark'] + u"#%s" % sanitizeTitle(headers['title'])
    #references = format % i18n['References']
    #    ,backtypelink,hashlib.md5(headers['bookmark']).hexdigest(),hashlib.md5(permalink).hexdigest())
  except KeyError:
    pass
  
  # perform replacement
  buffer = string.Template(''.join(items)).safe_substitute(locals())
  # remove unreplaced values
  for i in items:
    buffer = buffer.replace(i,'')
  return buffer

def pagetrail(i18n, trail, linkclass = "wiki"):
  """
  Build a breadcrumb trail for display atop the page
  """
  buffer = []
  for crumb in trail:
    buffer.append('<a class="%s" href="%s" title="%s %s">%s</a> : ' % (linkclass,crumb['link'],crumb['name'],
    i18n['updated_ago_format'] % timeSince(i18n, crumb['last-modified']), crumb['title']))
  return ''.join(buffer)[:-2]

def technoratiTags(headers,soup):
  """
  Build a div containing Technorati-style "tags" from the Wiki links and other page metadata
  """
  parse = ['keywords','categories','tags'] # headers to parse
  all = [] 
  links = soup.findAll('a',{'class':re.compile('^wiki.*')})
  for link in links:
    # add the last part of every link that doesn't end in a numeric string
    base = os.path.basename(link['href'].lower())
    if not re.match('^\d+',base) and base not in all:
      all.append(base)
  for header in parse:
    if header in headers:
      tags = [tag.strip().lower() for tag in headers[header].split(',')]
      for tag in tags:
        if tag not in all and tag != '':
          all.append(tag)
  if len(all) < 4: # be sparing
    return ''
  all.sort()
  buffer=[]
  for tag in all:
    buffer.append('<a href="http://technorati.com/tag/%s" rel="tag">%s</a>' % (tag, tag))
  return '<div class="technorati_tags" align="right"><small>Technorati Tags: %s</small></div>' % ', '.join(buffer)

def seeAlsoLinkTable(i18n, pagehash, width = 4, linkclass = "wiki", tableclass = "seealso", sort=True):
  """
  The world famous SeeAlso table
  """
  i = 0
  pages = pagehash.keys()
  if sort:
    pages.sort(lambda a, b: -cmp(pagehash[a]['last-modified'],pagehash[b]['last-modified']))
  count = len(pages)
  row = []
  buffer = []
  for link in pages:
    color = '#' + ('%02X' % (16*16 - (1.0*i/count)*64-1)) + ('%02X' % (16*16 - (1.0*i/count)*64-1)) + ('%02X' % (16*16 - (1.0*i/count)*64-1))
    rgba = 'rgba(%d,%d,%d,0.3)' % ((16*16 - (1.0*i/count)*64-1), (16*16 - (1.0*i/count)*64-1), (16*16 - (1.0*i/count)*64-1))
    td = '<a class="seealso %s" href="%s" title="%s %s">%s</a>' % (linkclass,link,pagehash[link]['name'],
          i18n['updated_ago_format'] % timeSince(i18n, pagehash[link]['last-modified']), pagehash[link]['title'])
    #row.append('<td width="%d%%" bgcolor="%s">%s</td>' % (100/width, color, td))
    row.append('<td width="%d%%" style="background-color:%s;">%s</td>' % (100/width, rgba, td))
    i = i + 1
    if 0 == i % width:
      buffer.append('<tr>%s</tr>' % ''.join(row))
      row = []
  buffer.append('<tr>%s</tr>' % ''.join(row))
  return '<table class="%s" width="100%%">%s</table>' % (tableclass,''.join(buffer))
