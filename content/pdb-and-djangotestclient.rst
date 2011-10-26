PDB and django.test.client
##########################
:date: 2008-11-17 00:14:57
:tags: debugging, django, pdb, python

So you have a site in production and someone called you up that there is a bug 
on the site.  Your template designer is trying to make a change to a template 
and the change is isn't showing up on the site.  You make the change on you 
development server and the change takes effect.  What is going wrong?

You can do a number of things:

 1. You can call your template designer an idiot and figure it's a problem between the chair and the keyboard
 2. You can spend hours trying to figure out how the development server and the production server differ and bang
    your head against the closest hard object until you find it.
 3. You can be a bad boy or girl and start changing code on the production server
 4. Or, you can use PDB and django.test.client to keep from spending all your hard earned money on hard liquor.
 
The url in question is the homepage.  We have a simple view, all it does is 
load a template.

.. sourcecode::
   python

    from django.http import HttpResponse
    from django.template import loader, Context
    
    def index(request):
        t = loader.get_template("index.html")
        c = Context({})
        return HttpResponse(t.render(c))
     
First we'll look at the index.html template that loads the page:

.. sourcecode::
   html

  <html>
  <head><title>Hi</title></head>
  <body>
  <h1>Welcome to my site, click on a link below to go somewhere</h1>
  {% include "includes/navigation.html" %}
  </body>
  </html>
 
Something is wrong with the include tag, it's not loading the correct template.
Taking a quick look in they site templates shows that the template exists.  
What's going on!

.. sourcecode::
   bash

  $ ls pdb_example_templates/includes/
  navigation.html  navigation.HTML~

Ok, there's something "wrong" with the {% include %} tag.  A quick glance at 
django/template/loader_tags.py shows that the ContantIncludeNode loads the 
template on line 102.  We're going to drill down the stack to find where the 
template is actually loaded.  Line 102 has get_template, get_template is 
defined in django.template.loader.  Open that up and find the definition of 
get_template. We see that get_template calls find_template_source.  That's 
up on the top of django.template.loader on line 47.  We know that there 
is something funky with the loading of the template so we have our starting 
point for PDB.

Let's SSH into the production server and start playing. First, what we need 
to do is create a simple little script to call the view. Let's call it wtf.py:

.. sourcecode::
   python

  def main():
      from django.test.client import Client
      c = Client()
      response = c.get("/")
	  print response.content

Since we're using *./manage.py shell* for this, we can't just do ol' 
*if __name__ == '__main__'* trick to run the script so we create a main() 
function to call from interactive mode.

.. sourcecode::
   python

  $ ~/src/pdb_example/manage.py shell
  Python 2.5.1 (r251:54863, Mar  7 2008, 03:39:23)
  Type "copyright", "credits" or "license" for more information.

  IPython 0.8.1 -- An enhanced Interactive Python.
  ?       -> Introduction to IPython's features.
  %magic  -> Information about IPython's 'magic' % functions.
  help    -> Python's own help system.
  object? -> Details about 'object'. ?object also works, ?? prints more.

  In [1]: import wtf

  In [2]: wtf.main()
  <html>
    <head><title>Hi</title></head>
  </html>
  <body>
  <h1>Welcome to my site, click on a link below to go somewhere</h1>
  <ul>
    <li><a href="/blog/">My Blog</a></li>
    <li><a href="http://www.flickr.com/photos/ericmoritz/">My Photos</a></li>
  </ul>
  </body>
 
Ok our little script calls up the correct view and generates the incorrect 
content, good.  Next step, get PDB into the mix.

There are two ways of doing this, the python way and the ipython way.  I'll 
do it the python way first for all you dummies that aren't using ipython yet 
(what are you waiting for?).  Edit wtf.py and add *import pdb; pdb.set_trace()*
right before the *c.get("/")* line.

.. sourcecode::
   python

  def main():
      from django.test.client import Client
      c = Client()
      import pdb; pdb.set_trace()
      response = c.get("/")
      print response.content
  
This will drop you into pdb before the view is called so you can set a 
breakpoint.

