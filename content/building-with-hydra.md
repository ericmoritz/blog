Title: Building with Hydra and Reactjs
Date: 2015-02-15 00:00:00
Tags: RDF, react, reactjs, hydra, json-ld
Status: draft

For the past year or so I've challenged myself to research a better
way to build RESTful services. The approach we've taken in the past
has led to tightly coupled clients that we have to hardcode the
knowledged of how to construct a URL to fetch a resource.

The approach has lead to tons of human readable documentations and
very brittle clients that break as soon as a URL's structure changes.

## Thinking with hypermedia

Take yourself back to when you first started making websites.  Most of
us had a plan. That plan was called a site map.

We'd start at the homepage. Then we would think about how the user
would navigate away from the index page.  Maybe they'd use the search
engine using a *form*, or maybe they'd click on the latest article
*link*, or maybe they will click on a category *link* to see the
articles for that category.

Hybermedia services are much like that. To build a hypermedia service,
you must first think about where the client can go and where the client
can navigate to.  In this blog post I'm going to walk you through a
simple service I constructed using [hydra](http://www.hydra-cg.com/).

# The service

A while back I wrote a
[CLI tool](https://github.com/ericmoritz/pitchfork-reviews) in Haskell
to dump the latest reviews from [Pitchfork](http://pitchfork.com/) and
filter them by score so I could skip all the bad albums and review
higher scoring albums.  It was an exercise on how to do concurrency in
Haskell by spidering the site and concurrently fetching the reviews.

I have been playing with Spark for a project at work and as an
exercise I [ported](https://github.com/ericmoritz/music-review-spider)
that Haskell program to Spark.  Spark gave me a framework that does all the
parallelization for me. All I had to think about was how to collect
the URLs for spidering and then transform that HTML into usable data.

Obviously I thought, "Hey, I've got the data, why don't I store it in a
triplestore for ad-hoc querying".  So I did that and now a cronjob is
fetching that data and stuffing it into a local
[Fuseki](http://jena.apache.org/documentation/serving_data/) TDB
database.

Naturally my next thought was, "Why don't I put a web interface
in front of this and use that instead of the CLI". So I did that.
One thing led to another and I thought, "Why don't I create a
microservice for this and get some practice with
[React](http://facebook.github.io/react/) and [Hydra](http://www.hydra-cg.com/).

## Building the site map.

So to start building any kind of hypermedia applications. Be it a
website or a webservice; you should think about the site map and how
resources are interconnected.

I started with the thought that a user should have a queue of latest
reviews. They should be able to mark any review as "seen" and that
review will be removed from their queue and placed in a seen
collection.

With that simple interaction mode, we have the following resources: a
`User/Queue`, a `User/Seen` and a `seenListForm` form for PUTing a
`Review` in or DELETEing a `Review` from the `User/Seen`
collection. The `seenListForm` links the `User/Queue` to the
`User/Seen`.

So we have the basic interactions for a user, now we need to think
about how the user gets to their queue from an index page.

If we start from the `Index` resource, the user needs to login to get their
`User` resource. Obviously we need an `loginForm`.  Once they are on the
`User` resource, they can follow the `queue` or `seen` links to their
`User/Queue` or `User/Seen` resources.

Finally, I want to be able to query the `User/Queue` resource for
reviews published after a date and/or reviews with a rating greater
than a given rating. For this we have a `queueForm`.

So that's our completed site map:

<!-- TODO: site map image -->

I'll skip the nitty gritty of the
https://github.com/ericmoritz/music-reviews-service and point you to
the
[mock service](https://raw.githubusercontent.com/ericmoritz/music-reviews-html5-client/master/mock_service/index.json)
I wrote for the React client.

```json
{
  "@context": {...},
  "loginForm": {
    "@type": "hydra:IriTemplate",
     "mapping": [
       {
         "property": "@id",
         "variable": "user_uri",
         "comment": "Login with a user's URI"
       }
     ],
     "template": "/mock_service/user.json{?user_uri}"
   }
}
```

If you look at that index page you will see the loginForm that allows
the user agent to construct a link to a
[user's resource](https://raw.githubusercontent.com/ericmoritz/music-reviews-html5-client/master/mock_service/user.json).

```json
{
  "@context": {...},
  "@id": "/mock_service/user.json",
  "@type": [
    "User"
  ],
  "queue": "/mock_service/queue.json",
  "seen": "/mock_service/seen.json"
}
```
In the
[User resource](https://raw.githubusercontent.com/ericmoritz/music-reviews-html5-client/master/mock_service/user.json)
You will see the
[queue](https://raw.githubusercontent.com/ericmoritz/music-reviews-html5-client/master/mock_service/queue.json)
and
[seen](https://raw.githubusercontent.com/ericmoritz/music-reviews-html5-client/master/mock_service/seen.json)
links.

```json
{
  "@context": {...},
  "@id": "/mock_service/queue.json",
  "@type": [
    "Collection",
    "ReviewList",
    "User/Queue"
  ],
  "member": [...],
   "queueForm": {
     "@type": "IriTemplate",
     "mapping": [
       {
         "comment": "Restrict queue to items with a pub_date >= given pub_date",
         "property": "datePublished",
         "required": false,
         "variable": "pub_date_gte"
       },
       {
         "comment": "Restrict queue to items with a rating >= given normalizedScore",
         "property": "normalizedScore",
         "required": false,
         "variable": "score_gte"
       }
     ],
     "template": "/mock_service/queue.json{?pub_date_gte,score_gte}"
  },
  "user": {
    "@id": "/mock_service/user.json",
    "@type": [
      "User"
    ],
    "queue": "/mock_service/queue.json",
    "seen": "/mock_service/seen.json"
  }
}
```

In the
[User/Queue resource](https://raw.githubusercontent.com/ericmoritz/music-reviews-html5-client/master/mock_service/queue.json)
you will see the `queueForm` form and I've embedded the `User`
resource using the `user` link so that the `seen` and `queue` links
are accessible from the `User/Queue` and `User/Seen` resources.

```json
{
  "@context": {...},
  "@id": "/mock_service/seen.json",
  "@type": [
    "Collection",
    "ReviewList",
    "User/Seen"
  ],
  "member": [...],
  "user": {
    "@id": "/mock_service/user.json",
    "@type": [
      "User"
    ],
    "queue": "/mock_service/queue.json",
    "seen": "/mock_service/seen.json"
  }
}
```

Finally, the
[User/Seen resource](https://raw.githubusercontent.com/ericmoritz/music-reviews-html5-client/master/mock_service/seen.json)
excludes the `queueForm` because there is no reason to use a
`queueForm` to add reviews to the queue (they're already there).

To remove items from the `User/Seen` collection, you simply execute a
DELETE request on the `Review`'s `@id`.

As you can see we have a complete hypermedia service as described by
[WWW Application Domain Requirements](http://www.ics.uci.edu/~fielding/pubs/dissertation/web_arch_domain.htm#sec_4_1)

# The React Client

Starting with the
[MusicReviewApp](https://github.com/ericmoritz/music-reviews-html5-client/blob/master/src/music-reviews.js#L164),
you will notice, all the logic for navigating the service is encoded in
the `navigate()` function:

```javascript
navigate(url) {
  this.setState({loading:true, data:this.state.data})
  $.ajax({
    url: url,
    dataType: 'json',
    success: data => {
      console.log(data);
      jsonld.compact(
        data,
        this.CONTEXT,
        (err, compacted) => {
          if(err) {
            console.error(url, err)
          } else {
            console.log(compacted);
            this.setState({loading:false, data:compacted})
          }
        }
      )
    },
    error: (xhr, status, err) => {
      this.setState({loading:false, data:{}}),
      console.error(url, status, err.toString()) 
    }
  })
},
serverUrl() {
  if(window.location.hash) {
    return window.location.hash.substring(1, window.location.hash.length)
  }
},
navigateToHash() {
  var serverUrl = this.serverUrl()
  if(serverUrl) {
    this.navigate(serverUrl);
   }
},
componentDidMount() {
  this.navigateToHash();
  $(window).on("hashchange", this.navigateToHash.bind(this))
}
```

We use the `window.location.hash` to determine the URL to located the
JSON-LD for the current page.  This greatly simplifies the client
because to navigate to a new resource, we simply set the
`window.location.hash` to the link we're following.

You will see in the [UserMenu](https://github.com/ericmoritz/music-reviews-html5-client/blob/master/src/music-reviews.js#L32) component, we're just using `a` tags to
link to the `User/Seen` and `User/Queue` resources.

Handling the `queueForm` and `loginForm` links are a little more
complicated but still manageable.

I wrote a simple
[iriTemplateRender()](https://github.com/ericmoritz/music-reviews-html5-client/blob/master/src/music-reviews.js#L18)
that given a `hydra:IriTemplate` object and an object of properties to
bind, it renders a URL that can be assigned to `window.location.hash`.

You will notice a lot of parallels between the resources we defined in
the service and React components we created for the client.  The
components, [ReviewList]() and [Review]() components have parallel
resources in the service. We're simply mapping the `ReviewList` and
`Review` resources to React components when we encounter them.

The most complex bit of the client comes in the `MusicReviewApp`'s
[render()](https://github.com/ericmoritz/music-reviews-html5-client/blob/master/src/music-reviews.js#L237) function.

Here we inspect the currently loaded root resource for available resources
and links based on the vocabulary of the service.

```javascript
render() {
  function hasType(object, type) {
    return object['@type'] && ensureArray(object['@type']).find(x => x	== type)
  }
  var content, loginForm, userMenu, userObj, reviewList, loading;

  if(this.state.loading) {
    loading = <Loading />
  }

  if(hasType(this.state.data, 'User')) {
    userObj = this.state.data;
  } else if(this.state.data.user) {
    userObj = this.state.data.user;
  }
  if(userObj) {
    userMenu = <UserMenu data={userObj} />
  }

```

We attempt to locate a `User` resource either by seeing if the root
resource is a `User` resource or if there is a `user` link on the root
resource. The we map that `User` resource to a `UserMenu` component.


```javascript

  if(this.state.data.loginForm) {
    loginForm = <LoginForm data={this.state.data.loginForm} />
  }

```

```javascript

  if(hasType(this.state.data, 'ReviewList')) {
    reviewList = <ReviewList data={this.state.data} />
  }
```

Next we determine if the root resource is of type `ReviewList` (the
superclass of `User/Queue` and `User/Seen` and map it to a
`ReviewList` component if it is.

```
  return (<bs.Panel bsStyle="primary">
    {loginForm}
    {userMenu}
    {loading}
    {reviewList}
    <div>
      <a href={this.serverUrl()} target="_blank">{this.serverUrl()}</a>
    </div>
   </bs.Panel>)
}
```

Next it is the job of the `UserForm` and `ReviewList` components to
render the `User` resource and `ReviewList` resources accordingly.

```javascript
var LoginForm = React.createClass({
    handleSubmit(e) {
  	  e.preventDefault();
	  var userUri = this.refs.userUri.getDOMNode().value.trim();
	  var url = iriTemplateRender(this.props.data, {'@id': userUri});
	  window.location.hash = "#" + url;
    },
	render() {
	  return (
	    <form className="LoginForm" onSubmit={this.handleSubmit}>
		Login: <input type="text" placeholder="user uri here" ref="userUri" />
		<input type="submit" value="Login" />
		</form>
      )
	}
});
```

Starting with the `UserForm` component, it simply constructs a form
that will use `iriTemplateRender()` to construct a URL to navigate to
`onSubmit`.

```javascript

var ReviewList = React.createClass({
    render() {
	  var formColContent;
	  var members = this.props.data.member;

	  var listColContent = (() => {
	    if(members.length) {
		  var items = members.map(
		    x => <bs.ListGroupItem><Review data={x} /></bs.ListGroupItem>
		  )
		  return <bs.ListGroup>{items}</bs.ListGroup>
		} else {
		  return <div>No items</div>
		}
	 })();

    if(this.props.data.queueForm) {
      formColContent = <QueueForm data={this.props.data.queueForm} />
	}

    return (
      <bs.Grid>
	  <bs.Row>
	    <bs.Col md={8}>{listColContent}</bs.Col>
	    <bs.Col md={4}>{formColContent}</bs.Col>
	  </bs.Row>
	  </bs.Grid>
	  )
  }
});
```

Next the `ReviewList` component maps its `member` proprety to `Review`
components and detects if a `queueForm` is linked to the `ReviewList`
resource. If a `queueForm` exists, it maps the `queueForm` to a
QueueForm component.

# Conclusion

I hope that you noticed that by using JSON-LD, Linked Data, Links, and
Forms that we have made a superior service to conventional
RESTful services.

We've removed all ambitquity by using hydra to described the links,
forms, and operations and Linked Data to document the classes and
properties.

By typing the resources using Linked Data types, we were able to
map those resources directly to React components for rendering and
interactivity.

I am personally excited about the possibility of this way of building
services.  I hope I got you excited as well.


