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
SrcTemplateList class for GRAMPS.
"""

from __future__ import print_function

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import sys

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

# Pattern from http://stackoverflow.com/questions/13789235/how-to-initialize-singleton-derived-object-once
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# See http://stackoverflow.com/questions/17237857/python3-singleton-metaclass-
# method-not-working the syntax has changed

# http://mikewatkins.ca/2008/11/29/python-2-and-3-metaclasses/
# http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python/17840539
STL = Singleton('STL', (object, ), {})

class SrcTemplateList(STL):
    """
    Manages a singleton list of the source templates.
    
    This should be replaced by access to the database when the templates are
    stored in the database.
    
    I would expect the TemplateList object to contain a dictionary of Template
    objects, with the template ID as a key.  It needs a method to return a list
    of keys, and another method to return the Template object for a given key.
    In this way it would act like a database table.
    """
#    __metaclass__ = Singleton
    def __init__(self):
        self.clear()
        
    def clear(self):
        self.template_list = {}
        self.GEDCOM_handle = None
        self.UNKNOWN_handle = None

    def add_template(self, handle, template):
        self.template_list[handle] = template
        
#    def get_template_from_handle(self, handle):
#        if handle in self.template_list:
#            return self.template_list[handle]
#        else:
#            return self.template_list[self.get_UNKNOWN_handle()]

#    def get_template_list(self):
#        return self.template_list
#    
#    def template_defined(self, handle):
#        if self.get_template_from_handle(handle) is None:
#            return False
#        else:
#            return True
#
#    def set_GEDCOM_handle(self, handle):
#        self.GEDCOM_handle = handle
#        
#    def get_GEDCOM_handle(self):
#        return self.GEDCOM_handle
#
#    def set_UNKNOWN_handle(self, handle):
#        self.UNKNOWN_handle = handle
#        
#    def get_UNKNOWN_handle(self):
#        return self.UNKNOWN_handle
