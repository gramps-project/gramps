#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Brian G. Matherly
# Copyright (C) 2009       Peter G. Landgren
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Some independent constants/functions that can be safely imported
without any translation happening yet.  Do _not_ add imports that will
perform a translation on import, eg Gtk.
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import platform
import sys
import ctypes
import os

#-------------------------------------------------------------------------
#
# Platforms
# Never test on LINUX, handle Linux in the else statement as default
#
#-------------------------------------------------------------------------
LINUX = ["Linux", "linux", "linux2"]
MACOS = ["Darwin", "darwin"]
WINDOWS = ["Windows", "win32"]

#-------------------------------------------------------------------------
#
# Public Functions
#
#-------------------------------------------------------------------------

#python 2 and 3 support, use correct conversion to unicode
if sys.version_info[0] < 3:
    conv_to_unicode_direct = unicode
    STRTYPE = basestring
    UNITYPE = unicode
else:
    conv_to_unicode_direct = str
    STRTYPE = str
    UNITYPE = str
cuni = conv_to_unicode_direct
def conv_to_unicode(x, y='utf8'):
    return x if x is None or isinstance(x, UNITYPE) else cuni(x, y)


# handle in database is bytes, while internally Gramps wants unicode for py3
if sys.version_info[0] < 3:
    handle2internal = lambda x: x
else:
    handle2internal = lambda x: conv_to_unicode(x, 'utf-8')

#-------------------------------------------------------------------------
#
# Platform determination functions
#
#-------------------------------------------------------------------------

def lin():
    """
    Return True if a linux system
    Note: Normally do as linux in else statement of a check !
    """
    if platform.system() in LINUX:
        return True
    return False
    
def mac():
    """
    Return True if a Macintosh system
    """
    if platform.system() in MACOS:
        return True
    return False

def win():
    """
    Return True if a windows system
    """
    if platform.system() in WINDOWS:
        return True
    return False

## The following functions do import gtk, but only when called. They
## should only be called after translation system has been
## initialized!

def is_quartz():
    """
    Tests to see if Python is currently running with gtk and 
    windowing system is Mac OS-X's "quartz".
    """
    if mac():
        try:
            from gi.repository import Gtk
            from gi.repository import Gdk
        except:
            return False
        return Gdk.Display.get_default().__class__.__name__.endswith("QuartzDisplay")
    return False

def has_display():
    """
    Tests to see if Python is currently running with gtk 
    """
    # FIXME: currently, Gtk.init_check() requires all strings
    # in argv, and we might have unicode.
    temp, sys.argv = sys.argv, sys.argv[:1]
    try:
        from gi.repository import Gtk
        from gi.repository import Gdk
    except:
        return False

    try:
        test = Gtk.init_check(temp) and \
            Gdk.Display.get_default()
        sys.argv = temp
        return bool(test)
    except:
        sys.argv = temp
        return False

# A couple of places add menu accelerators using <alt>, which doesn't
# work with Gtk-quartz. <Meta> is the usually correct replacement, but
# in one case the key is a number, and <meta>number is used by Spaces
# (a mac feature), so we'll use control instead.

def mod_key():
    """
    Returns a string to pass to an accelerator map.
    """

    if is_quartz():
        return "<ctrl>"

    return "<alt>"

# Python2 on Windows munges environemnt variables to match the system
# code page. This breaks all manner of things and the workaround
# though a bit ugly, is encapsulated here. Use this to retrieve
# environment variables if there's any chance they might contain
# Unicode, and especially for paths.

# Shamelessly lifted from http://stackoverflow.com/questions/2608200/problems-with-umlauts-in-python-appdata-environvent-variable, answer 1.


def get_env_var(name, default=None):
    if not name or not name in os.environ:
        return default

    if sys.version_info[0] < 3 and win():
        name = unicode(name) # make sure string argument is unicode
        n = ctypes.windll.kernel32.GetEnvironmentVariableW(name, None, 0)
        if n==0:
            return default
        # n is number of codepoints
        buf = ctypes.create_unicode_buffer(n+1)
        ctypes.windll.kernel32.GetEnvironmentVariableW(name, buf, n)
        return buf.value

    return os.environ[name]
    
