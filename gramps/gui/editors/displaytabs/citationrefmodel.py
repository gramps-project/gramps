#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
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
# GTK libraries
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# CitationModel
#
#-------------------------------------------------------------------------
class CitationRefModel(Gtk.ListStore):

    def __init__(self, citation_list, db):
        Gtk.ListStore.__init__(self, str, str, str, str, bool, str)
        self.db = db
        for handle in citation_list:
            citation = self.db.get_citation_from_handle(handle)
            src = self.db.get_source_from_handle(citation.get_reference_handle())
            self.append(row=[src.title, src.author, citation.page,
                             citation.gramps_id, citation.get_privacy(),
                             handle, ])
