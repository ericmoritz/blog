Javascript Name Clobbering
##########################
:date: 2005-07-22 00:58:46

I was working with two different javascript libraries today and ran into
the issue that brought about namespaces in other languages.

Jsval has a class called Field. I wanted to use prototype.js and
openrico so... guess what, prototype.js, has the class Field also... So,
they stepped on each other toes. I renamed all the Field references is
Jsval (because prototype.js is a dependancy for many libraries) and then
wrote this `http://en.wikipedia.org/wiki/Javascript\_Namespaces`_ out of
frustration. Maybe someone will listen to me and use javascript
namespaces.

.. _`http://en.wikipedia.org/wiki/Javascript\_Namespaces`: http://en.wikipedia.org/wiki/Javascript_Namespaces
