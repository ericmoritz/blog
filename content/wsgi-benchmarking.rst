wsgi-benchmarking
#################
:date: 2008-11-12 00:00:00
:tags: django, python, wsgi

WSGI Adapter Benchmarking
==========================

I took the opportunity to do some benchmarking of possible WSGI solutions for remote application servers.  The solutions described here are for the following setup: A frontend load balanced pool of visable HTTP servers that connect to a pool of load balanced internal application servers.

There were five solutions benchmarked:

  mod_proxy->Apache/mod_wsgi
    Uses mod_proxy on the frontend to talk to a pool of internal apache servers using embedded mod_wsgi
  
  mod_proxy->cherrypy
    Uses mod_proxy on the frontend to talk to a pool of internal `wsgiservers <http://www.cherrypy.org/browser/trunk/cherrypy/wsgiserver/__init__.py>`_ http servers

  mod_proxy->twisted.web2
    Uses mod_proxy on the frontend to talk to a pool of internal `twisted.web2 <http://twistedmatrix.com/trac/wiki/TwistedWeb2>`_ http servers

  mod_fastcgi->flup.server.fgci_fork
    Uses mod_fastcgi to talk to a pool of FLUP powered FCGI processes

  mod_scgi->flup.server.scgi_fork
    Uses mod_scgi to talk to a pool of FLUP powered SCGI processes


The benchmark that I did is basically just on overhead benchmark.  I did not test the concurrency performance of the solutions because I only have a single core 1.8ghz box at home and everything was done inside of two virtualbox VMs.

The apache, cherrypy, and twisted solutions all ran as HTTP servers on an internal VM that was only visible to the frontend VM.  Apache on the frontend VM used ProxyPass and ProxyPassReverse (setup described here, http://www.apachetutor.org/admin/reverseproxies) to broker the outside HTTP request to the internal VM.  The FCGI/SCGI solutions used mod_fastcgi and mod_scgi on the frontend VM and those modules connected directly to the internal VM using FLUP.

The benchmark script (stats/profile.sh) outputted three things.

1. Output of the sample WSGI app (shows the WSGI/HTTP headers passed to the internal server)
2. Headers of another request making a redirect from the internal server to the internal server to verify the Location header is rewritten correctly
3. AB stats of 1000 requests to the sample WSGI app to get a mean time per request.


Benchmark Summary
------------------

=================================  ====================  =======================
Solution                                   Mean                  Adj Mean
=================================  ====================  =======================
Baseline                                     1.121 [ms]                      n/a
mod_proxy->Apache/mod_wsgi                  10.748 [ms]               9.627 [ms]
mod_proxy->cherrypy                         14.281 [ms]              13.160 [ms]
mod_proxy->twisted.web2 server              20.503 [ms]              19.382 [ms]
mod_fcgi->flup_fcgi_fork                    20.940 [ms]              19.819 [ms]
mod_scgi->flup_scgi_fork                    24.902 [ms]              23.781 [ms]
=================================  ====================  =======================

Sample Size: 1000

The baseline shows the mean time to execute the application. The "adj mean" is "mean - baseline" to give the time the solution adds as overhead


Final Notes
------------

Apache appears to have the lowest overhead versus python only solutions.  Surprisingly fcgi and scgi did significantly worse than the mod_proxy solutions.  I personally trust the process management of Apache over cherrypy,twisted or FLUP and Apache has much more mature monitoring capabilities.

I would of really have liked to try nginx/mod_wsgi but I had trouble compiling it.  I have my doubts that nginx will be much faster than Apache for a single request and according to a comment made on this `page <http://piranha.org.ua/blog/2007/11/24/nginx-mod-wsgi-vs-fastcgi-en/>`_ nginx's asynchronous nature will probably kill performance with concurrent requests.

When it's all said and done, my money is on Apache/mod_wsgi for a remote application server.  Tried and true process management, mature monitoring tools and speed makes it a winner in my book.

Source code and results: http://eric.themoritzfamily.com/upload/wsgi-stats.zip