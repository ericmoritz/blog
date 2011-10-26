Google Apps Engine, wait what?!?
################################
:date: 2008-04-08 11:53:11
:tags: django, python

So I saw a post to this last night and I thought, "Oh it's like `Amazon's EC2 <http://www.amazon.com/gp/browse.html?node=201590011>`_ I won't ever need that".

Much to my surprise this morning, it's something I could really need.  It's a sandboxed distributed web framework.  No need for load balancing, hardware, whatever.

The first thing I saw was it uses WSGI, my first thought, "Sweet Django can run on this."  Which is true... sort-of.

There are few limitations that will `drive Djangonistas crazy. <http://code.google.com/appengine/docs/python/sandbox.html>`_.  

First, there is no local file support.  You can't upload arbitrary files to the file system.  *BUT*, you can store them in the datastore, so with Marty Alchin's filesystem backends, someone can write a  FileSystemBackend to support storing files into google's datastore

Second, and the big one,  Django Model support.  At first I thought, "oh, GQL,  sweet a SQL-like language, we can just make a DBBackend in django to support it."  Nope, for one, it's only supports Selects, and second, no joins.  So that's absolutely out of the question.

There are other ways of interfacing Django models to google's datastore.  One way is to implement dbapi on top of the google db.models, but that's probably absolutely retarded.  We'd have to implement a sql parser and basically our own db engine.

I haven't been following the queryset refactoring stuff, but hopefully it'll make this easier.  I'd like to see the Django ORM be less reliant on SQL.  I know the R in ORM is Relational, but I would be nice to be able to store and retrieve objects from different storage methods.

I'm surprised that there wasn't more effort made to make the two frameworks work together.  From what I see, I can't see a reason to run Django on GAE. 

So what does Django have going for it.  a ORM, and a Templating System.  GAE requires you to use the Datastore API, so no ORM.  Templating system?  GAE implements `Django templates <http://code.google.com/appengine/docs/gettingstarted/templates.html>`_  inside of webapp.  So no need for the Django Templating system.

Django provides tons of contrib apps, and those are great but how many of them rely on models, probably quite a few.  

I don't see a reason why you'd really want to load the complete Django stack if you can't use probably 75% of Django. 

I am really surprised that they didn't do more work to integrate GAE with Django.  I'm sure Guido was working really closely with GAE and it's not like he doesn't know about Django.

So here are benefits of GAE: First, you don't have to worry about hardware, it's all sitting on google's hardware being load balanced and distributed for you.  Don't have to worry about database optimization, again, it's all on google's hardware being load balanced and distributed.

So here are the faults of GAE, First, if you build an application on GAE, it's not portable, you can't take your app, export the data, plug it into Apache via mod_wsgi and go.  You're app is completely tied to the App Engine. Second, conspiracy alarms go off, google has all your application's data to do what they want with it.
 

