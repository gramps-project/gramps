#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011  Jerome Rapinat
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
# gen.filters.rules/Family/_MatchesSourceConfidence.py

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .._matchessourceconfidencebase import MatchesSourceConfidenceBase

#-------------------------------------------------------------------------
# "Confidence level"
#-------------------------------------------------------------------------
class MatchesSourceConfidence(MatchesSourceConfidenceBase):
    """Families matching a specific confidence level on its 'direct' source references"""

    labels = [_('Confidence level:')]
    name = _('Families with at least one direct source >= <confidence level>')
    description = _("Matches families with at least one direct source with confidence level(s)")