The *find_template_source* function does some module level caching stuff in 
the beginning. The guts that we want is near the bottom on line 67.

So let's fire up *manage.py shell* and set a breakpoint.

.. sourcecode::
   python

  $ ~/src/pdb_example/manage.py shell
  Python 2.5.1 (r251:54863, Mar  7 2008, 03:39:23)
  Type "copyright", "credits" or "license" for more information.

  IPython 0.8.1 -- An enhanced Interactive Python.
  ?       -> Introduction to IPython's features.
  %magic  -> Information about IPython's 'magic' % functions.
  help    -> Python's own help system.
  object? -> Details about 'object'. ?object also works, ?? prints more.
  
  In [1]: import wtf

  In [2]: wtf.main()
  > /home/eric/wtf.py(5)main()
  -> response = c.get("/")
  (Pdb) break django/template/loader.py:67
  Breakpoint 1 at /opt/django/versions/django-1.0/django/template/loader.py:67
  (Pdb) cont
  > /opt/django/versions/django-1.0/django/template/loader.py(67)find_template_source()
  -> for loader in template_source_loaders:
  (Pdb) list
   62                     import warnings 
   63                     warnings.warn("Your TEMPLATE_LOADERS setting includes %r, but your Python installation doesn't support that type of template loading. Consider removing that line from TEMPLATE_LOADERS." % path)
   64                 else:
   65                     loaders.append(func)
   66             template_source_loaders = tuple(loaders)
   67 B->     for loader in template_source_loaders:
   68             try:
   69                 source, display_name = loader(name, dirs)
   70                 return (source, make_origin(display_name, loader, name, dirs))
   71             except TemplateDoesNotExist:
   72                 pass
  (Pdb) name
  Out[2]: 'index.html'

Whoops, we're going to go through the load of every template and probably start 
drinking.  Let's make our breakpoint more specific.

.. sourcecode::
   python
  
  (Pdb) clear 1
  Deleted breakpoint 1
  (Pdb) break django/template/loader.py:67, name == 'includes/navigation.html'
  Breakpoint 2 at /opt/django/versions/django-1.0/django/template/loader.py:67
  
Ok, now our breakpoint will only break if the name of the template being loaded
is called *includes/navigation.html*. Let's continue.

.. sourcecode::
   python

  (Pdb) continue
  > /opt/django/versions/django-1.0/django/template/loader.py(67)find_template_source()
  -> for loader in template_source_loaders:
  (Pdb) name
  Out[2]: u'includes/navigation.html'
  (Pdb) list
   62                     import warnings
   63                     warnings.warn("Your TEMPLATE_LOADERS setting includes %r, but your Python installation doesn't support that type of template loading. Consider removing that line from TEMPLATE_LOADERS." % path)
   64                 else:
   65                     loaders.append(func)
   66             template_source_loaders = tuple(loaders)
   67 B->     for loader in template_source_loaders:
   68             try:
   69                 source, display_name = loader(name, dirs)
   70                 return (source, make_origin(display_name, loader, name, dirs))
   71             except TemplateDoesNotExist:
   72                 pass

Cool, we've successfully broke at the correct line with the correct template 
name.  Let's walk through the code.

.. sourcecode::
   python

   (Pdb) next
  > /opt/django/versions/django-1.0/django/template/loader.py(68)find_template_source()
  -> try:
  (Pdb) next
  > /opt/django/versions/django-1.0/django/template/loader.py(69)find_template_source()
  -> source, display_name = loader(name, dirs)

Now we're positioned right before the loader is called. Now we'll use the 
*step* command to step into that function.

.. sourcecode::
   python

  (Pdb) step
  --Call--
  > /opt/django/versions/django-1.0/django/template/loaders/app_directories.py(45)load_template_source()
  -> def load_template_source(template_name, template_dirs=None):
  (Pdb) list
   40                 yield safe_join(template_dir, template_name)
   41             except ValueError:
   42                 # The joined path was located outside of template_dir.
   43                 pass
   44
   45  -> def load_template_source(template_name, template_dirs=None):
   46         for filepath in get_template_sources(template_name, template_dirs):
   47             try:
   48                 return (open(filepath).read().decode(settings.FILE_CHARSET), filepath)
   49             except IOError:
   50                 pass
   
