#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008       Brian G. Matherly
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$

"""
This module provides the Plugin class for import plugins.
"""

from gen.plug import Plugin

class ImportPlugin(Plugin):
    """
    This class represents a plugin for importing data into Gramps
    """
    def __init__(self, name, description, import_function, mime_types=None):
        """
        @param name: A friendly name to call this plugin.
            Example: "GEDCOM Import"
        @type name: string
        @param description: An short description of the plugin.
            Example: "This plugin will import a GEDCOM file into a database"
        @type description: string
        @param import_function: A function to call to perform the import.
            The function must take the form:
                def import_function(db, filename, callback):
            where:
                "db" is a Gramps database to import the data into
                "filename" is the file that contains data to be imported
                "callback" is a callable object that takes two parameters.
                    The first parameter is a progress indicator.
                    The second parameter is a text string.
        @type import_function: callable
        @param mime_types: A list of mime types that apply to the file type.
            Example: "['application/x-gramps']"
        @type mime_types: [str] (list of strings)
        @return: nothing
        """
        Plugin.__init__(self, name, description)
        self.__import_func = import_function
        self.__mime_types = mime_types
    
    def get_module_name(self):
        """
        Get the name of the module that this plugin lives in.
        
        @return: a string representing the name of the module for this plugin
        """
        return self.__import_func.__module__
    
    def get_import_function(self):
        """
        Get the import function for this plugins.
        
        @return: the callable import_function passed into __init__ 
        """
        return self.__import_func
    
    def get_mime_types(self):
        """
        Get the list of mime types that apply to the import file.
        
        @return: [str] (list of strings)
        """
        return self.__mime_types
