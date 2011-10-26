How Beryl/XGL and Deskbar simplified my life
############################################
:date: 2006-10-25 07:55:35

`|Screenshot of my simple gnome|`_ Screenshot of my current desktop

Yesterday I was playing with Gnome's basic layout and I decided because
`Deskbar`_ was so good at locating what I wanted that it was quicker to
use Deskbar than the standard Gnome application list. I decided to take
things farther and remove some key GUI standards from my screen because
I found that using alternative methods of accomplishing the same thing
were quicker.

Removed the Application Menu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First I removed the application menu in favor of using Deskbar. It's
much quicker to hit the Deskbar keyboard shortcut and type out "web" or
"mail" to launch Firefox or Evolution. The application menu is still
accessible by pressing Alt-F1. The benefit of ALT-F1 is that it opens
the menu where the cursor is. This reduces the amount of movement the
mouse has to do to accomplish the same thing. I'm also able to use the
arrow keys to choose an item in the application menu

Replaced the Run Dialog with Deskbar by Mapping it to Alt-F2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Normally the run dialog is mapped to the shortcut Alt-F2. Because
Deskbar includes the ability to run an application by the executable
name, there was a overlap of functionality between the run dialog and
Deskbar. Replacing the run dialog with Deskbar does not remove any
functionality. In fact Deskbar gives me more functionality.

Removed the Standard Gnome Window List
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`|Example of the Scaling Plugin|`_ Scaling Plugin

I removed the standard Gnome Window List in favor of Beryl's Scale
plugin. Beryl's Scale functionality resembles OSX's Expose
functionality. Because the Scale plugin displays all the windows
currently open and unminimized at a keypress, I can quickly find the
window I want visually and select it either with the mouse or with the
arrow keys.

The one flaw I had always found with the window list is once you get
more than five windows open, you can no longer see the window title and
easily identify the window you want. What also tends to happen is when I
have multiple windows open, the only thing I can see is the logo of the
window and no more. This makes it extremely difficult to find a window.

Another problem is when I have multiple Gnome Terminal windows open. The
title bar with Gnome Terminal is usually the current directory I am
working in. Trying to find the window by the current working directory
is not enough to determine the correct window and I end up clicking a
number terminals before finding the correct one. Being able to see all
the windows currently open, I can see the terminal that resembles the
shell I'm looking for.

Change My Perception of "Minimize"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because I no longer have a window list in my panel, I can no longer
easily find windows that I've minimized. The solution I found to
alleviate this problem is to change my perception of what minimize is
used for.

Instead of using minimize to put the window in the window list but not
on my screen I now think of it as hiding the window. To find the window,
I added the window selector applet to my main panel. That way I can find
the window I hid.

Fitts' law
~~~~~~~~~~

`Fitts law`_ is a well know model in ergonomics and user interfaces.
Granted I'm not a usability expert by no means but I doubt you have to
be one to understand Fitts. This is an over simplification of the law,
but I'll try to explain it. When it applies to the mouse cursor, Fitts'
law says that the time to hit a target is related to the target's size
and the distance from the starting point.

For instance moving the mouse from the center of the screen to a target
a hundred pixels to the right takes a certain amount of time. The size
of the target also plays a part because a large target is easier to put
the cursor on than a small target. With a small target you have to be
careful not to overshoot the target and therefore you have to slow down
when you get near the target.

Another principle of Fitts' Law is if the target is in a location where
you cannot overshoot, you do not have to slow down to hit it regardless
of it's size. The target is thought to have an infinite size and
therefore it is easier and quicker to hit the bottom of the screen than
it is to hit a 64x64 size icon sitting 10 pixels from the bottom of the
screen. This principle is a key reason for Apple putting the menus for
applications on the top of the screen as opposed to within the window
like Windows/Gnome/KDE does.

The key way to understand the application of Fitts law is to understand
that it only applies to one dimension at time. The distance is either
horizontal or vertical. Even though you may move the mouse diagonal to
reach a target there is actually two distances in play. You are both
moving the mouse horizontally and vertically when you move it
diagonally.

