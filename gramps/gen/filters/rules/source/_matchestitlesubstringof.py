#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011       Helge Herz
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
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.get_translation().gettext

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .. import Rule

#-------------------------------------------------------------------------
# "Sources having a title that contain a substring"
#-------------------------------------------------------------------------
class MatchesTitleSubstringOf(Rule):
    """Source title containing <substring>"""

    labels      = [ _('Substring:')]
    name        = _('Sources title containing <substring>')
    description = _("Matches sources whose title contains a "
                    "certain substring")
    category    = _('General filters')

    def apply(self, db, source):
        """ Apply the filter """
        title = source.get_title()
        if title.upper().find(self.list[0].upper()) != -1:
            return True
        return False
