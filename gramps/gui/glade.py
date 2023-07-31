#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Gerald Britton <gerald.britton@gmail.com>
#
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# ------------------------------------------------------------------------
#
# Glade
#
# ------------------------------------------------------------------------

"""
Glade file operations

This module exports the Glade class.

"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import sys
import os
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GLADE_DIR, GRAMPS_LOCALE as glocale
from gramps.gen.constfunc import is_quartz

# ------------------------------------------------------------------------
#
# Glade class. Derived from Gtk.Builder
#
# ------------------------------------------------------------------------


class Glade(Gtk.Builder):
    """
    Glade class: Manage glade files as Gtk.Builder objects
    """

    __slots__ = ["__toplevel", "__filename", "__dirname"]

    def __init__(self, filename=None, dirname=None, toplevel=None, also_load=[]):
        """
        Class Constructor: Returns a new instance of the Glade class

        :type  filename: string or None
        :param filename: The name of the glade file to be used. Defaults to None
        :type  dirname: string or None
        :param dirname: The directory to search for the glade file. Defaults to
                    None which will cause a search for the file in the default
                    directory followed by the directory of the calling module.
        :type  toplevel: string or None
        :param toplevel: The toplevel object to search for in the glade file.
                     Defaults to None, which will cause a search for a toplevel
                     matching the supplied name.
        :type  also_load: list of strings
        :param also_load: Additional toplevel objects to load from the glade
                     file.  These are typically liststore or other objects
                     needed to operate the toplevel object.
                     Defaults to [] (empty list), which will not load
                     additional objects.
        :rtype:   object reference
        :returns:  reference to the newly-created Glade instance

        This operates in two modes; when no toplevel parameter is supplied,
        the entire Glade file is loaded. It is the responsibility of the user
        to make sure ALL toplevel objects are destroyed.

        When a toplevel parameter is supplied, only that object and any
        additional objects requested in the also_load parameter are loaded.
        The user only has to destroy the requested toplevel objects.
        """
        Gtk.Builder.__init__(self)
        self.set_translation_domain(glocale.get_localedomain())

        filename_given = filename is not None
        dirname_given = dirname is not None

        # if filename not given, use module name to derive it

        if not filename_given:
            filename = sys._getframe(1).f_code.co_filename
            filename = os.path.basename(filename)
            filename = filename.rpartition(".")[0] + ".glade"
            filename = filename.lstrip("_").lower()

        # if dirname not given, use current directory

        if not dirname_given:
            dirname = sys._getframe(1).f_code.co_filename
            dirname = os.path.dirname(dirname)

        # try to find the glade file

        if filename_given and dirname_given:  # both given -- use them
            path = os.path.join(dirname, filename)

        elif filename_given:  # try default directory first
            path = os.path.join(GLADE_DIR, filename)
            if not os.path.exists(path):  # then module directory
                path = os.path.join(dirname, filename)

        elif dirname_given:  # dirname given -- use it
            path = os.path.join(dirname, filename)

        # neither filename nor dirname given.  Try:
        # 1. derived filename in default directory
        # 2. derived filename in module directory

        else:
            path = os.path.join(GLADE_DIR, filename)
            if not os.path.exists(path):
                path = os.path.join(dirname, filename)

        # try to build Gtk objects from glade file.  Let exceptions happen

        self.__dirname, self.__filename = os.path.split(path)

        # try to find the toplevel widget

        # toplevel is given
        if toplevel:
            loadlist = [toplevel] + also_load
            with open(path, "r", encoding="utf-8") as builder_file:
                data = builder_file.read()
                if is_quartz():
                    data = data.replace("GDK_CONTROL_MASK", "GDK_META_MASK")
                self.add_objects_from_string(data, loadlist)
            self.__toplevel = self.get_object(toplevel)
        # toplevel not given
        else:
            with open(path, "r", encoding="utf-8") as builder_file:
                data = builder_file.read()
                if is_quartz():
                    data = data.replace("GDK_CONTROL_MASK", "GDK_META_MASK")
                self.add_from_string(data)
            # first, use filename as possible toplevel widget name
            self.__toplevel = self.get_object(filename.rpartition(".")[0])

            # next try lowercase filename as possible widget name
            if not self.__toplevel:
                self.__toplevel = self.get_object(filename.rpartition(".")[0].lower())

                if not self.__toplevel:
                    # if no match found, search for first toplevel widget
                    for obj in self.get_objects():
                        if hasattr(obj, "get_toplevel"):
                            self.__toplevel = obj.get_toplevel()
                            break
                    else:
                        self.__toplevel = None

    def __get_filename(self):
        """
        __get_filename: return filename of glade file
        :rtype:   string
        :returns:  filename of glade file
        """
        return self.__filename

    filename = property(__get_filename)

    def __get_dirname(self):
        """
        __get_dirname: return directory where glade file found
        :rtype:   string
        :returns:  directory where glade file found
        """
        return self.__dirname

    dirname = property(__get_dirname)

    def __get_toplevel(self):
        """
        __get_toplevel: return toplevel object
        :rtype:   object
        :returns:  toplevel object
        """
        return self.__toplevel

    def __set_toplevel(self, toplevel):
        """
        __set_toplevel: set toplevel object

        :type  toplevel: string
        :param toplevel: The name of the toplevel object to use
        """
        self.__toplevel = self.get_object(toplevel)

    toplevel = property(__get_toplevel, __set_toplevel)

    def get_child_object(self, value, toplevel=None):
        """
        get_child_object: search for a child object, by name, within a given
                          toplevel.  If no toplevel argument is supplied, use
                          the toplevel attribute for this instance
        :type  value: string
        :param value: The name of the child object to find
        :type  toplevel: string
        :param toplevel: The name of the toplevel object to us
        :rtype:   object
        :returns:  child object
        """
        if not toplevel:
            toplevel = self.__toplevel
            if not toplevel:
                raise ValueError("Top level object required")

        if isinstance(toplevel, str):
            toplevel = self.get_object(toplevel)

        # Simple Breadth-First Search

        queue = [toplevel]
        while queue:
            obj = queue.pop(0)
            obj_id = Gtk.Buildable.get_name(obj)
            if obj_id == value:
                return obj
            if hasattr(obj, "get_children"):
                queue += obj.get_children()

        return None
