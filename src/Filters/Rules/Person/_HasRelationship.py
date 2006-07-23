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
# HasRelationship
#
#-------------------------------------------------------------------------
class HasRelationship(Rule):
    """Rule that checks for a person who has a particular relationship"""

    labels      = [ _('Number of relationships:'),
                    _('Relationship type:'),
                    _('Number of children:') ]
    name        = _('People with the <relationships>')
    description = _("Matches people with a particular relationship")
    category    = _('Family filters')

    def apply(self,db,person):
        rel_type = 0
        cnt = 0
        num_rel = len(person.get_family_handle_list())

        # count children and look for a relationship type match
        for f_id in person.get_family_handle_list():
            f = db.get_family_from_handle(f_id)
            cnt = cnt + len(f.get_child_ref_list())
            if self.list[1] and int(self.list[1]) == f.get_relationship():
                rel_type = 1

        # if number of relations specified
        if self.list[0]:
            try:
                v = int(self.list[0])
            except:
                return False
            if v != num_rel:
                return False

        # number of childred
        if self.list[2]:
            try:
                v = int(self.list[2])
            except:
                return False
            if v != cnt:
                return False

        # relation
        if self.list[1]:
            return rel_type == 1
        else:
            return True
