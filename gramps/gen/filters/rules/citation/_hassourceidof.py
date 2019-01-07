#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2011-2013  Tim G L Lyons
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .._hasgrampsid import HasGrampsId

#-------------------------------------------------------------------------
#
# HasSourceIdOf
#
#-------------------------------------------------------------------------
class HasSourceIdOf(HasGrampsId):
    """Rule that checks for a citation with a source which has a specific
    Gramps ID"""

    name = _('Citation with Source <Id>')
    description = _("Matches a citation with a source with a specified Gramps "
                    "ID")
    category = _('Source filters')

    def apply(self, dbase, citation):
        source = dbase.get_source_from_handle(
                                    citation.get_reference_handle())
        if HasGrampsId.apply(self, dbase, source):
            return True
        return False
