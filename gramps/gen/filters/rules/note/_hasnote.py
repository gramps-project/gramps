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
from ....lib.notetype import NoteType
from .. import Rule

#-------------------------------------------------------------------------
#
# HasNote
#
#-------------------------------------------------------------------------
class HasNote(Rule):
    """Rule that checks for a note with a particular value"""


    labels = [ _('Text:'),
                    _('Note type:'),
                    ]
    name = _('Notes matching parameters')
    description = _("Matches Notes with particular parameters")
    category = _('General filters')
    allow_regex = True

    def prepare(self, db, user):
        if self.list[1]:
            self.ntype = NoteType()
            self.ntype.set_from_xml_str(self.list[1])
        else:
            self.ntype = None

    def apply(self,db, note):
        if not self.match_substring(0, note.get()):
            return False

        if self.ntype:
            if self.ntype.is_custom() and self.use_regex:
                if self.regex[1].search(str(note.type)) is None:
                    return False
            elif note.type != self.ntype:
                return False

        return True
