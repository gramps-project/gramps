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

# $Id: _HasRepo.py 7737 2006-11-30 20:30:28Z rshura $

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
from RelLib import NoteType
from Filters.Rules._Rule import Rule

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasNote(Rule):
    """Rule that checks for a note with a particular value"""


    labels      = [ _('Text:'), 
                    _('Note type:'), 
                    ]
    name        = _('Notes matching parameters')
    description = _("Matches Notes with particular parameters")
    category    = _('General filters')

    def apply(self,db,note):
        if not self.match_substring(0,note.get()):
            return False

        if self.list[1]:
            specified_type = NoteType()
            specified_type.set_from_xml_str(self.list[1])
            if note.type != specified_type:
                return False

        return True
