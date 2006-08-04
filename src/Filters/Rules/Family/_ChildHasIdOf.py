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

# $Id: _HasNameOf.py 6529 2006-05-03 06:29:07Z rshura $

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
from Filters.Rules import HasGrampsId

#-------------------------------------------------------------------------
#
# HasNameOf
#
#-------------------------------------------------------------------------
class ChildHasIdOf(HasGrampsId):
    """Rule that checks for a person with a specific GRAMPS ID"""

    labels      = [ _('Person ID:') ]
    name        = _('Families with child with the <Id>')
    description = _("Matches familis where child has a specified "
                    "GRAMPS ID")
    category    = _('Child filters')

    def apply(self,db,family):
        for child_ref in family.get_child_ref_list():
            child = db.get_person_from_handle(child_ref.ref)
            if HasGrampsId.apply(self,db,child):
                return True
        return False
