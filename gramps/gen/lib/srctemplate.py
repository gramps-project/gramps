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
from collections import defaultdict

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
from .tableobj import TableObject
from .handle import Handle
from ..constfunc import cuni
from .templateelement import TemplateElement

#-------------------------------------------------------------------------
#
#  SrcTemplate class
#
#-------------------------------------------------------------------------

class SrcTemplate(TableObject):
    """
    Sources conform to a certain template, which governs their styling when 
    used in reports.
    
    The SrcTemplate object holds all the logic to do the actual styling.
    Predefined templates themself are stored in SrcAttributeType, or in extra 
    xml files with defenitions

    The structure typically is a dictionary as follows:
        
        {
            REF_TYPE_L: [
                ('', AUTHOR, '.', EMPTY, False, False, EMPTY, GED_AUTHOR, 'hint', 'tooltip'),
                ('', TITLE, '.', STYLE_QUOTE, False, False, EMPTY, GED_TITLE, '', ''),
                ('', PUB_INFO, '', EMPTY, False, False, EMPTY, GED_PUBINF, '', ''),
                ],
            REF_TYPE_F: [
                ('', AUTHOR, ',', EMPTY, False, False, EMPTY, EMPTY, '', ''),
                ('', TITLE, ',', STYLE_QUOTE, False, False, EMPTY, EMPTY, '', ''),
                ('', PUB_INFO, '.', EMPTY, False, False, EMPTY, EMPTY, '', ''),
                ('', DATE, ' -', EMPTY, False, False, EMPTY, EMPTY, '', ''),
                ('', PAGE6S9, '.', EMPTY, False, False, EMPTY, EMPTY, '', ''),
                ],
            REF_TYPE_S: [
                ('', AUTHOR, ',', EMPTY, False, False, EMPTY, EMPTY, '', ''),
                ('', DATE, ' -', EMPTY, False, False, EMPTY, EMPTY, '', ''),
                ('', PAGE6S9, '.', EMPTY, False, False, EMPTY, EMPTY, '', ''),
                ],
        }
        
        This defines the 3 source reference types. A reference type consists of
        a list of tuples with fieldsdescriptions.
        A fielddescription consists of the columns:
        0/ left delimiter
        1/ field, this is a SrcAttributeType
        2/ right delimiter
        3/ style to use
        4/ bool: if field should be private by default on creation
        5/ bool: if optional field
        6/ shortening algorithm to use, EMPTY indicates no transformation
        7/ the REF_TYPE_L reference maps to GEDCOM fields on export via
           this column. GEDCOM contains Title, Author and Pub.Info field
    """
    
    def __init__(self, template_key=None):
        """
        Create a new Template instance. 
        
        After initialization, most data items have empty or null values,
        including the database handle.
        """
        TableObject.__init__(self)
        self.handle = ""
        self.name = ""
        self.descr = ""
        self.template_element_list = []
        self.mapdict = defaultdict(str)
 
    def serialize(self):
        """
        Convert the data held in the Template to a Python tuple that
        represents all the data elements. 
        
        This method is used to convert the object into a form that can easily 
        be saved to a database.

        These elements may be primitive Python types (string, integers), 
        complex Python types (lists or tuples, or Python objects. If the
        target database cannot handle complex types (such as objects or
        lists), the database is responsible for converting the data into
        a form that it can use.

        :returns: Returns a python tuple containing the data that should
            be considered persistent.
        :rtype: tuple
        """
        return (
            self.handle,
            self.name,
            self.descr,
            [template_element.serialize() for template_element in self.template_element_list],
            self.mapdict
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
        return {"handle": Handle("Srctemplate", self.handle), 
                "name": cuni(self.name),
                "descr": cuni(self.descr),
                "elements": [e.to_struct() for e in self.template_element_list],
                "mapdict" : {'dict': self.mapdict}
                }

    def unserialize(self, data):
        """
        Convert the data held in a tuple created by the serialize method
        back into the data in a SrcTemplate object.

        :param data: tuple containing the persistent data associated the
            SrcTemplate object
        :type data: tuple
        """
        (self.handle,
         self.name,
         self.descr,
         template_element_list,
         self.mapdict,
         ) = data
         
        self.template_element_list = [TemplateElement().unserialize(te)
                                      for te in template_element_list]
        return self
    
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name
        
    def get_descr(self):
        return self.descr
    
    def set_descr(self, descr):
        self.descr = descr
        
    def get_map_dict(self):
        """Return the map for the template"""
        return self.mapdict
    
    def set_map_dict(self, templmap):
        """Set the map for the template"""
        self.mapdict = templmap
    
    def set_map_element(self, key, value):
        self.mapdict[key] =  value
        
    def get_map_element(self, key):
        return self.mapdict[key]
        
    def get_template_element_list(self):
        return self.template_element_list
    
    def set_template_element_list(self, template_element_list):
        self.template_element_list = template_element_list

    def add_template_element(self, template_element):
        self.template_element_list.append(template_element)
