Xubuntu Day 3
#############
:date: 2007-08-02 19:42:53

So it's been three days since I started using XFCE flavored Ubuntu. It's
been a pretty lovely existence, but I have a few tips that's I've come
across

Notification Daemon
~~~~~~~~~~~~~~~~~~~

Stock Xubuntu doesn't come with a notification daemon that works with
XFCE installed. So those little popups that rise out of the task bar in
Gnome don't rise anymore and I end up missing things like new IMs, new
mail notifications, etc. Unfortunately, there is not a package in the
repositories for the xfce friendly notification daemon so you'll have to
compile it yourself. Follow these `instructions`_.

.. _instructions: http://devilsadvocate-chs.blogspot.com/2006/11/libnotify-popups-on-xubuntu-xfce4.html


Mail Notifications
~~~~~~~~~~~~~~~~~~

Since I'm running Xubuntu in VMWare and I need Outlook running so that
Activesync will sync appointments to my Blackjack, It's hard to know
when new emails come in. Luckly, our Exchange server here provides IMAP.
I could run Evolution and get my mail in XFCE, but why should I have two
mail clients running. So what I did was set up two Mail Watcher panel
Applets, one for my corporate email and one for my personal Google Apps
for Domains account.
Unfortunately I was missing emails yesterday because by default, all the
Mail Watcher applet does when new mail comes in is change the icon. This
is what prompted me to get the notification daemon working. Details on
how to tie Mail Watcher and Notifications together are `here`_
By the way, I absolutely love `Google Apps for Domains`_, it's
brilliant. I wrote a little mailto: handler script for my wife's laptop
so that when she clicks on mailto: links anywhere, it opens gmail. I'll
provide that script sometime, it's a little 10 line beauty.

Powered by `ScribeFire`_.

.. _here: http://xubuntublog.wordpress.com/2007/04/27/email-notification/
.. _Google Apps for Domains: https://www.google.com/a/
.. _ScribeFire: http://scribefire.com/
