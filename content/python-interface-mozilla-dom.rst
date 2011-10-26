python interface to the mozilla DOM
###################################
:date: 2008-02-08 14:39:38
:tags: amazing, javascript, python

Glenn Franxman and I were brain storming on how to do unittesting with a real browser DOM with working javascript.  Basically everything accessible to the browser could be accessible to python

I ran across this post: http://ejohn.org/blog/bringing-the-browser-to-the-server/ where he uses Rhino and a custom window library to mimic the interface of the window: 
http://jqueryjs.googlecode.com/svn/trunk/jquery/build/runtest/env.js

He's using Rhino which is a java engine... It would suprise me if Spidermonkey, which as python bindings, would not work.

*Update* the env.js library has bindings to java classes so it won't work... I'll have to create an interface to those.