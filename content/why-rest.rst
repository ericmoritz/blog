Why REST?
#########
:date: 2010-10-06 01:42:52
:tags: REST, programming

Preface
--------
I have to say before you read this that I only have a theoritical
understanding of how a web service benefits for being RESTful.  Most
of the topics I have explored are actually explained in Roy Fieldings
`section on REST <http://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm>`_

In the future, I would like to explore and test the assumptions I have
made and come up with evidence of thier truthiness.



Why REST?
----------
RESTful web services have been talked about ad-nauseum for a decade.
In fact, REST felt like such a hipster's architecture that I pawned it
off as a fad and waited this long to only begin to understand it.
Prior to understanding a technology, I have to ask myself, "What
motivates people to use this technology over others?".  I think I may
have figured it out.

The key to benefit of REST is the fact that it lives within the
confines of HTTP/1.1. Within this world a RESTful web service benefits
from all the solutions already solved by the HTTP/1.1 spec. A brief
list of standard HTTP solutions that benefit RESTful web services are
a uniform interface, caching, asynchronous processing, and security.

A RESTful web service, in particular a resource oriented RESTful web
service, starts with a list of URLs that resources live on.
Resources are basically entities that live inside your application.  A
few examples could be a Blog entry, a Forum post, a page hit.
These entities don't have to map directly to your applications
database, they could merely be logical resources, such as a page hit.

When a client sends a resource to the server, the server will act on
that resource.  If it's a blog post, it would store the blog post. If
it's a logical resource like a page hit, the service would simply 
increment a counter somewhere.

Each resource has a limited number of verbs that can be done to that
resource.  The primary verbs are GET, POST, PUT and DELETE.  There are
inherent restrictions to what these verbs can do. GET never writes on
the server; whereas POST/PUT and DELETE always write.  Due to these
restrictions you can do some simple optimizations to your web service
to help it scale.

One of the limitations of SQL is replication and it is a hard problem
to solve.  In the most basic SQL replication architecture you have a
master server and a number of slave servers.  The master is written to
and the slaves are read from.  If your web service abides by the
HTTP/1.1 read/write restrictions based on the HTTP method, you can
easily route your database connection to your read slaves on GET and
your write master on POST, PUT, and DELETE.  This would be a more
complex solution in a GET based RPC service because every GET to a URL
could potentially write to the server.  A special router would have to
be written that have to know which procedure writes and which reads.
You can gain the same benefit with a custom RPC if you support POST
and limit your writes to just POST methods.

Another problem already solved by HTTP/1.1 is caching.  If you can
assume that a GET will always read and if you know when resource was
last changed, you can send the Last-Modified header with the
response. The client is then responsible for caching the content and
storing the Last-Modified date.  The client will now send the
If-Modified-Since header with each new request for that resource.  If
the resource has not been modified, the service will respond with a
"304 Not Modified" with no information.  The service is done.  All it
had to do is check if the resource has been modified since the client
last requested the content.  There are other cache headers such as
ETag and Cache-Expires, but I think Last-Modified is the simplest to
support.

The beauty of your web service supporting HTTP/1.1 caching is that
browsers already support it.  All AJAX calls to your service will only
return content if it's changed.  This makes every web browser out
there a replicated node for your service!  Instant horizontal scaling,
how's that feel?

However, you should not trust clients to cache your content, so you
should implement a server side caching layer in front of your web
service.  Varnish can sit in front of your service and serve all
cached content from memory. If you want to get really distributed, you
can load balance an expandable pool of nginx servers caching content
into a expandable pool of memcached servers that sit in front of your
web service.  If you always send a Last-Modified header, these super
fast asynchronous servers can serve up cached content until the
content is changed.

Sometimes it takes a long time to process a write and one solution is
to make that request asynchronous.  HTTP/1.1 has a standard response
code for supporting this, "202 Accepted".  This status code tells the
client, "I have your content, I will process it when I can".  This
allows you to respond in a timely matter.  The client knows that it's
write is being worked on.  Using a "202 Accepted" response in
conjunction with a request with a Last-Modified header allows the
client to poll the service for new content and the service will only
work as hard as it has to get the Last-Modified value.

An example of asynchronous processing might be implemented in a search
engine.  Let's say your search engine indexer is time consuming.  It
parses out keywords, does named entity extraction, and searches for
addresses to geocode.  This would be a lot of things to do in one HTTP
request. Don't worry HTTP/1.1 lets you tell the client you've queue it
up.  When a new piece of content needs to be index, the service would
queue the document and respond with a "202 Accepted" and the client
can move on. Eventually the search engine will index the content and
the new content will show up in the search engine.

For security, HTTP/1.1 defines support username/password based
authentication and SSL encryption so any web service has the ability
to use these technologies.

A RESTful web service also has the benefit of having a limited number
of actions that can act on a resource.  This simplifies authorization
and access control tremendously.  If you want to restrict a client
from writing to a resource you can forbid a client from doing a PUT,
POST or DELETE on the URL.  You can even set up an OAuth based system
external to the web service that allows users to grant authorization
to external applications to do things on their behalf.

For instance, a blogging system's OAuth based system could define a
permission of "Add/Update blog entries", and this permission would allow
`PUT /blog/entry/:slug` resources and `POST /blog/entry/`.  The web service
does not have to worry about authorizing access to that resource because
a layer between the client and the service handles that for it.

These are small number of solutions that HTTP/1.1 provides web
services if they abide by a RESTful resource oriented architecture and
make use of the functionality that HTTP/1.1 has already defined for
you.  

There are a number of off the shelf products that can benefit RESTful
web services such as caching servers, load balancers, and
authentication frameworks. These solutions would have to be
implemented within your web service or within your service's
overloaded HTTP protocol. One example of this reimplementation is
SOAP's WS-* suite of specifications.  Reinventing the wheel is rampant
in the web development world and this is mainly due to ignorance of
existing solutions.  There is no reason to keep reimplementing
functionality solved by HTTP on top of HTTP.
