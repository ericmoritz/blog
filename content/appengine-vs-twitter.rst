appengine vs twitter
####################
:date: 2008-05-20 03:17:11
:tags: django, gae, google, twitter

So `Glenn Franxman`_ was opining this afternoon about how twitter_ is going to reach a point where they're going to grow to big and need to make money somehow.  He said that they're either going to have to throw ads everywhere or hope to be aquired.

He thinks that they're like every startup in web 2.0 where they're hoping to be aquired by Google.

I said to him, "Why would Google aquire them?   I could write twitter on `google app engine`_ in like 30 minutes."

Well it took me two hours to shoehorn Django into GAE and about an hour to get a working prototype.  It's far from complete, but it works.  I still have to integrate textmarks_ to enable SMS i/o, add following and replies, but it works.

You can view the app at http://meow.appspot.com/  and you can checkout the code at https://launchpad.net/meow

.. _Glenn Franxman: http://www.hackermojo.com/
.. _twitter: http://www.twitter.com
.. _google app engine: http://code.google.com/appengine/
.. _textmarks: http://www.textmarks.com
