# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# enable logging for error handling
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# Rule
#
#-------------------------------------------------------------------------
class Rule(object):
    """Base rule class."""

    labels      = []
    name        = ''
    category    = _('Miscellaneous filters')
    description = _('No description')

    def __init__(self, arg):
        self.set_list(arg)
        self.nrprepare = 0

    def is_empty(self):
        return False
    
    def requestprepare(self, db):
        """
        Request that the prepare method of the rule is executed if needed
        
        Special: Custom Filters have fixed values, so only one instance needs to
        exists during a search. It is stored in a FilterStore, and initialized
        once.
        As filters are can be grouped in a group
        filter, we request a prepare. Only the first time prepare will be
        called
        """
        if self.nrprepare == 0:
            self.prepare(db)
        self.nrprepare += 1

    def prepare(self, db):
        """prepare so the rule can be executed efficiently"""
        pass

    def requestreset(self):
        """
        Request that the reset method of the rule is executed if possible
        
        Special: Custom Filters have fixed values, so only one instance needs to
        exists during a search. It is stored in a FilterStore, and initialized
        once.
        As filters are can be grouped in a group
        filter, we request a reset. Only the last time reset will be
        called
        """
        self.nrprepare -= 1
        if self.nrprepare == 0:
            self.reset()

    def reset(self):
        """remove no longer needed memory"""
        pass
 
    def set_list(self, arg):
        assert isinstance(arg, list) or arg is None, "Argument is not a list"
        if len(arg) != len(self.labels):
               log.warning(("Number of arguments does not match number of labels.\n" +
                            "   list:   %s\n" +
                            "   labels: %s") % (arg,self.labels))
        self.list = arg

    def values(self):
        return self.list
    
    def check(self):
        return len(self.list) == len(self.labels)

    def apply(self, db, person):
        return True

    def display_values(self):
        v = ( '%s="%s"' % (_(self.labels[ix]), self.list[ix])
              for ix in xrange(len(self.list)) if self.list[ix] )

        return ';'.join(v)

    def match_substring(self, param_index, str_var):
        # make str_var unicode so that search for ü works
        # see issue 3188
        str_var = unicode(str_var)
        if self.list[param_index] and \
               (str_var.upper().find(self.list[param_index].upper()) == -1):
            return False
        else:
            return True