How Fitts' Law is used on my desktop

Though you can't see most of the applications of Fitts in the my
screenshot, it is used in a few places:

#. The window selector panel applet that I use to locate hidden
   (minimized) windows is located in the topp left. This gives window
   selector icon infinite width and height because it's in the corner.
   If I'm too low and continue to move the mouse cursor to the left past
   the left edge of the screen the cursor will slide upwards into the
   corner.
#. The Scale plugin is activated by simply moving the cursor to anywhere
   on bottom edge of the screen. This gives that target an infinite
   height because the target is on the bottom and an infinite width
   because it doesn't matter where on the bottom I hit. All I have to do
   is fling the cursor to the bottom of the screen and I see all my
   visible windows.
#. Deskbar is on the top center of the screen. While I generally use the
   shortcut to access Deskbar. Putting it on the top of the screen gives
   it an infinite height. It is also in the center of the panel,
   although this does not give it a infinate width, it substantially
   increasses the ease of hitting the target. Having the deskbar applet
   in the center makes the max distance horizontally no more than half
   the screen minus the width of the Destbar applet. If the deskbar was
   on the left or right side of the panel the max distance horizontally
   would be the width of the screen minus the width of the deskbar
   applet. I also made the width of the deskbar applet nearly 50% of the
   screen. 90% of the time the cursor would be between the second
   quarter and fourth quarter the of the screen. So the max distance
   horizontally is essentially zero because more often than not I would
   not have to move the cursor horizontally to get to the deskbar.
   Moments when my cursor is within the 1st quarter or the 4th quarter
   of the screen, the max distance my mouse would have to travel would
   be a quarter of the screen.
#. The Scaling plugin has the ability to display only windows from a
   single application, all applications on the current virtual desktop,
   and all windows. I've mapped the "Show all windows of a single
   application" function to the top right of the screen so that it has
   infinite width and height. This is good when I have multiple Firefox
   windows open.

The Fitts Optimized Targets All Have Keyboards Shortcuts to reduce hand
movement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I am a Dvorak keyboard user and a huge fan of Ratpoison. The main goal
of both the Dvorak layout and Ratpoison is to reduce the movement of
your hands. It takes a lot of time, both physically and mentally to
switch from keyboard mode to mouse mode and vice-versa.

While I probably use the keyboard more than the average joe, it's no
secret that we live in a point and click world. It's common for me to be
surfing the web and need to switch to another window. Hence the Fitts
optimized trigger for the scale plugin. It's also not uncommon for me to
be hacking away in Emacs and need to switch to another window. It would
be a waste of energy to move my hand from the keyboard, grab the mouse
and fling it to the bottom to see all the windows.

To minimize the movement of my hand from the keyboard to the mouse and
back again, all areas of the screen that were chosen because they are
Fitts optimized to reduce mouse movement have a keyboard shortcut to
reduce hand movement.

If I decide I want to choose another window while my hand is on the
mouse, I simply fling the cursor to the bottom and select the window
with the mouse cursor. If I have my fingers on the keyboard, I simple
hit F8 and use the arrow keys to select the window I want.

Decreased the importance of the Desktop
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Normally the Nautilus file browser is the central application when
interacting with the computer. I deactivate the icons on the desktop
with gconf . There are three reasons for me to do this. The first reason
is I wanted to use Nautilus like any other application. The second
reason is the desktop usually gets cluttered with files, the third
reason is that there is an easier way of accessing your files than
desktop icons.

To prevent the clutter, I took a cue from Windows and OSX and created a
number of folders in my Desktop folder:

#. **Applications**, these are user installed applications that would
   normally go in opt if installed system wide. Applications like
   Songbird, Opera, Limewire go in here.
#. **Reference**, the idea for this folder was taken from "Getting
   Things Done". It holds all kinds of reference information, generally
   saved documents that will need to be referenced later. I avoided
   calling it the vague term, "Documents", because a document could be
   anything. The name "Reference" defines the purpose of these files.
