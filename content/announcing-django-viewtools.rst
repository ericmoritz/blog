Announcing django-viewtools
###########################
:date: 2009-02-17 18:30:37
:tags: debugging, django, python

Hi, I'm announcing a project I have called `django-viewtools <https://launchpad.net/django-viewtools>`_

django-viewtools provides a management command to help in debugging and profiling views

=========
Overview
=========

django-viewtools provides a number of management commands for
debugging views.

There are a number of flags that can be used when calling the view

-d, --debug: This sets settings.DEBUG to True before calling the
 view. This allows you to retrieve the content from a view in
 production when settings.DEBUG is on

-n, --no-debug: This sets settings.DEBUG to False, handy to see what
 will happen if DEBUG is turned off.

--pdb: This starts PDB before the request is handled. Great for when
  you have a traceback email and want to set a breakpoint where it
  occurs.

--pm: This fires up PDB's post_mortum when an error occurs in the
  process of calling a view.

--profile: This dumps a hotshot profile file to the location specified
  for profiling the performance of a view.

-q, --quiet: Don't output the response of the view

-m, --mute: Turn off output through stdout and stderr, handy for noisy
 views with print statements everywhere.

Example
========
So you have a traceback that gives you the following


.. sourcecode::
   python

  File "/home/eric/Projects/django/env/django-1.0.2/lib/python2.5/site-packages/viewtools/views.py", line 4, in py_error
    raise ValueError("This is an error")

An you don't know why it's happening. Even worse, it's only happening
on your production server.

Before django-viewtools, you only had one option in this scenario,
edit your production code, put some print statements or forced
assertion errors to peek into the code to see the problem.

django-viewtools makes things a lot easier

.. sourcecode::
   python

    (django-1.0.2)eric@knoxpy:~/Projects/django/projects/viewtooltest$ ./manage.py viewtools --pdb /py_error/
    > /home/eric/Projects/django/env/django-1.0.2/lib/python2.5/site-packages/viewtools/management/commands/viewtools.py(135)call_view()
    -> try:
    (Pdb) break /home/eric/Projects/django/env/django-1.0.2/lib/python2.5/site-packages/viewtools/views.py:4
    Breakpoint 1 at /home/eric/Projects/django/env/django-1.0.2/lib/python2.5/site-packages/viewtools/views.py:4
    (Pdb) continue
    > /home/eric/Projects/django/env/django-1.0.2/lib/python2.5/site-packages/viewtools/views.py(4)py_error()
    -> raise ValueError("This is an error")
    (Pdb) list
      1 from django.db import connection as db
      2
      3 def py_error(request):
      4 B-> raise ValueError("This is an error")
      5
      6 def db_error(request):
      7 c = db.cursor()
      8 c.execute("select * from asotuhaosetuhaosethuasote")
    [EOF]
    (Pdb) print request
    <WSGIRequest
    GET:<QueryDict: {}>,
    POST:<QueryDict: {}>,
    COOKIES:{},
    META:{'CONTENT_TYPE': 'text/html; charset=utf-8',
     'HTTP_COOKIE': <SimpleCookie: >,
     'PATH_INFO': u'/py_error/',
     'QUERY_STRING': '',
     'REQUEST_METHOD': 'GET',
     'SCRIPT_NAME': u'',
     'SERVER_NAME': 'testserver',
     'SERVER_PORT': '80',
     'SERVER_PROTOCOL': 'HTTP/1.1',
     'wsgi.errors': <cStringIO.StringO object at 0x10a68b8>,
     'wsgi.input': <django.test.client.FakePayload object at 0x10ec150>,
     'wsgi.multiprocess': True,
     'wsgi.multithread': False,
     'wsgi.run_once': False,
     'wsgi.url_scheme': 'http',
     'wsgi.version': (1, 0)}>
    (Pdb)

Isn't that just great? I can see all the local variables in the view.
