#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011  Jerome Rapinat
# Copyright (C) 2011  Douglas S. Blank
# Copyright (C) 2011  Benny Malengier
# Copyright (C) 2011       Tim G L Lyons
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
# gen.filters.rules/_MatchesSourceConfidenceBase.py

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from . import Rule

#-------------------------------------------------------------------------
# "Confidence level"
# Sources of an attribute of an event are ignored
#-------------------------------------------------------------------------
class MatchesSourceConfidenceBase(Rule):
    """Objects with a specific confidence level on 'direct' Source references"""

    labels = ['Confidence level:']
    name = 'Object with at least one direct source >= <confidence level>'
    description = "Matches objects with at least one direct source with confidence level(s)"
    category = _('Citation/source filters')

    def apply(self, db, obj):
        required_conf = int(self.list[0])
        for citation_handle in obj.get_citation_list():
            citation = db.get_citation_from_handle(citation_handle)
            if required_conf <= citation.get_confidence_level():
                return True
        return False
