# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       Benny Malengier
# Copyright (C) 2013       Tim G L Lyons
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
SrcTemplate class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from __future__ import print_function

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger('.template')

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from ..constfunc import cuni

#-------------------------------------------------------------------------
#
#  TemplateElement class
#
#-------------------------------------------------------------------------

class TemplateElement(SecondaryObject):        
    """
    TemplateEelement class.

    This class is for keeping information about each template-element.
    
    TemplateElement:

     - template_element_name - English name of the element exactly as it appears
       in Yates e.g. [WRITER FIRST]

     - name to be displayed in the user interface e.g. 'Name of the first
       author'

     - hint e.g. "Doe, D.P. & Cameron, E."

     - tooltip e.g. "Give names in following form: 'FirstAuthorSurname, Given
       Names & SecondAuthorSurname, Given Names'. Like this Gramps can parse the
       name and shorten as needed."

     - citation - True if this element appears in a citation (false for a source
       element)
       
     - short - True if this element is an optional short element
     
     - short_alg - algorithm to shorten the field.
     
     - list of Mappings - there would always be a GEDCOM mapping. Also we would
       expect a CSL mapping

    """

    def __init__(self, source=None):
        """
        Create a new TemplateEelement instance, copying from the source if present.
        """
        if source:
            self.name = source.name
            self.display = source.display
            self.hint = source.hint
            self.tooltip = source.tooltip
            self.citation = source.citation
            self.short - source.short
            self.short_alg = source.short_alg
        else:
            self.name = ""
            self.display = ""
            self.hint = ""
            self.tooltip = ""
            self.citation = False
            self.short = False
            self.short_alg = ""
        
    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (self.name,
                self.display,
                self.hint,
                self.tooltip,
                self.citation,
                self.short,
                self.short_alg
               )

    def to_struct(self):
        """
        Convert the data held in this object to a structure (eg,
        struct) that represents all the data elements.
        
        This method is used to recursively convert the object into a
        self-documenting form that can easily be used for various
        purposes, including diffs and queries.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns a struct containing the data of the object.
        :rtype: dict
        """
        return {"name": cuni(self.name),
                "display": cuni(self.display),
                "hint": cuni(self.hint),
                "tooltip": cuni(self.tooltip),
                "citation": cuni(self.citation),
                "short": cuni(self.short),
                "short_alg": cuni(self.short_alg),
                }

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (self.name, self.display, self.hint, self.tooltip, self.citation,
         self.short, self.short_alg) = data
        return self

    def get_name(self):
        """
        Return the name for the Template element.
        """
        return self.name

    def set_name(self, name):
        """
        Set the name for the Template element according to the given argument.
        """
        self.name = name

    def get_hint(self):
        """
        Return the hint for the Template element.
        """
        return self.hint

    def set_hint(self, hint):
        """
        Set the hint for the Template element according to the given argument.
        """
        self.hint = hint

    def get_display(self):
        """
        Return the display form for the Template element.
        """
        return self.display

    def set_display(self, display):
        """
        Set the display form for the Template element according to the given
        argument.
        """
        self.display = display
        
    def get_tooltip(self):
        """
        Return the tooltip for the Template element.
        """
        return self.tooltip

    def set_tooltip(self, tooltip):
        """
        Set the tooltip for the Template element according to the given argument.
        """
        self.tooltip = tooltip
        
    def get_citation(self):
        """
        Return the citation for the Template element.
        """
        return self.citation

    def set_citation(self, citation):
        """
        Set the citation for the Template element according to the given argument.
        """
        self.citation = citation
        
    def get_short(self):
        """
        Return the short for the Template element.
        """
        return self.short

    def set_short(self, short):
        """
        Set the short for the Template element according to the given argument.
        """
        self.short = short
        
    def get_short_alg(self):
        """
        Return the short_alg for the Template element.
        """
        return self.short_alg

    def set_short_alg(self, short_alg):
        """
        Set the short_alg for the Template element according to the given argument.
        """
        self.short_alg = short_alg
