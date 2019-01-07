#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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
from .. import Rule

#-------------------------------------------------------------------------
# "Events having notes that contain a substring"
#-------------------------------------------------------------------------
class MatchesSubstringOf(Rule):
    """Notes having notes containing <substring>"""

    labels = [ _('Substring:')]
    name = _('Notes containing <substring>')
    description = _("Matches notes that contain text "
                    "which matches a substring")
    category = _('General filters')

    def apply(self, db, note):
        """ Apply the filter """
        text = note.get()
        if text.upper().find(self.list[0].upper()) != -1:
            return True
        return False
