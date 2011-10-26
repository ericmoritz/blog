Python Encodings and Unicode
############################
:date: 2008-11-21 20:24:43
:tags: python

I am sure there has been a number of explanations on Unicode and Python 
but I'm going to do a little write up for my own sake.


Byte Streams VS Unicode Objects
----------------------------------------

Let's start by defining what a string in Python is.  When you use the 
string type what you're actually doing is storing a string of bytes.

.. sourcecode::
   python

  [  a ][  b ][  c ] = "abc"
  [ 97 ][ 98 ][ 99 ] = "abc"
  

With this example, the string "abc" is a string of the bytes, 97, 98, 99 in 
the ASCII table.  A deficiency of Python 2.X is that by default it treats 
every string as ASCII. Unfortunately ASCII is lowest common denominator of 
Latin type character sets.  

ASCII is the first 127 characters of a number 
of character mappings. Character mappings such as windows-1252 
(aka Latin-1, aka cp1252) and UTF-8 both have the same first 127 
characters. You're safe mixing string encodings when every byte value in 
your string is lower that 127.  However it's really dangerous to make that 
assumption.  More on that later.

A problem arises when you mix encodings that have bytes in them that are 
greater than 126.  Let's take another string encoded as windows-1252.  
Character map windows-1252 is a 8-bit character map so there can be a total
of 256 characters in the table.  The first 127 match ASCII, the second 127 
are extra characters that the windows-1252 encoding defines.

.. sourcecode::
   python

  A windows-1252 encoded string looks like this:
  [ 97 ] [ 98 ] [ 99 ] [ 150 ] = "abc–" 

Windows-1252 is still a string of bytes but do you see that the last byte is 
greater than 126.  If Python attempts to decode that byte stream as the 
default encoding ASCII, it will throw an error.  Let's see what happens 
when Python tries to decode that string.

.. sourcecode::
   python

  >>> x = "abc" + chr(150)
  >>> print repr(x)
  'abc\x96'
  >>> u"Hello" + x
  Traceback (most recent call last):
    File "<stdin>", line 1, in ?
  UnicodeDecodeError: 'ASCII' codec can't decode byte 0x96 in position 3: ordinal not in range(128)


Let's take another string encoded as UTF-8

.. sourcecode::
   python

   A UTF-8 encoded string looks like this:
   [ 97 ] [ 98 ] [ 99 ] [ 226 ] [ 128 ] [ 147 ] = "abc–" 
   [0x61] [0x62] [0x63] [0xe2]  [ 0x80] [ 0x93] = "abc-"
  
If you pull up your handy dandy Unicode character table, you'll see that an 
en dash is Unicode codepoint 8211 (0x2013).  That value is greater than 
the 127 max of ASCII.  Hell it's greater than the max value that 1 byte 
can store. Since 8211 (0x2013) is actually two bytes UTF-8 has to do some 
magic to tell the system there are three bytes needed to store one 
character.  Again, let's see what happens when Python attempts to use the 
default ASCII encoding on a UTF-8 encoded string that has characters 
greater than 126.


.. sourcecode::
   python

  >>> x = "abc\xe2\x80\x93"
  >>> print repr(x)
  'abc\xe2\x80\x93'
  >>> u"Hello" + x
  Traceback (most recent call last):
    File "<stdin>", line 1, in ?
  UnicodeDecodeError: 'ASCII' codec can't decode byte 0xe2 in position 3: ordinal not in range(128)

As you can see, Python always defaults to ASCII.  It hits that fourth byte
which has a decimal value of 226 that's greater than 126 so Python 
raises an error.  This is the trouble with mixing encodings.


Decoding Byte Streams
----------------------------
The term decoding can be confusing when you first start learning about 
Unicode in Python.  You decode byte streams to make Unicode objects and 
encode Unicode objects into byte streams.

Python has to know how to decode a byte stream to Unicode.  When you take 
a byte stream, you call it's "decode" method to create a Unicode object 
from it.

Your best bet is to decode byte streams to Unicode as early as possible.


.. sourcecode::
   python

  >>> x = "abc\xe2\x80\x93"
  >>> x = x.decode("utf-8")
  >>> print type(x)
  <type 'unicode'>
  >>> y = "abc" + chr(150)
  >>> y = y.decode("windows-1252")
  >>> print type(y)
  >>> print x + y
  abc–abc–

