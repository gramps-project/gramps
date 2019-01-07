#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
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
#
# HasNameOf
#
#-------------------------------------------------------------------------
class RegExpName(Rule):
    """Rule that checks for full or partial name matches"""

    labels = [_('Text:')]
    name = _('People with a name matching <text>')
    description = _("Matches people's names containing a substring or "
                    "matching a regular expression")
    category = _('General filters')
    allow_regex = True

    def apply(self,db,person):
        for name in [person.get_primary_name()] + person.get_alternate_names():
            for field in [name.first_name, name.get_surname(), name.suffix,
                          name.title, name.nick, name.famnick, name.call]:
                if self.match_substring(0, field):
                    return True
        return False
