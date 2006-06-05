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

# $Id: _SearchName.py 6529 2006-05-03 06:29:07Z rshura $

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Filters.Rules._Rule import Rule
import re

#-------------------------------------------------------------------------
#
# HasNameOf
#
#-------------------------------------------------------------------------
class RegExpName(Rule):
    """Rule that checks for full or partial name matches"""

    labels      = [_('Expression:')]
    name        = _('People matching the <regex_name>')
    description = _("Matches people's names with a specified regular expression")
    category    = _('General filters')

    def __init__(self, list):
        Rule.__init__(self, list)
        
        try:
            self.match = re.compile(list[0],re.I|re.U|re.L)
        except:
            self.match = re.compile('')

    def apply(self,db,person):
        for name in [person.get_primary_name()] + person.get_alternate_names():
            for field in [name.first_name, name.surname, name.suffix, name.title,
                          name.prefix, name.patronymic]:
                if self.match.match(field):
                    return True
        else:
            return False
