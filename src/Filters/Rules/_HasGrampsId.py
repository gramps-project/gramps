#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2010       Raphael Ackermann
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
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Filters.Rules import Rule

#-------------------------------------------------------------------------
#
# HasIdOf
#
#-------------------------------------------------------------------------
class HasGrampsId(Rule):
    """Rule that checks for an object with a specific GRAMPS ID."""

    labels      = [ _('ID:') ]
    name        = 'Object with <Id>'
    description = "Matches objects with a specified Gramps ID"
    category    = _('General filters')

    def apply(self, db, obj):
        """
        apply the rule on the obj.
        return true if the rule passes, false otherwise.
        """
        return obj.gramps_id == self.list[0]
