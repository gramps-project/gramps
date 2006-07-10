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

# $Id: _HasAttribute.py 6529 2006-05-03 06:29:07Z rshura $

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
# HasAttribute
#
#-------------------------------------------------------------------------
class HasRelType(Rule):
    """Rule that checks for a person with a particular personal attribute"""

    labels      = [ _('Relationship Type:') ]
    name        = _('Family with the relationship type')
    description = _("Matches family with the relationship type "
                    "of a particular value")
    category    = _('General filters')

    def apply(self, db, obj):
        if not self.list[0]:
            return False
        else:
            return obj.get_relationship() == self.list[0]
