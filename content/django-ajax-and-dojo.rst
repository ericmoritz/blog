Django Ajax and Dojo?
#####################
:date: 2005-07-29 22:21:40

The other day in the #django channel I was msg'd by Alex, a developer
for the `Dojo Javascript toolkit`_. (Have anyone noticed that javascript
toolkits are popping up like crazy?). Well, Alex asked my, "Why are you
using prototype.js for Django Ajax". I told him that I used it for some
other projects and it's simple. He told my to take a look at his
project.

At first glance I thought, "Man, Dojo is much more than what Django Ajax
needs." It looked over complicated and I just didn't want to get into
figuring out how this thing works. (It was probably late at night). All
I thought that Django Ajax needed was a simple ajax library. I told
Alex, "Dojo looks like overkill for my needs." He responded by saying,
"This maybe true, but people are going to want this." I thought he was
just trying to push his project. Man was I wrong...

Today I took a second look at Dojo because MochiKit was released and it
had a reference to Dojo on their site. The other day I looked at this
page, `Fast Widget Authoring`_, but I didn't really read it because it
didn't think it pertained to DjAj's needs. Today I actually took the
time to the page and... Damn... This is cool shit!. The first thing I
thought was, "This looks a lot like how Django does things...". Dojo
**IS** for Javascript, what Django is for Python web development. This
is going to be big.

If you read the article, you will see what Dojo does. Basically it
allows you to create packaged javascript components using html and css.
No more, innerHTML-String Splicing crap, no more DOM appendChild, blah,
blah, blah, well not as much anyhow.

I'm going to be playing with Dojo a little and most likely integrate
Django Ajax with it. Happy Hacking...

.. _Dojo Javascript toolkit: http://dojotoolkit.org/
.. _Fast Widget Authoring: http://dojotoolkit.org/fast_widget_authoring.html
