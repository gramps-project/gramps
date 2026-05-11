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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Some independent constants/functions that can be safely imported
without any translation happening yet.  Do _not_ add imports that will
perform a translation on import, eg Gtk.
"""

# ------------------------------------------------------------------------
#
# python modules
#
# ------------------------------------------------------------------------
import platform
import sys
import os
from pathlib import Path

# -------------------------------------------------------------------------
#
# Platforms
# Never test on LINUX, handle Linux in the else statement as default
#
# -------------------------------------------------------------------------
LINUX = ["Linux", "linux", "linux2"]
MACOS = ["Darwin", "darwin"]
WINDOWS = ["Windows", "win32"]

# -------------------------------------------------------------------------
#
# Platform determination functions
#
# -------------------------------------------------------------------------


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
            import gi

            gi.require_version("Gtk", "3.0")
            gi.require_version("Gdk", "3.0")
            from gi.repository import Gtk
            from gi.repository import Gdk
        except ImportError:
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
        import gi

        gi.require_version("Gtk", "3.0")
        gi.require_version("Gdk", "3.0")
        from gi.repository import Gtk
        from gi.repository import Gdk
    except ImportError:
        return False

    try:
        test = Gtk.init_check(temp) and Gdk.Display.get_default()
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


def get_env_var(name, default=None):
    """
    Returns the value of the specified environment variable, or default if the variable is not defined.
    """
    if not name or name not in os.environ:
        return default

    return os.environ[name]


def get_curr_dir():
    """
    Returns the current working directory.
    """
    return os.getcwd()


# -------------------------------------------------------------------------
#
# Functions that return base directories as described in the XDG base directory
# specification.
#
# -------------------------------------------------------------------------
def get_user_home_dir():
    """
    Returns the user's home directory.
    """
    return str(Path.home())


def get_user_data_dir():
    """
    Returns a base directory in which to store user-specific application data.
    """
    if win():
        return get_env_var(
            "APPDATA", os.path.join(get_user_home_dir(), "AppData", "Roaming")
        )
    else:
        if "XDG_DATA_HOME" in os.environ:
            return get_env_var("XDG_DATA_HOME")
        return os.path.join(get_user_home_dir(), ".local", "share")


def get_user_config_dir():
    """
    Returns a base directory in which to store user-specific configuration settings.
    """
    if win():
        return get_user_data_dir()
    else:
        if "XDG_CONFIG_HOME" in os.environ:
            return get_env_var("XDG_CONFIG_HOME")
        return os.path.join(get_user_home_dir(), ".config")


def get_user_cache_dir():
    """
    Returns a base directory in which to store temporary cached data.
    """
    if win():
        return os.path.join(
            get_user_home_dir(), "AppData", "Local", "Microsoft", "Windows", "INetCache"
        )
    else:
        if "XDG_CACHE_HOME" in os.environ:
            return get_env_var("XDG_CACHE_HOME")
        return os.path.join(get_user_home_dir(), ".cache")
