Title: Building with Hydra and Reactjs
Date: 2015-02-15 00:00:00
Tags: RDF, react, reactjs, hydra, json-ld
Status: draft

For the past year or so I've challenged myself to research a better
way to build RESTful services. The approach we've taken in the past
led to tightly coupled clients with hardcoded knowledged of how to
construct the URL to fetch a resource.

This approach has lead to tons of human readable documentation and
very brittle clients that break as soon as a URL's structure changes.

## Thinking with hypermedia

Take yourself back to when you first started making websites.  Most of
us started with a plan and that plan was called a site map. We would
follow a throught process for each site we built.

We would start at the homepage. Then we would think about how the user
would navigate away from the homepage.  Maybe they would use the search
engine using a **form**, or maybe they'd click on the latest article
**link**, or maybe they would click on a category **link** to see the
articles for that category.

Our site map might look something like this:

![blog site map](/static/blog_site_map.png)

Hypermedia services are much like this. The first step in designing a
hypermedia service is to think about which resources a user agent can
access and what links and forms a user agent can follow to reach
other resources.

In this blog post I'm going to walk you through a simple service I
constructed using [hydra](http://www.hydra-cg.com/). Hydra uses links
to URLs and templated URLs as forms to enable a user agent to
access linked resources.

# The service

A while back I wrote a
[CLI tool](https://github.com/ericmoritz/pitchfork-reviews) to dump
the latest reviews from [Pitchfork](http://pitchfork.com/) and filter
them by score so I could skip all the bad albums and jump straight to
higher scoring albums.

I have been playing with Spark for a project at work and as an
exercise I [ported](https://github.com/ericmoritz/music-review-spider)
that CLI program to Spark.

Once I had some usable data, I thought "Why don't I store
it in a database for ad-hoc querying". So I did that.

Naturally my next thought was, "Why don't I put a web interface
in front of this and use that instead of the CLI tool?".

One thing led to another and I thought, "Why don't I create a
microservice for this and get some practice with
[React](http://facebook.github.io/react/) and [Hydra](http://www.hydra-cg.com/).

## Building the site map.

Again, I can't stress this enough. When building any kind of
hypermedia application (web site or web service) you should think
about the site map and how resources are interconnected.

I started with the thought that a user should have a queue of latest
reviews. They should be able to mark any review as "seen" and that
review will be removed from their queue and placed in a seen
collection.

With that simple interaction model, we have the following resources: a
`User/Queue` resource, and a `User/Seen` collection resource. We have a
`seenItem` form for instructing the user agent on how to PUT a review
into the `User/Seen` collection and how to DELETE a review from the
`User/Seen` collection.

![blog site map](/static/music_review_site_map_simple.png)

So we have the basic interactions for a user agent. Now we need to
think about how the user agent gets to their user's queue from an
index resource. The index resource serves as a single point of entry
for a user agent.

If we start from the `Index` resource, the user needs to login to get their
`User` resource. Obviously we need an `loginForm` to link them to
their `User` resource.

Once they are on their `User` resource, they can follow the `queue` or
`seen` links to their `User/Queue` or `User/Seen` resources.

Finally, I want them to be able to query their `User/Queue` resource for
reviews published after a date and/or reviews with a rating greater
than a given rating. For this we have a `queueForm` property.

So that's our completed site map:

![music review service site map](/static/music_review_site_map.png)

I'll skip the nitty gritty of the
[music-reviews-service](https://github.com/ericmoritz/music-reviews-service)
implementation and point you to the
[mock service](https://raw.githubusercontent.com/ericmoritz/music-reviews-html5-client/master/mock_service/index.json)
I wrote for the React client.

If you look at that index page you will see the loginForm that allows
the user agent to construct a link to a
[user's User resource](https://raw.githubusercontent.com/ericmoritz/music-reviews-html5-client/master/mock_service/user.json).


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
  "@id": "/mock_service/user.json",
  "@type": [
    "User"
  ],
  "queue": "/mock_service/queue.json",
  "seen": "/mock_service/seen.json"
}
```


In the
[User/Queue resource](https://raw.githubusercontent.com/ericmoritz/music-reviews-html5-client/master/mock_service/queue.json)
you will see the `queueForm` form for querying the `User/Queue` members.

I've embedded the `User` resource using the `user` link so that the
`seen` and `queue` links are accessible from the `User/Queue` and
`User/Seen` resources.

Finally we have a `seenItem` form for instructing a user agent on how to build a URL for a `User/Seen/Item` resource and how to PUT a new `User/Seen/Item` in the `User/Seen` collection and how to DELETE a `User/Seen/Item` from the `User/Seen` collection.

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
        "comment": "Restrict queue to items with a pub_date >= given datePublished",
        "property": "datePublished",
        "required": false,
        "variable": "pub_date_gte"
      },
      {
        "comment": "Restrict queue to items with a rating >= given ratingValue",
        "property": "ratingValue",
        "required": false,
        "variable": "score_gte"
      }
    ],
    "template": "/mock_service/queue.json{?pub_date_gte,score_gte}"
  },
  "seenItem": {
    "@type": "IriTemplate",
    "mapping": [
      {
        "property": "review_id",
        "required": true,
        "variable": "review_id"
      }
    ],
    "operation": [
      {
        "@type": "DeleteResourceOperation",
        "comment": "If you delete a review into a user's seen collection, it adds it to their queue",
        "method": "DELETE"
      },
      {
        "@type": "CreateResourceOperation",
        "comment": "If you put a review into a user's seen collection, it removes it from their queue",
        "method": "PUT"
      }
    ],
    "template": "/mock_service/seen/{review_id}"
  },
  "user": {
    "@id": "/mock_service/user.json",
    "@type": ["User"],
    "queue": "/mock_service/queue.json",
    "seen": "/mock_service/seen.json"
  }
}
```

Finally the `User/Seen` resource which looks a lot like the `User/Queue` resource.

```json
{
  "@context": {...},
  "@id": "/mock_service/seen.json",
  "@type": [
    "Collection",
    "ReviewList",
    "User/Seen"
  ],
  "member": [],
  "seenItem": {...},
  "user": {...}
}
```

As you can see we have a complete hypermedia service the follows the
[WWW Application Domain Requirements](http://www.ics.uci.edu/~fielding/pubs/dissertation/web_arch_domain.htm#sec_4_1)
and follows the semantics of our service.

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

We use the `window.location.hash` to determine the URL of the
JSON-LD for the current page.  This greatly simplifies the client
because to navigate to a new resource, we simply set the
`window.location.hash` to the link we're following.

You will see in the [UserMenu](https://github.com/ericmoritz/music-reviews-html5-client/blob/master/src/music-reviews.js#L32) component, we're just using &lt;a&gt; tags to
link to the `User/Seen` and `User/Queue` resources.

Handling the `queueForm` and `loginForm` links are a little more
complicated but pretty trivial.

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


We attempt to locate a `User` resource either by seeing if the root
resource is a `User` resource or if there is a `user` link on the root
resource. Then we map that `User` resource to a `UserMenu` component.

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

Next we check if there is a loginForm link and map that to a LoginForm
component.

```javascript

  if(this.state.data.loginForm) {
    loginForm = <LoginForm data={this.state.data.loginForm} />
  }

```

Next we determine if the root resource is of type `ReviewList` (the
superclass of `User/Queue` and `User/Seen` and map it to a
`ReviewList` component if it is.


```javascript

  if(hasType(this.state.data, 'ReviewList')) {
    reviewList = <ReviewList data={this.state.data} />
  }
```

Finally we just return the compontents we may have created.  JSX will simply ignore any undefined components.

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


Starting with the `UserForm` component, it simply constructs a form
that will use `iriTemplateRender()` to construct a URL to navigate to
`onSubmit`.

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

Next the `ReviewList` component maps its `member` proprety to `Review`
components and detects if a `queueForm` is linked to the `ReviewList`
resource. If a `queueForm` exists, it maps the `queueForm` to a
QueueForm component.


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
