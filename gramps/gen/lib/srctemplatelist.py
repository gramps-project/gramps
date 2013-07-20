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

class SrcTemplateList(object):
    """
    Manages a singleton list of the source templates.
    
    This should be replaced by access to the database when the templates are
    stored in the database.
    
    I would expect the TemplateList object to contain a dictionary of Template
    objects, with the template ID as a key.  It needs a method to return a list
    of keys, and another method to return the Template object for a given key.
    In this way it would act like a database table.
    """
    __metaclass__ = Singleton
    def __init__(self):
        self.template_list = {}
        
    def add_template(self, handle, template):
        self.template_list[handle] = template
        
    def get_template_from_name(self, name):
        # N.B. names can be ambiguous; it is better to use the handles which are
        # guaranteed o be unique. This method returns the first matching
        # template it finds.
        
        # Match processing in old set_template_key()
        gedtempl = None
        if name == 'UNKNOWN':
            name = 'GEDCOM'
        for template in self.template_list.itervalues():
            if template.get_name() == name:
                return template
            if template.get_name() == 'GEDCOM':
                gedtempl = template
        # Return the GEDCOM template if one was found
        return gedtempl

    def get_template_from_handle(self, handle):
        return self.template_list[handle]

    def get_template_list(self):
        return self.template_list
    
    def template_defined(self, name):
        if self.get_template_from_name(name) is None:
            return False
        else:
            return True
