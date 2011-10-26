Django RSS
##########
:date: 2005-07-26 03:19:25

From what I can tell, turning on RSS is very easy. Basically you setup a
urlpattern like in
`http://code.djangoproject.com/svn/djangoproject.com/django\_website/settings/urls/main.py`_
and then make a module that is the same name as your settings module
that ends in \_rss, like so:
`http://code.djangoproject.com/svn/djangoproject.com/django\_website/settings/main\_rss.py`_

Happy hacking!

.. _`http://code.djangoproject.com/svn/djangoproject.com/django\_website/settings/urls/main.py`: http://code.djangoproject.com/svn/djangoproject.com/django_website/settings/urls/main.py
.. _`http://code.djangoproject.com/svn/djangoproject.com/django\_website/settings/main\_rss.py`: http://code.djangoproject.com/svn/djangoproject.com/django_website/settings/main_rss.py