We're now at the start of the *load_template_source* function.  Let's walk 
through this function to see if it finds a template.

.. sourcecode::
   python
   
  (Pdb) next
  > /opt/django/versions/django-1.0/django/template/loaders/app_directories.py(46)load_template_source()
  -> for filepath in get_template_sources(template_name, template_dirs):
  (Pdb) next
  > /opt/django/versions/django-1.0/django/template/loaders/app_directories.py(47)load_template_source()
  -> try:
  (Pdb) filepath
  Out[2]: u'/home/eric/src/pdb_example/example/templates/includes/navigation.html'

Ok, the first template it's trying to load is the template in our app's 
templates folder.  This shouldn't work, so let's continue to verify that our
assumption is correct.


.. sourcecode::
   python


  (Pdb) next
  > /opt/django/versions/django-1.0/django/template/loaders/app_directories.py(48)load_template_source()
  -> return (open(filepath).read().decode(settings.FILE_CHARSET), filepath)
  (Pdb) next
  --Return--
  > /opt/django/versions/django-1.0/django/template/loaders/app_directories.py(48)load_template_source()->(u'<ul>\n...n</ul>\n', u'/home/...ion.html')
  -> return (open(filepath).read().decode(settings.FILE_CHARSET), filepath)
  (Pdb) next
  > /opt/django/versions/django-1.0/django/template/loader.py(70)find_template_source()
  -> return (source, make_origin(display_name, loader, name, dirs))
  (Pdb) list
   65                     loaders.append(func)
   66             template_source_loaders = tuple(loaders)
   67 B       for loader in template_source_loaders:
   68             try:
   69                 source, display_name = loader(name, dirs)
   70  ->             return (source, make_origin(display_name, loader, name, dirs))
   71             except TemplateDoesNotExist:
   72                 pass
   73         raise TemplateDoesNotExist, name
   74
   75     def get_template(template_name):
  (Pdb) source
  Out[2]: u'<ul>\n  <li><a href="/blog/">My Blog</a></li>\n  <li><a href="http://www.flickr.com/photos/ericmoritz/">My Photos</a></li>\n</ul>\n'
  (Pdb)
 
We've walked through the loader's function and have returned with a 
success.  However, this is the app_directories loader, the site should of used
the filesystem loader first because the template designer has his own
set of templates that are outside of the django project code. 

Let's look at our TEMPLATE_LOADERS setting to see what's up


.. sourcecode::
   python



  # List of callables that know how to import templates from various sources.
  TEMPLATE_LOADERS = (
      'django.template.loaders.app_directories.load_template_source',
      'django.template.loaders.filesystem.load_template_source',
  )

Doh!  Our loaders are backward.  Who did that?


.. sourcecode::
   python


  $ svn blame settings.py
  42 newman TEMPLATE_LOADERS = (
  42 newman     'django.template.loaders.app_directories.load_template_source',
  42 newman     'django.template.loaders.filesystem.load_template_source',
  42 newman )

Newman! Hang on, I have to go smack my other programmer in the back of the 
head...

Now to use pdb with ipython with all the benefits of ipython 
(colors, tab completion, etc). There is a module `here <http://trac.gotcha.python-hosting.com/file/bubblenet/pythoncode/ipdb/ipdb/__init__.py?format=txt>`_
that will help you out.  Just download that script as ipdb.py in the same
folder as wtf.py (or somewhere in sys.path)


.. sourcecode::
   bash


  $ curl http://trac.gotcha.python-hosting.com/file/bubblenet/pythoncode/ipdb/ipdb/__init__.py?format=txt > ipdb.py

Then change your code like this:

.. sourcecode::
   python


  def main():
    from django.test.client import Client
    c = Client()
    import ipdb; ipdb.set_trace()
    response = c.get("/")
    print response.content

So, there you have it.  How to use pdb and django.test.client to solve bugs 
in production without editing the code and potentially disrupting service.
