Experimenting
#############
:date: 2008-05-09 11:01:00
:tags: django, programming, python, smisk

I ran across Smisk_ two days ago and though. "Hmm,  someone should write a wsgi adaptor for that".

Maybe an hour after I had that thought,  I started working on one.  It was pretty easy.  Smisk_'s classes seem to be inspired by WSGI_, all the wsgi environment variables had a Smisk_ equivilent.  So the adaptor was basically putting tab A in Slot B and Tab B is slot A, etc.

If you noticed in my `del.icio.us feed`_.  I bookmarked Smisk_ itself and three hours later, I bookmarked my launchpad branch of `smisk-wsgi`_.  Pretty cool.

Fifteen hours later across the globe in Sweden, Smisk_'s project owner Rasmus Anderson, `merged my code`_ in with some changes. 

So in a total of 3 hours, something went from concept to reality thanks to Python_.  I don't think the quickness is a testimate to my mad hacking skills.  It's really a testimate to Python_'s agility.

So what is Smisk_ and why is it cool?   Smisk_ is a low level web framework built in C but controled by Python.   Basically it's a fastcgi_ interface to Python with some really well thought out classes bolted on.

What does the wsgi_ adapter get you?  It basically allows you to expose your wsgi_ based framework/app (Django_, Cherrypy_, etc) to fastcgi_ via C.  Now, what does that get you?  Well it gets you a faster fastcgi_ protocol (I think).  

Now, I don't have any quantifiable evidence if it's actually faster or not. Rasmus has some `performance tests`_ on the Smisk_ wiki.  Logic would say it would be.  If it is faster,  it's probably in the range of miliseconds, so it's probably not something to lose sleep over.  Generally your application slows down due to database performance.

Is the WSGI adaptor compliant?  For the most part.  I'm doing tests with the wsgiref's validator app.  There are some methods that we have to add to smisk's Stream class to make it valid.  That means C work, so I have to brush up on my skills, but it shouldn't be long.

I'm currently running this blog on Django_ on top of Smisk_.  I found some nasty bugs (causes segfaults on POST) that were in the Stream class, so I wouldn't recomend doing the same until Rasmus merges the changes_ I sent him.

Will this replace flup_ as a fastcgi_ to wsgi_ adapter?  I doubt it at this point, flup_ has some nice pooling features that would have to be built into Smisk_ in order for Smisk_ to have the flexibility of flup_.  I don't know if those features are in Rasmus' plans for Smisk_ or not.  

.. _Smisk: http://trac.hunch.se/smisk/
.. _WSGI: http://www.python.org/dev/peps/pep-0333/
.. _del.icio.us feed: http://del.icio.us/ericmoritz
.. _smisk-wsgi: https://code.launchpad.net/~ericmoritz/+junk/smisk-wsgi
.. _merged my code: http://hg.hunch.se/smisk/rev/0ddab23e8dc8
.. _Python: http://www.python.org
.. _fastcgi: http://www.fastcgi.com/
.. _Django: http://www.djangoproject.com
.. _Cherrypy: http://www.cherrypy.org
.. _performance tests: http://trac.hunch.se/smisk/wiki/Performance
.. _changes: http://eric.themoritzfamily.com/upload/smisk.wsgi.patch
.. _flup: http://www.saddi.com/software/flup/