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

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import warnings
import functools

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
    conv_to_unicode = unicode
    conv_to_unicode_direct = unicode
    STRTYPE = basestring
    UNITYPE = unicode
else:
    def conv_to_unicode(x, y):
        if isinstance(x, str):
            return x
        else:
            return x.decode(y)
    conv_to_unicode_direct = str
    STRTYPE = str
    UNITYPE = str
cuni = conv_to_unicode_direct

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
    except:
        return False
    try:
        test = Gtk.init_check(temp)
        sys.argv = temp
        if test:
            return True
        else:
            return False
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

#-------------------------------------------------------------------------
#
# DECORATORS
#
#-------------------------------------------------------------------------

def deprecated(func):
    '''This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.'''

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn_explicit(
            "Call to deprecated function {}.".format(func.__name__),
            category=DeprecationWarning,
            filename=func.func_code.co_filename,
            lineno=func.func_code.co_firstlineno + 1
        )
        return func(*args, **kwargs)
    return new_func