#. **Media**, obviously media files. This has subfolders to keep this
   folder from getting cluttered

#. **Images**

   #. **Photos**, actual photos taken from my camera
   #. **Illustrations**, Vector based images
   #. **Backgrounds**, I seperate backgrounds from photos or
      illustrations because backgrounds are generally novalties. The
      name "Backgrounds" also describes the purpose of these files.
   #. **Novalites**, Images that completely pointless but funny

#. **Videos**

   #. **Movies**, Full length movies that I've ripped from DVDs
   #. **TV Episodes**, TV episodes that I've downloaded
   #. **Novalties**, Novalties items like silly you tube videos of
      people falling over or cats attacking cealing fans. Basically
      mental junk food.

With these folders I've created bookmarks in Nautilus so that I can
easily access these folders from, the nautilus side bar, choose/save
file dialog or deskbar's "File and File Bookmarks" plugin.

The reason why this is easier use than using the desktop for storing
files is that it's quicker to get to the files you need using deskbar.

The normal way to access the desktop is that you need to either use the
show desktop icon, or use the beryl show desktop plugin. Once you get to
the desktop, if you keep all your stuff on the desktop, you're done, but
you have a cluttered desktop.

If you keep all your stuff in sub folders of the desktop, you need first
locate the subfolder on the desktop, then locate the files in that
folder. It's a multistep process.

Using Nautilus bookmarks and the "Find File and File Bookmarks" deskbar
applet is that to get to the subfolder that's on the desktop, it's a two
step process: Click on deskbar and type subfolder name. The normal way
would be: Show the desktop, locate the folder, open the folder. It may
seem like a one extra step, but the time it takes to locate the folder
takes longer to do than typing in the name. You could say that the old
method is two steps more because typing a name is so much quicker than
scanning the desktop for an icon

Limitations
~~~~~~~~~~~

Although I think that this setup is great, and it's optimized allow me
to do many of my common tasks with very little effort and energy, there
are a few flaws. This set up is also only a day old and I'm sure I'll
find others. I'll append this section with any that I find.

#. Once the Gnome Volume Manager (the thing that monitors the system for
   removable media) mounts a drive, I can not unmount the drive from
   Nautilus. The only way that Gnome made it possible to unmount
   removable media is by the desktop icon. I'm sure that there is a way
   to umount a drive with some sort of panel applet but for the moment,
   I simply run "pumount [mount point]" in the terminal.
#. When deskbar hangs, I can no longer launch anything. The solution
   I've found is to hit ALT-F1, open up the application menu, open
   terminal, and kill deskbar.

.. _|image2|: http://eric.themoritzfamily.com/wp-content/uploads/2006/10/Screenshot.png
.. _Deskbar: http://raphael.slinckx.net/deskbar/
.. _|image3|: http://eric.themoritzfamily.com/wp-content/uploads/2006/10/Screenshot-1.png
.. _Fitts law: http://blogs.msdn.com/jensenh/archive/2006/08/22/711808.aspx
.. _|Screenshot of my simple gnome|: http://eric.themoritzfamily.com/wp-content/uploads/2006/10/Screenshot.png
.. _|Example of the Scaling Plugin|: image:: http://eric.themoritzfamily.com/wp-content/uploads/2006/10/Screenshot-1.png
.. |Screenshot of my simple gnome| image:: http://eric.themoritzfamily.com/wp-content/uploads/2006/10/Screenshot.thumbnail.png
.. |Example of the Scaling Plugin| image:: http://eric.themoritzfamily.com/wp-content/uploads/2006/10/Screenshot-1.thumbnail.png
.. |image2| image:: http://eric.themoritzfamily.com/wp-content/uploads/2006/10/Screenshot.thumbnail.png
.. |image3| image:: http://eric.themoritzfamily.com/wp-content/uploads/2006/10/Screenshot-1.thumbnail.png
