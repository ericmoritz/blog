Title: Your own appengine
Date: 2008-04-08 18:16:23
Tags: appengine, couchdb, django, parellel, python, tahoe

My main gripe with [appengine](http://code.google.com/appengine/) is that while you're sticking your app on a lot of iron, it's pretty much stuck there forever because of the infrastructure.  Your app is not portable.  You can't just take it off of Google's iron and host it yourself. 

So, when I was listening to [part 3](http://www.youtube.com/watch?v=oG6Ac7d-Nx8) of the google app engine intro, I heard him describe BigTable as a "a distributed, fault-tolerant and schema-free", I knew I heard that before.  I heard that from the [CouchDB project](http://incubator.apache.org/couchdb/).  I never saw a need for CouchDB, but it's looking interesting now.

After looking at the SDK for appengine, the datastore interface is pretty simple, there's no reason it couldn't be implemented with CouchDB as the backend.  Giving you your own "distributed, fault-tolerant and schema-free" datastore.

Also in  [part 3](http://www.youtube.com/watch?v=oG6Ac7d-Nx8) that they run your python code on a low overhead, distributed, fault-tolerant infrastructure..  I knew I heard that before too. I heard it with the [Parallel Python](http://www.parallelpython.com) project.

Need a decentralized, fault-tolerant file system?  There's [Tahoe](http://allmydata.org/trac/tahoe).  Tahoo provides that too.

So let's say you have 20 servers, a mix match of database, media and http servers.  Now instead of partitioning them to have their own roles, they become nodes in a cloud all handling http, appserving, media file serving and data storage.  

If you create a webserver inside of parallel python that basically brokers requests for different sites to the parallel python cloud, a node in llpy then executes the request.  llpy may contact the couchdb cloud.  All using the power of the cloud.  Therefore if you have 22 sites and only 5 get heavy traffic, you don't have to waste the power of the other 17 machines on the slow sites.

The appengine SDK looks like a start to create such a system.  The datastore modules provide a way to interface CouchDB.  Recreating the http brokering system with llpy shouldn't be that hard.

And once the django community finds a way to work it's ORM onto Google's datastore api (which I know they will), implementing Django inside your own parellel python/couchdb appengine wouldn't be hard.

Creating your own appengine wouldn't be for the average joe schmoe, It would be for big companies with some iron.