[![Stories in Ready](https://badge.waffle.io/rcarmo/yaki-gae.png?label=ready&title=Ready)](https://waffle.io/rcarmo/yaki-gae)

yaki-gae
========

An experimental version of Yaki for Google App Engine.

## Why?

I initially decided to do this as a quick and dirty test to see whether it would be viable to use the NoSQL datastore for raw markup and very basic metadata, and ended up realizing that this would be a great chance to finish [refactoring Yaki][tng] as an MVC/WSGI app with a well-defined set of constraints regarding storage, task queues, etc.

That and try out a PaaS, which I've never really done (I favor sysadmining my own machines, but there's only so much time in the world). [GAE][gae] isn't perfect, but it's well documented and a good fit for [my usual development pattern][dp].

So, among other things, this version aimed to do away (almost completely) with the `yaki` package and standardize the internals a bit more.

However, after finishing that, I realized that it was prohibitively expensive to crawl the remote data store for changes, so I decided to put this on ice, strip away the GAE bits, and move development to a private Bitbucket repo.

This is pretty usable on its own, provided you're willing to write a way to manage the content store rather than sync it with a cloud store service -- it's certainly feasible to run a self-contained blog engine atop GAE using this as a basis, but a filesystem is just more convenient for me.

## Architecture

The base premise of [Yaki][y] is that all my content is stored as flat files -- rather than generate a static site out of five thousand files and keep them all around, I'd rather have [Yaki][y] keep track of metadata and render pages as necessary. 

In order to work inside [App Engine][gae], I tossed out direct filesystem access and replaced it with [Dropbox][db] (soon [MEO Cloud][mc]) API access -- so [Yaki][y] is, in effect, acting as a caching proxy to the API, storing pages in the datastore as users navigate the site.

## Constraints

One of the main constraints I have is that I need to support multiple markup formats (such as [Textile][tt], which is still superior to [Markdown][md] for a number of use cases).

Were it not for that (and the superior feature sets of most [Python][py] markup renderers) and I would probably be rewriting this in [Go].

## Coding Style

Given that I'm re-using a fair amount of old code, the coding style is uneven and there is an uneasy mix of singletons, static classes, functional code, rather excessive memoization, etc. One of the priorities here was to minimize datastore and cloud store requests.

[gae]: https://cloud.google.com/products/app-engine/
[db]: http://www.dropbox.com
[mc]: http://meocloud.pt
[ttom]: http://the.taoofmac.com
[y]: https://github.com/rcarmo/Yaki
[tng]: https://github.com/rcarmo/yaki-tng
[2822]: http://www.ietf.org/rfc/rfc2822.txt
[tt]: http://en.wikipedia.org/wiki/Textile_(markup_language)
[md]: http://en.wikipedia.org/wiki/Markdown
[py]: http://www.python.org
[go]: http://www.golang.org
[dp]: http://the.taoofmac.com/space/blog/2013/08/11/2300
