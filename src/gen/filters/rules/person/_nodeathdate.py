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
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.filters.rules._rule import Rule

#-------------------------------------------------------------------------
# "People without a death date"
#-------------------------------------------------------------------------
class NoDeathdate(Rule):
    """People without a death date"""

    name        = _('People without a known death date')
    description = _("Matches people without a known deathdate")
    category    = _('General filters')

    def apply(self,db,person):
        death_ref = person.get_death_ref()
        if not death_ref:
            return True
        death = db.get_event_from_handle(death_ref.ref)
        if death:
            death_obj = death.get_date_object()
            if not death_obj:
                return True
            if death_obj.sortval == 0:
                return True
        return False
