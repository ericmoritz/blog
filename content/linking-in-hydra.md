Title: Linking in Hydra
Date: 2015-05-01
Status: draft
Tags: linked-data, hydra, json-ld

<em>Please note that in order to keep the JSON concise,
I've omitted the JSON-LD `@context` and used standard naming.</em>

I had a conversation with a coworker about using JSON-LD and Hydra to
add hypermedia to an existing RESTful service. I will walk you through
our conversion. 

## Start with an object graph

It is our habit as RESTful service designers to think of our resources
first and then the verbs that operate on those resources. With
hypermedia I find that it is easier to think of the object graph of a
service.

So, lets start with the definition of a "Resource" most hypermedia
services. A Resource is simply a collection of key value pairs. Links
are properties that point to other resources (bags of key/value
pairs).

So in his service, he has two resources, a TopFive resource and an
Asset Resource.

```
  [TopFive]    [Asset]
```

Starting with the TopFive resource we have a link to Asset resources
called `contents`

```
  [TopFive] --- contents --> [Asset]
```

Next he needs a way to Fetch assets using an list of asset ids. This
is a link from TopFive to an AssetCollection resource. Lets call this
link `assetMultiGet`

```
  [TopFive] -- assetMultiGet --> [AssetCollection] --> member --> [Asset]
```

So now our service's entire object graph looks like the following

```
   [TopFive] ---- contents --> [Asset]
       |
       +---- assetMultiGet --> [AssetCollection]  --> member --> [Asset]
```

Now that we have defined what our object graph looks like, we can
design our hypermedia service based on the requirements of the clients.

## Lens? Representations?

I find a good analogy to use is that URLs are lens into our service's
object graph. These URLs will only show us one particular
representation of our entire object graph (The R of REST!).

We can start a representation of our object graph starting with a
TopFive resource. The simplest representation our object graph for
this URL would be:

```
{
  "@id": "/"
  "@type": ["TopFive"],
}
```

In our service, "/" will return a `TopFive` resource.

Next we'll link this `TopFive` resource to `Asset` resources using the `contents` link:

```json
{
  "@id": "/"
  "@type": ["TopFive"],
  "contents": [
    "/assets/1",
    "/assets/2",    
    "/assets/3",
    "/assets/4",
  ]
}
```

This is the simpliest way to represent our object graph including the
`contents` link. We have the `TopFive` resource at the root and
`contents` links to the assets via their URLs.

There is an issue with this particular view of our object graph.
In order for a client to get access to the properties of each asset the
client will need to
[dereference](http://en.wikipedia.org/wiki/Dereferenceable_Uniform_Resource_Identifier)
each URL.

To make it easier for the client, we can include some of the asset's
properties. This way, the client will no longer need to dereference
the assets via HTTP.

```json
{
  "@id": "/",
  "@type": ["TopFive"],
  "contents": [
     {"@id": "/assets/1", "id": 1, "name": "Asset 1", "thumbnail": "..."},
     {"@id": "/assets/2", "id": 2, "name": "Asset 2", "thumbnail": "..."},
     {"@id": "/assets/3", "id": 3, "name": "Asset 3", "thumbnail": "..."},
     {"@id": "/assets/4", "id": 4, "name": "Asset 4", "thumbnail": "..."},
  ]
}
```

This is just like the decisions we make when writing HTML pages. In
HTML, We have to decide how much of the linked page needs to be
included with the linking page. 


The next link we need to include `assetMultiGet`. Now we have a
problem. This resource does not have a static URL. It has query
parameters.

Fortunately we have the `hydra:IriTemplate` class for linking to
resources that algorithmically.

```
{
  "@id": "/",
  "@type": ["TopFive"],
  "assetMultiGet": {
     "@id": "/assetMultiGet",
     "@type": ["IriTemplate", "AssetCollection"],
     "template": "/assetMultiGet{?assetId}",
     "mapping": [{
       "variable": "assetId",
       "property": "id",
       "required": true
     }]
  },
  "contents": [
     {"@id": "/assets/1", "name": "Asset 1", "thumbnail": "..."},
     {"@id": "/assets/2", "name": "Asset 1", "thumbnail": "..."},
     {"@id": "/assets/3", "name": "Asset 1", "thumbnail": "..."},
     {"@id": "/assets/4", "name": "Asset 1", "thumbnail": "..."},
  ]
}
```

You may be confused that `assetMultiGet` is supposed to link to an
`AssetCollection` but is doesn't look like an AssetCollection (i.e. no
member property).

That is because `assetMultiGet` is linking to an view of a
`AssetCollection` resource that has no `AssetCollection` properties.

Instead what `assetMultiGet` is linking to is a resource (at
"/assetMultiGet") which is both an `IriTemplate` and an
`AssetCollection` resource. This resource could have either
`IriTemplate` properties or `AssetCollection` properties. In this
case, it only has `IriTemplate` properties.

Clients can now use the `assetMultiGet` `IriTemplate` properties to
construct a URL to access an `AssetCollection` resource.

The client will choose which assets it has in it's memory to multiget.
Lets say it uses `/assets/1` and `/assets/2`.

The mapping states that in order to fill in the required `assetId`
parameter, it will use the `id` property.

So if the client requests `/assetMultiGet?assetId=1&assetId=2`:

```json
{
  "@id": "/assetMultiGet?assetId=1&assetId=2",
  "member": [
     {"@id": "/assets/1", "name": "Asset 1", "thumbnail": "..."},
     {"@id": "/assets/2", "name": "Asset 1", "thumbnail": "..."},
  ]
}
```

A IriTemplate resource is the Hydra analog to an HTML form with a
method of "get".

## Operation

The final way that we can interact with a service is via
`hydra:Operation` resources. This allows service developers to
describe POST/PUT/DELETE operations on resources.

His service is read only but if a client was allowed to delete a
resource an `Asset` resource might look like this:

```json
{
  "@id": "/asset/1",
  "operation": [
    {"method": "DELETE"},
    {"method": "PUT"}
  ]
}
```
So now we know that we make DELETE and PUT requests to the `/asset/1` URL.

## Summary.

So to summarize:

1. Start with the entire object graph of your service
2. URLs are lens into your entire object graph
3. @id are direct links i.e. &lt;a /&gt; tags
4. hydra:IriTemplate resources are like &lt;form method="get" /&gt; tags
5. hydra:operation links define POST/PUT/DELETE operations on the resource


## Interesting...

While we were talking, an interesting organizational fact came to
light.  He is only writing the `top-5` service.  Another developer is
writing the `asset-multiget` service.

This really hammers in the brilliance of the design of Hypermedia. We
no longer need to contain the entire object graph in one service. The
`top-5` service can run and develop independent of the
`asset-multiget` service and both can be independent of the `asset`
service.

The boundaries between the services can be chosen to meet the best
design and platform for these services. Links enable us to transfer
clients between these services as if it was one monolithic system.

