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
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Rule
#
#-------------------------------------------------------------------------
class Rule:
    """Base rule class"""

    labels      = []
    name        = ''
    category    = _('Miscellaneous filters')
    description = _('No description')

    def __init__(self,list):
        self.set_list(list)

    def is_empty(self):
        return False
    
    def prepare(self,db):
        pass

    def reset(self):
        pass

    def set_list(self,list):
        assert type(list) == type([]) or list == None, "Argument is not a list"
        assert len(list) == len(self.labels), \
               "Number of arguments does not match number of labels.\n"\
               "list: %s\nlabels: %s" % (list,self.labels)
        self.list = list

    def values(self):
        return self.list
    
    def check(self):
        return len(self.list) == len(self.labels)

    def apply(self,db,person):
        return True

    def display_values(self):
        v = [ '%s="%s"' % (_(self.labels[ix]),_(self.list[ix]))
              for ix in range(0,len(self.list)) if self.list[ix] ]

        return ';'.join(v)
