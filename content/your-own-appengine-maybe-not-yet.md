Title: Your own appengine, maybe not yet
Date: 2008-04-08 23:14:28
Tags: appengine, couchdb, diy, parellel, python, tahoe

Well, I started looking at both Parallel Python and CouchDB.

CouchDB still seems to be a viable replacement for the BigTable backend to datastore.  A GQL parser will have to be written to interface with Couch's views, but that's probably easy enough.

After looking at PP (Parallel Python) a little more.  It's definitely not the correct solution.  PP only works with a limitted python scope.  You couldn't say, load all of Django inside of PP.

The way that appengine works is simple CGI, this makes every request autonomous.  It doesn't need to know what machine it's running on. 

One possible implementation is to distribute your source code across all nodes.  With some kind of virtual hosting router and load balance system, you could make your own appengine on a small scale.  

mod_fastcgi on lighttpd allows you to load balance application servers inside of  lighttpd.  You could distribute fastcgi servers across all 20 app servers all with a pool of min_children/20.  So if you need at least 10 children you could have 1 app server per site per machine.  I'm not completely sure, but I don't think mod_fastcgi load balancing provides any fault tolerance.

So the idea is to have each http request load balanced to each lighttpd server.  each lighttpd server load balances fastcgi among all the nodes.  Each fastcgi app server can access the couchdb cloud of all the nodes.