Encoding Unicode to byte streams
----------------------------------------
Unicode objects are an encoding agnostic representation of text.  You 
can't simply output a Unicode object.  It has to be turned into a byte 
string before it's outputted.  Python will be nice enough to do it for 
you however Python defaults to ASCII when encoding a Unicode object to 
a byte stream, this default behavior can be the source of many headaches.


.. sourcecode::
   python


  >>> u = u"abc\u2013"
  >>> print u
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
  UnicodeEncodeError: 'ascii' codec can't encode character u'\u2013' in position 3: ordinal not in range(128)
  >>> print u.encode("utf-8")
  abc–

Using the codecs module
-----------------------------
The codecs module can help out a lot when ingesting byte streams.  You can
open files with an encoding defined and what you read from that file will
automatically be converted to Unicode objects.

Try this

.. sourcecode::
   python


  >>> import codecs
  >>> fh = codecs.open("/tmp/utf-8.txt", "w", "utf-8")
  >>> fh.write(u"\u2013")
  >>> fh.close()
  
What that did was take an Unicode object and write it out as a utf-8 file.
You can do the same in the other direction.

Try this

.. sourcecode
   python

  >>> import urllib, codecs
  >>> fh = open("/tmp/google-com.html", "w")
  >>> fh.write(urllib.urlopen(url).read()) # Download Google's homepage to a file
  >>> fh.close()
  >>> fh = codecs.open("/tmp/google-com.html", "r", "utf-8")
  >>> type(fh.read(1))
  <type 'unicode'>

When reading data from a file codecs.open create a file object that will 
automatically convert the utf-8 encoded file into a Unicode object.

Let's take the previous example and use the urllib stream directly

.. sourcecode::
   python


  >>> stream = urllib.urlopen("http://www.google.com")
  >>> Reader = codecs.getreader("utf-8")
  >>> fh = Reader(stream)
  >>> type(fh.read(1))
  <type 'unicode'> 
  >>> Reader
  <class encodings.utf_8.StreamReader at 0xa6f890>

One-liner version

.. sourcecode::
   python


  >>> fh = codecs.getreader("utf-8")(urllib.urlopen("http://www.google.com"))
  >>> type(fh.read(1))
  
You have to be careful with the codecs module.  Whatever you pass to it 
must be a Unicode object otherwise it will try to automatically decode the
byte stream as ASCII

.. sourcecode::
   python

  >>> x = "abc\xe2\x80\x93" # our "abc-" utf-8 string
  >>> fh = codecs.open("/tmp/foo.txt", "w", "utf-8")
  >>> fh.write(x)
  Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/lib/python2.5/codecs.py", line 638, in write
    return self.writer.write(data)
  File "/usr/lib/python2.5/codecs.py", line 303, in write
    data, consumed = self.encode(object, self.errors)
  UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 3: ordinal not in range(128)
  
Crap, there Python goes again, trying to decode everything as ASCII.

Problems with slicing up UTF-8 byte streams
----------------------------------------------------

Since an UTF-8 encoded string is just a list of bytes, len() and slicing do not work correctly.  Take our string from before

.. sourcecode::
   python


  [ 97 ] [ 98 ] [ 99 ] [ 226 ] [ 128 ] [ 147 ] = "abc–"
  
Now do the following

.. sourcecode::
   python

  >>> my_utf8 = "abc–"
  >>> print len(my_utf8)
  6

What? It looks like 4 chars, but len is saying 6. This is because len is counting bytes not characters.  

.. sourcecode::
   python


  >>> print repr(my_utf8)
  'abc\xe2\x80\x93'

Now let's try slice the string

.. sourcecode::
   python


  >>> my_utf8[-1] # Get the last char
  '\x93'

Crap, that's the last byte, not the last char.

To slice up UTF-8 correctly, your best bet is to decode the byte stream to create a Unicode object from it.  Then you can manipulate, count, whatever safely.

.. sourcecode::
   python


  >>> my_unicode = my_utf8.decode("utf-8")
  >>> print repr(my_unicode)
  u'abc\u2013'
  >>> print len(my_unicode)
  4
  >>> print my_unicode[-1]
  –


When Python automatically encodes/decodes
------------------------------------------
There are a number of cases when Python could throw an error when it tries to
automatically encode or decode as ascii.

The first case is when it tries to concat unicode and string values together

