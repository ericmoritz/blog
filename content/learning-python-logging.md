Title: Learning Python Logging
Date: 2012-02-17 17:46:00
Tags: python, logging

The Python `logging` module is often a source of confusion with
developers.  Often, logging is the final thought in a project. When we
are finishing up a project, the last thing we want to do is sift
through the [logging
documentation](http://docs.python.org/library/logging.html) to figure
logging out. It is a perpetual cycle that results in some very bad
code.

I am going to assume that you have some familiarity with the Python
logging module and the concept of logging levels, so I will only
address concepts with the logging module that has been a source of
confusion in colleagues.

# How Python logging should be used in modules

The first source of confusion with the Python logging module is the
question of how to create a logger.  This is probably the easiest part
of Python logging.  Here's how you do it:

    :::python

    import logging
    log = logging.getLogger(__name__)

That is basically it.  That code will create a logger based on the
module's fully qualified name. So if we have a module called
`mypackage.module1.module2`, that will be the logger's name.

Keep in mind that `__name__` is the string `"__main__"` if
your Python file is run as a script.  Other than that, this is all you
need to do.

You do not have to worry about logging levels, handlers, or anything
else in your modules.  How your loggers are configured is an application
level setting. Your modules have no reason to worry about how to
configure loggers.

# Logger names

An often overlooked fact about loggers is that logger names are
hierarchical.  That is why I choose to use the module name as the
logger name. The hierarchy starts with the root logger and descends
from there.

The root logger can be accessed by calling:

    :::python

      rootLogger = logging.getLogger()

Configuring the root logger will cascade down to the other loggers:

    :::python

      rootLogger.setLevel(logging.INFO)

The same is true if you access a parent of any other logger:

    :::python

      appLogger = logging.getLogger("myapp")
      appLogger.setLevel(logging.INFO)

All `myapp.*` loggers will have the level `INFO` as their default.

Let us say that there are the following loggers used in our application:

* `redis.connection`
* `mysql.connection`
* `mysql.query`
* `myapp.models.polls`
* `myapp.models.questions`
* `myapp.models.articles`

If we only wanted connection errors from our databases, query debug
information from MySQL, and warnings from `myapp`'s models; we could
configure it as so:

    :::python

    logging.getLogger().setLevel(logging.ERROR)
    logging.getLogger("mysql.query").setLevel(logging.DEBUG)
    logging.getLogger("myapp.models").setLevel(logging.WARNING)

That is it.  This accomplishes what I described. We set the default
level to `ERROR` which causes `redis.connection` and `mysql.connection`
to only emit `ERROR` and `EXCEPTION` level messages. We set the
`mysql.query` logger to `DEBUG` to emit query debug messages. Finally, we
set the `myapp.models` logger to `WARNING`.

# Configuring Python loggers

I just showed you how to configure the level of a logger
pragmatically. Where should that code exist?  

If you answered, "In the module," I want you to get up, 
find the nearest blunt object, and hit yourself with it. 
Do you not remember me saying that logging configuration 
is an application level configuration?

Here is a hypothetical script that uses a Redis connection.

[`import_presidents1.py`](https://github.com/ericmoritz/blog/blob/master/example-code/learn-python-logging/import_presidents1.py):

    :::python

    import csv
    from redis import StrictRedis
    
    reader = csv.reader(open("./presidents.csv"))
    header = reader.next()
    
    client = StrictRedis()
    
    for row in reader:
        key = "president:%s" % (row[0], )
        doc = dict(zip(header, row))
    
        client.set(key, doc)
    

Now, let us assume that the redis module used a `redis.connection`
logger that logs a `DEBUG` level message whenever the redis client needs
to reconnect to the server. Here is a [mock Redis client](https://github.com/ericmoritz/blog/blob/master/example-code/learn-python-logging/redis.py)
for this example.

When we run the code as it is, no connection messages will be printed.

Now, let us say our connection is flaky and we have to reconnect to
Redis often:

[`import_presidents2.py`](https://github.com/ericmoritz/blog/blob/master/example-code/learn-python-logging/import_presidents2.py):

    :::python

    import csv
    from redis import StrictRedis
    
    reader = csv.reader(open("./presidents.csv"))
    header = reader.next()
    
    client = StrictRedis()
    
    for i, row in enumerate(reader):
        key = "president:%s" % (row[0], )
        doc = dict(zip(header, row))
    
        # simulate a disconnect every 3 operations
        if i % 3 == 0:
            client.disconnect()
    
        client.set(key, doc)
    
We can configure the `redis.connection` logger to output the
connection messages by configuring our script like so:

[`import_presidents3.py`](https://github.com/ericmoritz/blog/blob/master/example-code/learn-python-logging/import_presidents3.py):

    :::python

    import logging
    import csv
    from redis import StrictRedis
    
    logging.basicConfig()
    logging.getLogger("redis.connection").setLevel(logging.DEBUG)
    
    reader = csv.reader(open("./presidents.csv"))
    header = reader.next()
    
    client = StrictRedis()
    
    for i, row in enumerate(reader):
        key = "president:%s" % (row[0], )
        doc = dict(zip(header, row))
    
        # simulate a disconnect every 3 operations
        if i % 3 == 0:
            client.disconnect()
    
        client.set(key, doc)
    

For simplicity, we could have replaced:

    :::python

    logging.basicConfig()
    logging.getLogger("redis.connection").setLevel(logging.DEBUG)
 
with:

    :::python

    logging.basicConfig(level=logging.DEBUG)


[`logging.basicConfig()`](http://docs.python.org/library/logging.html#logging.basicConfig)
is a really handy function.  I find myself using `basicConfig()` often
because most of the time I simply want to output to `stderr` or to a
single file rather than wanting complex routing using Handlers.

# What are Handlers and Formatters?

Apart from Loggers, there are three classes that are used to configure
an application's loggers: `logging.Handler`, `logging.Formatter`, and
`logging.Filter`.

A Handler defines how a message is handled.  For instance, there is a
[StreamHandler](http://docs.python.org/library/logging.handlers.html#streamhandler)
that logs messages to `stderr`.

There are 13 standard Handlers defined in the
[`logging.handlers`](http://docs.python.org/library/logging.handlers.html) 
module that will send messages to files, syslog, HTTP servers,
sockets, and what have you.

A Formatter is exactly what it sounds like.  It formats a
LogRecord. That's pretty much it.

A Filter filters a LogRecord.  I have never needed one, so I will let
you define your own use case for Filters.

Let us change our presidential import script to log any exceptions
that occur when importing:
                                       
[`import_presidents4.py`](https://github.com/ericmoritz/blog/blob/master/example-code/learn-python-logging/import_presidents4.py):

    :::python

    import config
    import logging
    import csv
    from redis import StrictRedis
    
    # We do not want to use __name__ here because __name__ is "__main__"
    log = logging.getLogger("presidents.importer")
    
    try:
        reader = csv.reader(open("./presidents.csv"))
        header = reader.next()
    
        client = StrictRedis()
    
        for i, row in enumerate(reader):
            key = "president:%s" % (row[0], )
            doc = dict(zip(header, row))
    
            # simulate a disconnect every 3 operations
            if i % 3 == 0:
                client.disconnect()
    
            # simulate a failure
            if row[0] == "37":
                raise exception("crook.")
    
            client.set(key, doc)
    except:
        log.exception("dang it.")
    

Notice that we added `import config`. This will let us separate
configuration from implementation.  (For our little one-off script,
having a `config.py` module is overkill; it exists here to prove a
point.)

Here's the contents of [`config.py`](https://github.com/ericmoritz/blog/blob/master/example-code/learn-python-logging/config.py):

    :::python

    import logging
    from logging import FileHandler, StreamHandler
    
    default_formatter = logging.Formatter(\
       "%(asctime)s:%(levelname)s:%(message)s")
    
    console_handler = StreamHandler()
    console_handler.setFormatter(default_formatter)
    
    error_handler = FileHandler("error.log", "a")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(default_formatter)
    
    root = logging.getLogger()
    root.addHandler(console_handler)
    root.addHandler(error_handler)
    root.setLevel(logging.DEBUG)
    

An alternative way to configure your application's logger is to use
the
[`logging.config.fileConfig`](http://docs.python.org/library/logging.config.html#logging.config.fileConfig)
to configure the loggers using an INI file.

Here is the equivalent INI file for the configuration we previously
described using Python code:

[`logging.ini`](https://github.com/ericmoritz/blog/blob/master/example-code/learn-python-logging/logging.ini):

    :::ini

    [formatters]
    keys=default
    
    [formatter_default]
    format=%(asctime)s:%(levelname)s:%(message)s
    class=logging.Formatter
    
    [handlers]
    keys=console, error_file
    
    [handler_console]
    class=logging.StreamHandler
    formatter=default
    args=tuple()
    
    [handler_error_file]
    class=logging.FileHandler
    level=ERROR
    formatter=default
    args=("error.log", "w")
    
    [loggers]
    keys=root
    
    [logger_root]
    level=DEBUG
    formatter=default
    handlers=console,error_file
        

To use this file, let us modify our `config.py`.

[`config_ini.py`](https://github.com/ericmoritz/blog/blob/master/example-code/learn-python-logging/config_ini.py):

    :::python

    import logging.config
    import os.path
    LOGGING_CONF=os.path.join(os.path.dirname(__file__),
                              "logging.ini")
                              
    logging.config.fileConfig(LOGGING_CONF)

Finally, here's the updated import script:

[`import_presidents5.py`](https://github.com/ericmoritz/blog/blob/master/example-code/learn-python-logging/import_presidents5.py):

    import config_ini
    import logging
    import csv
    from redis import StrictRedis
    
    # We do not want to use __name__ here because __name__ is "__main__"
    log = logging.getLogger("presidents.importer")
    
    try:
        reader = csv.reader(open("./presidents.csv"))
        header = reader.next()
    
        client = StrictRedis()
    
        for i, row in enumerate(reader):
            key = "president:%s" % (row[0], )
            doc = dict(zip(header, row))
    
            # simulate a disconnect every 3 operations
            if i % 3 == 0:
                client.disconnect()
    
            # simulate a failure
            if row[0] == "37":
                raise Exception("Crook.")
    
            client.set(key, doc)
    except:
        log.exception("Dang it.")
    

For some people INI files leave a bad taste is the mouth.  If you do
not like the taste of INI files, you can also configure the loggers
using a dictionary or with Python code.  It's up to you.

There we have it. Python 2's built-in `logging` module is one of those
warts of the standard library that goes against the "Zen of Python";
but once you learn the non-obvious way the designers intended to be
used, it becomes simple.

I hope this helps clear up Python's logging module for you.

Links

* [Example Code](https://github.com/ericmoritz/blog/tree/master/example-code/learn-python-logging)
* [Hacker News Discussion](http://news.ycombinator.com/item?id=3612786)
