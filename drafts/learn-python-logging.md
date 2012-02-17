Title: Learn Python Logging
Date: 2012-02-17 17:46:00
Tags: python, logging

The Python logging module is often a source of confusion with
developers.  Often logging is the final thought in a project and the
last thing we want to do when we're finishing up a project is sift
through the [logging
documentation](http://docs.python.org/library/logging.html) to figure
it out. It is a perpetual cycle that results in some very bad code.

# How modules should use Python logging

The first source of confusion with the Python logging module is the
question of how do I create a logger.  This is probably the easiest
part of Python logging.  Here's how you do it:

    import logging
    log = logging.getLogger(__name__)

That's basically it.  That will create a logger based on the module's
fully qualified name. So if we have a module called mypackage.module1.module2.
That will be the logger's name.  

Keep in mind that `__name__` could be the string
"\_\_main\_\_" if your python file is ran as a script.  Other than that,
that is all you need to know.

You don't have to worry about logging levels, or handlers or anything
in your modules.  How your loggers are configured is an application level setting and your modules have no reason to worry about that stuff.

# Logger names

An often overlooked fact about loggers is that logger names are hierarchical.  That is why I choose to use the module name as the logger name.

There is a root logger that can be accessed by calling:

      rootLogger = logging.getLogger()

Configuring the root logger will cascade down to the other loggers:

      rootLogger.setLevel(logging.INFO)

The same is true if you access a parent of any other logger:

      appLogger = logging.getLogger("myapp")
      appLogger.setLevel(logging.INFO)

All `myapp.*` loggers will have the level `INFO` as their default.

Let us say that there are the following loggers used in your application:

* redis.connection
* mysql.connection
* mysql.query
* myapp.models.polls
* myapp.models.questions
* myapp.models.articles

If we only wanted connection errors from redis and mysql, query debug
information from mysql and warnings from myapp's models, we could configure it as so:

    logging.getLogger().setLevel(logging.ERROR)
    logging.getLogger("mysql.query").setLevel(logging.DEBUG)
    logging.getLogger("myapp.models").setLevel(logging.WARNING)

That's it.  This accomplishes what I described.  The default level is
ERROR which causes "redis.connection" and "mysql.connection" to only
emit ERROR and EXCEPTION level messages.  "mysql.query" DEBUG and
above messages are logged and 

# Configuring Python loggers

I just showed you how to configure the level of a logger
pragmatically. Where should that code exist?  If you answered, "In the
module", I want you to get up, find the nearest blunt object and hit
yourself with it. Do you not remember me saying that logging configuration is an application level configuration?

Here's a hypothetical script that uses a redis connection.


    import csv
    from redis import StrictRedis
    
    reader = csv.reader(open("./presidents.csv"))
    header = reader.next()
    
    client = StrictRedis()
    
    
    for row in reader:
        key = "president:%s" % (row[0], )
        doc = dict(zip(header, row))
    
        client.set(key, doc)

Now, let's assume that the redis module defined the above mentioned,
"redis.connection" logger that logs a DEBUG level message whenever the
redis client needs to reconnect to the server.  

When we run the code as it is, no connection messages will be printed.

Now, let's say our connection is flaky and we have to reconnect to
redis:

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
    

We can configure the "redis.connection" logger to output the
connection messages by configuring our script like so:

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


For that script, we could of probably replaced:

    logging.basicConfig()
    logging.getLogger("redis.connection").setLevel(logging.DEBUG)
 
With:

    logging.basicConfig(level=logging.DEBUG)


# What is a Handler and What is a Formatter?

Apart from Loggers, there are three classes that are used to configure
an application's loggers.

A Handler defines how a message is handled.  For instance, there is a
[StreamHandler](http://docs.python.org/library/logging.handlers.html#streamhandler)
that logs messages to stderr.

There are 13 standard Handlers defined in the
[logging.handlers](http://docs.python.org/library/logging.handlers.html) 
module that will send messages to files, syslog, HTTP servers,
sockets, what have you.

A Formatter is exactly what it sounds like.  It formats a
LogRecord. That's pretty much it.


Let us change our presidential import script to log any exceptions
that occur when importing
                                       
    import config
    import logging
    from logging.handlers import SMTPHandler
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
        
            client.set(key, doc)
    except:
        log.exception("Dang it.")
        raise

Notice that we added "import config, this will let us separate
configuration from implementation.  For our little one-off script,
having a config.py module only exists to prove a point.

Here's the contents of config.py:

    import logging
    from logging import FileHandler, StreamHandler

    default_formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
    
    console_handler = StreamHandler()
    console_handler.setLevel(logging.INFO)

    error_handler = FileHandler("error.log", "a")
    error_handler.setLevel(logging.ERROR)

    root = log.getLogger()
    root.addHandler(console_handler)
	root.addHandler(error_handler)
    root.setFormatter(default_formatter)


An alternative way to configure your application's logger is to use
the
[logging.config.fileConfig](http://docs.python.org/library/logging.config.html#logging.config.fileConfig)
to configure the loggers using an INI file.  Here is an example by
combining all the examples we have seen.  We want to output INFO level 
messages to stderr and EXCEPTION level messages to a `pwd`/error.log

    [formatters]
    keys=default
    
    [formatter_default]
    format=%(asctime)s:%(levelname)s:%(message)s
    class=logging.Formatter
    
    [handlers]
    keys=console, error_file
    
    [handler_console]
    class=logging.StreamHandler
    level=INFO
    format=default
    args=tuple()
    
    [handler_error_file]
    class=logging.FileHandler
    level=ERROR
    format=default
    args=("error.log", "w")
    
    [loggers]
    keys=root
    
    [logger_root]
    level=INFO
    formatter=default
    handlers=console,error_file
    

To use this file, let's modify our config.py:

    import logging.config
    import os.path
    LOGGING_CONF=os.path.join(os.path.dirname(__file__),
                              "logging.ini")
                              
    logging.config.fileConfig(LOGGING_CONF)

There we have it.  It's pretty simple once you use it properly.
