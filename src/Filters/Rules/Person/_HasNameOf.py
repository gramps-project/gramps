#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
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
from gen.ggettext import sgettext as _

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
                    _('person|Title:'),
                    _('Prefix:'),
                    _('Patronymic:'),
                    _('Call Name:'),]
    name        = _('People with the <name>')
    description = _("Matches people with a specified (partial) name")
    category    = _('General filters')

    def apply(self,db,person):
        self.firstn = self.list[0]
        self.lastn = self.list[1]
        self.surn = self.list[2]
        self.title = self.list[3]
        self.prefix = self.list[4]
        self.patr = self.list[5]
        self.calln = self.list[6]
        for name in [person.get_primary_name()] + person.get_alternate_names():
            val = 1
            if self.firstn and name.get_first_name().upper().find(self.firstn.upper()) == -1:
                val = 0
            if self.lastn and name.get_surname().upper().find(self.lastn.upper()) == -1:
                val = 0
            if self.surn and name.get_suffix().upper().find(self.surn.upper()) == -1:
                val = 0
            if self.title and name.get_title().upper().find(self.title.upper()) == -1:
                val = 0
            if self.prefix and name.get_prefix().upper().find(self.prefix.upper()) == -1:
                val = 0
            if self.patr and name.get_patronymic().upper().find(self.patr.upper()) == -1:
                val = 0
            if self.calln and name.get_call_name().upper().find(self.calln.upper()) == -1:
                val = 0
            if val == 1:
                return True
        return False
