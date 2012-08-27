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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Filters/Rules/Person/_MatchesSourceConfidence.py
# $Id: _MatchesSourceConfidence.py 18361 2011-10-23 03:13:50Z paul-franklin $
#

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
from Filters.Rules._MatchesSourceConfidenceBase import MatchesSourceConfidenceBase

#-------------------------------------------------------------------------
# "Confidence level"
#-------------------------------------------------------------------------
class MatchesSourceConfidence(MatchesSourceConfidenceBase):
    """Media matching a specific confidence level on its 'direct' source references"""

    labels    = [_('Confidence level:')]
    name        = _('Place with direct source >= <confidence level>')
    description = _("Matches places with at least one direct source with confidence level(s)")
