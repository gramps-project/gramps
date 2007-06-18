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
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Filters.Rules._Rule import Rule

#-------------------------------------------------------------------------
#
# HasNameOf
#
#-------------------------------------------------------------------------
class HasNameOf(Rule):
    """Rule that checks for full or partial name matches"""

    labels      = [ _('Given name:'),
                    _('Family name:'),
                    _('Suffix:'),
                    _('person|Title:')]
    name        = _('People with the <name>')
    description = _("Matches people with a specified (partial) name")
    category    = _('General filters')

    def apply(self,db,person):
        self.f = self.list[0]
        self.l = self.list[1]
        self.s = self.list[2]
        self.t = self.list[3]
        for name in [person.get_primary_name()] + person.get_alternate_names():
            val = 1
            if self.f and name.get_first_name().upper().find(self.f.upper()) == -1:
                val = 0
            if self.l and name.get_surname().upper().find(self.l.upper()) == -1:
                val = 0
            if self.s and name.get_suffix().upper().find(self.s.upper()) == -1:
                val = 0
            if self.t and name.get_title().upper().find(self.t.upper()) == -1:
                val = 0
            if val == 1:
                return True
        return False
