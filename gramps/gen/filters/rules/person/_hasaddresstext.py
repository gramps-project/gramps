#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Brian G. Matherly
# Copyright (C) 2008  Jerome Rapinat
# Copyright (C) 2008  Benny Malengier
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


# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# HasAddressText
#
# -------------------------------------------------------------------------
class HasAddressText(Rule):
    """Rule that checks for text in personal addresses"""

    labels = [_('Text:')]
    name = _('People with an address containing <text>')
    description = _("Matches people with a personal address containing "
                    "the given text")
    category = _('General filters')
    allow_regex = True

    def apply(self, db, person):
        for address in person.get_address_list():
            for string in address.get_text_data_list():
                if self.match_substring(0, string):
                    return True
        return False
