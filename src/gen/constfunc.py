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
perform a translation on import, eg gtk.
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
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.const import WINDOWS, MACOS, LINUX

#-------------------------------------------------------------------------
#
# Public Functions
#
#-------------------------------------------------------------------------

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
            import gtk
        except:
            return False
        return gtk.gdk.WINDOWING == "quartz"
    return False

def has_display():
    """
    Tests to see if Python is currently running with gtk 
    """
    # FIXME: currently, gtk.init_check() requires all strings
    # in argv, and we might have unicode.
    temp, sys.argv = sys.argv, sys.argv[:1]
    try:
        import gtk
    except:
        return False
    try:
        gtk.init_check()
        sys.argv = temp
        return True
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
