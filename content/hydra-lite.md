Title: Hydra lite
Date: 2015-05-01
Tags: linked-data, hydra, json-ld

For the past year or so I have been working with JSON-LD and Hydra. I
have been an internal zealot for using JSON-LD and Hydra for building
hypermedia services but I have been met with indifference for
"simpler" formats such as HAL.

I think this preference for HAL is due to the cognitive baggage of
RDF that comes with JSON-LD. For any developer being introduced to
JSON-LD+Hydra, Linked Data and RDF is something they may have heard of
in passing or never heard of. So for them, learning Hydra means
having to learn all about vast world of RDF vocabularies, of which
there are almost 500 indexed at [Linked Open
Vocabularies](http://lov.okfn.org/dataset/lov). That is a lot to
research for someone who just wants to build their MVP microservice
yesterday.

So what I want to do is introduce a usage of Hydra that is light on
cognitive baggage. This light usage of Hydra doesn't introduce the
entire universe of Linked Data for those that gravitate to HAL for
it's "simplicity" and I'll show you why I put "simplicity" in quotes
because JSON-LD is a much simpler and natural format for Hypermedia
enabled JSON than HAL.

## Rules of Hydra lite

These are the simple rules of Hydra lite:

1. @context is optional
2. Use duck typing for JSON only clients
3. Use consistent JSON data types

### @context is optional

The `@context` of a JSON-LD resource is great.  I love using it to
document my services.  However to match the cognitive weight of HAL
`@context` brings the entire world of Linked Data to hypermedia
services that can be daunting for developers being introduced to
Hydra.

### Use duck typing for JSON only clients

Given that most, if not all, clients consuming these services will by
JSON-LD naive, we have to enable duck typing allow those clients to
detect linked resources (more on this below).

## Resource

Lets start with what a resource is in hypermedia.  A
resource is simply an object with keys and values:

```js
{
   "name": "JSON-LD/Hydra lite",
   "url": "http://eric.themoritzfamily.com/hydra-lite.html"
}
```


## Links

With HAL, to link to another resource you use the special `_links`
property

```js
{
   "name": "JSON-LD/Hydra lite",
   "url": "http://eric.themoritzfamily.com/hydra-lite.html",
   "_links": {
      "self": "/entries/hydra-lite.json",
      "up": "/"
   }
}
```

If we want to provide additional data for the `up` resource, we have
to move that to the `_embedded` field:

```js
{
  "name": "JSON-LD/Hydra lite",
  "url": "http://eric.themoritzfamily.com/hydra-lite.html",
  "_link": {
    "self": "/entries/hydra-lite.json"
  },
  "_embedded": {
    "up": {
      "_links": {
        "self": "/"
      },
      "name": "Eric Moritz' Blog"
    }
  }
}
```

In Hydra lite this a lot simpler and JSON native:

```js
{
   "@id": "/entries/hydra-lite.json",
   "name": "JSON-LD/Hydra lite",
   "url": "http://eric.themoritzfamily.com/hydra-lite.html",
   "up": {"@id": "/"}
}
```

And the "embedded" version:

```js
{
   "@id": "/entries/hydra-lite.json",
   "name": "JSON-LD/Hydra lite",
   "url": "http://eric.themoritzfamily.com/hydra-lite.html",
   "up": {
      "@id": "/",
      "name": "Eric Moritz' blog"
   }
}
```

I think it is self evident how JSON-LD is simpler than HAL.

## Linking and Duck Typing

While it is legal in JSON-LD to write the "up" link as `{"up": "/"}`:

```js
{
   "@id": "/entries/hydra-lite.json",
   "name": "JSON-LD/Hydra lite",
   "url": "http://eric.themoritzfamily.com/hydra-lite.html",
   "up": "/"
}
```

In my experience, most clients written to consume hypermedia are written
in an ad-hoc way.  While it would be ideal that every consumer of this
service would use a JSON-LD enabled client, that is often not the
case.

For JSON-LD naive clients, it is better to structure the link as I
have above. The reason I use an object is for duck typing and future
proofing the service.

If I would have started with `{"up": "/"}`, adding the `name` field to
the resource would change the JSON type of the `up` property from a
string to an object.  Clients will likely break if they expect a
string and get an object.

## Resource typing

There are recurring patterns that I have seen in my work with services
and the most common one has to be resource typing.

By definition, resource typing giving a resource a `type` field to
classifies it for clients to identify its type.

This is often solved in an ad-hoc way like the following:

```js
{
   "@id": "/entries/hydra-lite.json",
   "objectType": "BlogPost",
   "name": "JSON-LD/Hydra lite",
   "url": "http://eric.themoritzfamily.com/hydra-lite.html",
   "up": {
      "@id": "/",
      "name": "Eric Moritz' blog",
      "type": "Homepage"
   }
}
```

as often the case, different developers designed the schema of the
`BlogPost` class and the `Homepage` class in isolation and didn't
coordinate their field names.

JSON-LD has a standard field called `@type` to type resources:

```
{
   "@id": "/entries/hydra-lite.json",
   "@type": ["BlogPost"],
   "objectType": "BlogPost",
   "name": "JSON-LD/Hydra lite",
   "url": "http://eric.themoritzfamily.com/hydra-lite.html",
   "up": {
      "@id": "/",
      "name": "Eric Moritz' blog",
      "type": "Homepage",
      "@type": ["Homepage"]
   }
}
```

For backwards compatibility, we keep the "objectType" and "type"
fields and bolt on the standard JSON-LD "@type" field.

You will notice that I used an array for the `@type` value.  This is
because `@type` can have multiple values.

For instance, we could provide a superclass for both these resources
called a [Thing](http://schema.org/Thing):

```js
{
   "@id": "/entries/hydra-lite.json",
   "@type": ["BlogPost", "Thing"],
   "objectType": "BlogPost",
   "name": "JSON-LD/Hydra lite",
   "url": "http://eric.themoritzfamily.com/hydra-lite.html",
   "up": {
      "@id": "/",
      "name": "Eric Moritz' blog",
      "type": "Homepage",
      "@type": ["Homepage", "Thing"]
   }
}
```

Typing is extremely valuable for clients that need to render these
resources.  Generic templates/UI components can be designed for all
`Thing` resources and more specific templates/UI components could be
designed for `BlogPost` and `Homepage` resources.


## Operations

Finally, I want to introduce Hydra operations.  This is the only bit
of Hydra that Hydra lite uses:

```js
{
   "@id": "/entries/hydra-lite.json",
   "@type": ["BlogPost", "Thing"],
   "name": "JSON-LD/Hydra lite",
   "url": "http://eric.themoritzfamily.com/hydra-lite.html",
   "up": {
      "@id": "/",
      "name": "Eric Moritz' blog",
      "@type": ["Homepage", "Thing"]
   },
   "operation": [
      {"method": "DELETE"},
      {
        "method": "PUT",
        "expects": {
          "@id": "BlogPost",
          "supportedProperty": [
             {"@id": "name", "required": true},
             {"@id": "body"}
          ]
        }
       }
   ]
}
```

Operations are the final component of Hydra lite that finalizes it as
a complete hypermedia solution.

## Conclusion

There is no argument from me that the inclusion of Linked Data
principles to hypermedia services are extremely valuable for
documentation purposes. However, when it comes to RESTful service
developers looking to introduce hypermedia into their services, Hydra
lite provides an easy way to bolt it on without a major refactor of
the service and without weeks of research into what Linked Data is and
what it provides.

While I am not a member of the [Hydra W3C Community
Group](http://www.hydra-cg.com/) I welcome any questions and
suggestions from the Hydra-CG team on how to improve Hydra lite.