.. sourcecode::
   python


  >>> u"" + u"\u2019".encode("utf-8")
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
  UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 0:   ordinal not in range(128)

The same will happen when you try to join a list.  Python will automatically 
decode strings to unicode when there are both strings and unicode objects in
the list

.. sourcecode::
   python


  >>> ",".join([u"This string\u2019s unicode", u"This string\u2019s utf-8".encode("utf-8")])
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
  UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 11:  ordinal not in range(128)

Or when trying to format a string

.. sourcecode::
   python


  >>> "%s\n%s" % (u"This string\u2019s unicode", u"This string\u2019s  utf-8".encode("utf-8"),)
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
  UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 11: ordinal not in range(128)

Basically when you are mixing unicode and byte strings together, you can
cause an error.

Take for instance you're taking a utf-8 file and then adding some text to it
that is an unicode object.  There can be a UnicodeDecodeError

.. sourcecode::
   python


  >>> buffer = []
  >>> fh = open("utf-8-sample.txt")
  >>> buffer.append(fh.read())
  >>> fh.close()
  >>> buffer.append(u"This string\u2019s unicode")
  >>> print repr(buffer)
  ['This file\xe2\x80\x99s got utf-8 in it\n', u'This string\u2019s unicode']
  >>> print "\n".join(buffer)
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
  UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 9: ordinal not in range(128)

You can fix that by using the codecs module to load in the file as unicode

.. sourcecode::
   python


  >>> import codecs
  >>> buffer = []
  >>> fh = open("utf-8-sample.txt", "r", "utf-8")
  >>> buffer.append(fh.read())
  >>> fh.close()
  >>> print repr(buffer)
  [u'This file\u2019s got utf-8 in it\n', u'This string\u2019s unicode']
  >>> buffer.append(u"This string\u2019s unicode")
  >>> print "\n".join(buffer)
  This file’s got utf-8 in it

  This string’s unicode

As you can see, the stream produced by codecs.open automatically converted the
string to unicode when the data is read.


Best Practices
-----------------

  1. Decode First, Encode Last
  2. When in doubt, encode as utf-8
  3. Use codecs with unicode objects to simplify things
  
Decode First means whenever taking byte stream input, decode
that input to Unicode as early as possible.  This will help prevent issues
where len() and slice malfunctions with utf-8 byte streams.

Encode last means only encode to byte streams when you're ready to output
the text to something.  That output could be a file, a database, a socket,
whatever.  Only encode the Unicode objects when you're done with 
them.  Encode last also means, don't let Python encode your Unicode 
objects for you.  Python will use ASCII and your programs will crash.

When in doubt, encode as UTF-8 means this:  Since UTF-8 can handle any Unicode
character, your best bet is to use it as opposed to window-1252 or god 
forbid ASCII.  

The codecs module help you skip steps when ingesting streams such as files
or sockets.  Without the tools provided by the codecs module you'll have to
read the content of the files into byte streams and then decode those 
byte streams into Unicode objects.

The codecs module lets you read the bytes in and decode the bytes on the
fly getting your text into unicode objects much simplier and with less
overhead.

 
Explaining UTF-8
--------------------
This final section will give you primer on UTF-8, you can ignore this
unless you're a super-geek. 

With UTF-8, any byte between 127 and 255 are special.  Those bytes tell the 
system that the bytes following the current byte are part of a multi-byte 
sequence.

.. sourcecode::
   python


  Our UTF-8 encoded string looks like this:
  [ 97 ] [ 98 ] [ 99 ] [ 226 ] [ 128 ] [ 147 ] = "abc–" 


The last three bytes are a UTF-8 multi-byte sequence.  If you convert the 
first of the three, 226 to binary you can see what it looks like.

.. sourcecode::
   python


  11100010


The first three bits tell the system that it is starting a three byte 
sequence that is 226, 128, 147

So taking the full sequence bytes

.. sourcecode::
   c

  11100010 10000000 10010011

Then you apply the following mask for three byte sequences (described 
`here <http://en.wikipedia.org/wiki/UTF-8#Description>`_)

.. sourcecode::
   c

  1110xxxx 10xxxxxx 10xxxxxx 
  XXXX0010 XX000000 XX010011 Remove the X's 
  0010       000000   010011 Collapse the numbers
  00100000 00010011          Get Unicode number 0x2013, 8211 The "–"

This is a basic primer on how UTF-8, refer to the UTF-8 Wikipedia page for
greater detail
