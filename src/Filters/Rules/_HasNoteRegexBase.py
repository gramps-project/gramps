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

# $Id$

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import re
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Filters.Rules import Rule

#-------------------------------------------------------------------------
# "People having notes that contain a substring"
#-------------------------------------------------------------------------
class HasNoteRegexBase(Rule):
    """People having notes containing <substring>."""

    labels      = [ _('Text:')]
    name        = _('Objects having notes containing <text>')
    description = _("Matches objects whose notes contain a substring "
                    "or match a regular expression")
    category    = _('General filters')
    allow_regex = True

    def apply(self, db, person):
        notelist = person.get_note_list()
        for notehandle in notelist:
            note = db.get_note_from_handle(notehandle)
            n = note.get()
            if self.match_substring(0, n) is not None:
                return True
        return False
