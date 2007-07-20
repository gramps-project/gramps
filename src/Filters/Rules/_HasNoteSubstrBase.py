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

# $Id: _HasNoteMatchingSubstringOf.py 6634 2006-05-12 22:38:48Z dallingham $

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

#-------------------------------------------------------------------------
# "People having notes that contain a substring"
#-------------------------------------------------------------------------
class HasNoteSubstrBase(Rule):
    """People having notes containing <subtring>"""

    labels      = [ _('Substring:')]
    name        = _('Objects having notes containing <substring>')
    description = _("Matches objects whose notes contain text matching a substring")
    category    = _('General filters')

    def apply(self,db,person):
        notelist = person.get_note_list()
        for notehandle in notelist:
            note = db.get_note_from_handle(notehandle)
            n = unicode(note.get(False))
            if n.upper().find(self.list[0].upper()) != -1:
                return True
        return False
