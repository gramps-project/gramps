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
from ....utils.alive import probably_alive
from .. import Rule
from ....datehandler import parser

#-------------------------------------------------------------------------
# "People probably alive"
#-------------------------------------------------------------------------
class ProbablyAlive(Rule):
    """People probably alive"""

    labels = [_("On date:")]
    name = _('People probably alive')
    description = _("Matches people without indications of death that are not too old")
    category = _('General filters')

    def prepare(self, db, user):
        try:
            self.current_date = parser.parse(str(self.list[0]))
        except:
            self.current_date = None

    def apply(self,db,person):
        return probably_alive(person,db,self.current_date)
