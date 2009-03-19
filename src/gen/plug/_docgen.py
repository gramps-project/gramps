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
# $Id: $

"""
This module provides the Plugin class for document generator plugins.
"""

from gen.plug import Plugin
import BaseDoc

class DocGenPlugin(Plugin):
    """
    This class represents a plugin for generating documents from Gramps
    """
    def __init__(self, name, description, basedoc, paper, style, extension):
        """
        @param name: A friendly name to call this plugin.
            Example: "Plain Text"
        @type name: string
        @param description: A short description of the plugin.
            Example: "This plugin will generate text documents in plain text."
        @type description: string
        @param basedoc: A class that implements the BaseDoc.BaseDoc 
            interface.
        @type basedoc: BaseDoc.BaseDoc
        @param paper: Indicates whether the plugin uses paper or not.
            True = use paper; False = do not use paper
        @type paper: bool
        @param style: Indicates whether the plugin uses styles or not.
            True = use styles; False = do not use styles
        @type style: bool
        @param extension: The extension for the output file.
            Example: "txt"
        @type extension: str
        @return: nothing
        """
        Plugin.__init__(self, name, description, basedoc.__module__)
        self.__basedoc = basedoc
        self.__paper = paper
        self.__style = style
        self.__extension = extension
    
    def get_basedoc(self):
        """
        Get the BaseDoc class for this plugin.
        
        @return: the BaseDoc.BaseDoc class passed into __init__ 
        """
        return self.__basedoc
    
    def get_paper_used(self):
        """
        Get the paper flag for this plugin.
        
        @return: bool - True = use paper; False = do not use paper
        """
        return self.__paper
    
    def get_style_support(self):
        """
        Get the style flag for this plugin.
        
        @return: bool - True = use styles; False = do not use styles
        """
        return self.__style
    
    def get_extension(self):
        """
        Get the file extension for the output file.
        
        @return: str
        """
        return self.__extension

    def get_text_support(self):
        """
        Check if the plugin supports the BaseDoc.TextDoc interface.
        
        @return: bool: True if TextDoc is supported; False if TextDoc is not 
            supported.
        """
        return bool(issubclass(self.__basedoc, BaseDoc.TextDoc))

    def get_draw_support(self):
        """
        Check if the plugin supports the BaseDoc.DrawDoc interface.
        
        @return: bool: True if DrawDoc is supported; False if DrawDoc is not 
            supported.
        """
        return bool(issubclass(self.__basedoc, BaseDoc.DrawDoc))