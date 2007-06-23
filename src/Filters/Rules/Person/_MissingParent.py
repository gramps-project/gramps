#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007 Johan Gronqvist (johan.gronqvist@gmail.com)
# copyright (C) 2007 Brian G. Matherly
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
# "People with less than 2 parents"
#-------------------------------------------------------------------------
class MissingParent(Rule):
    """People with less than two parents"""

    name        = _('People missing parents')
    description = _("Matches people that are children"
                    " in a family with less than two parents"
                    " or are not children in any family.")
    category    = _('Family filters')

    def apply(self,db,person):
        families = person.get_parent_family_handle_list()
        if families == []:
            return True
        for family_handle in person.get_parent_family_handle_list():
            family = db.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()
            if not father_handle: 
                return True
            if not mother_handle:
                return True
        return False
        
