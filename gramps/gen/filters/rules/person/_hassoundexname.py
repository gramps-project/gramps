#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2017  Paul Culley <paulr2787_at_gmail.com>
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
# Gramps modules
#
#-------------------------------------------------------------------------
from .. import Rule
from ....lib.nameorigintype import NameOriginType
from ....soundex import soundex
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext


#-------------------------------------------------------------------------
#
# HasNameOf
#
#-------------------------------------------------------------------------
class HasSoundexName(Rule):
    """Rule that checks for full or partial name matches"""

    labels = [_('Name:')]
    name = _('Soundex match of People with the <name>')
    description = _("Soundex Match of people with a specified name. First "
                    "name, Surname, Call name, and Nickname are searched in "
                    "primary and alternate names.")
    category = _('General filters')
    allow_regex = False

    def apply(self, db, person):
        self.sndx = soundex(self.list[0])
        for name in [person.get_primary_name()] + person.get_alternate_names():
            if self._match_name(name):
                return True
        return False

    def _match_name(self, name):
        if self.list[0]:
            if soundex(str(name.get_first_name())) == self.sndx:
                return True
            elif soundex(str(name.get_surname())) == self.sndx:
                return True
            elif soundex(str(name.get_call_name())) == self.sndx:
                return True
            elif soundex(str(name.get_nick_name())) == self.sndx:
                return True
            elif soundex(str(name.get_family_nick_name())) == self.sndx:
                return True
            else:
                for surn in name.get_surname_list():
                    if self._match_surname(surn):
                        return True
        return False

    def _match_surname(self, surn):
        if soundex(str(surn.get_surname())) == self.sndx:
            return True
        if surn.get_origintype().value == NameOriginType.PATRONYMIC:
            if soundex(str(surn.get_surname())) == self.sndx:
                return True
        return False
