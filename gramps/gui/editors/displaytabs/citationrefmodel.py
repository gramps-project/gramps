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


# -------------------------------------------------------------------------
#
# Python
#
# -------------------------------------------------------------------------
from html import escape


# -------------------------------------------------------------------------
#
# GTK libraries
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gramps.gen.config import config
from gramps.gen.utils.string import conf_strings
from gramps.gen.datehandler import get_date, get_date_valid
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Globals
#
# -------------------------------------------------------------------------
invalid_date_format = config.get("preferences.invalid-date-format")


# -------------------------------------------------------------------------
#
# CitationModel
#
# -------------------------------------------------------------------------
class CitationRefModel(Gtk.ListStore):
    def __init__(self, citation_list, db):
        Gtk.ListStore.__init__(
            self, str, str, str, str, str, str, str, bool, str, int, str
        )
        self.db = db
        dbgsfh = self.db.get_source_from_handle
        for handle in citation_list:
            citation = self.db.get_citation_from_handle(handle)
            src = dbgsfh(citation.get_reference_handle())
            confidence = citation.get_confidence_level()
            self.append(
                row=[
                    src.title,
                    src.author,
                    self.column_date(citation),
                    src.get_publication_info(),
                    _(conf_strings[confidence]),
                    citation.page,
                    citation.gramps_id,
                    citation.get_privacy(),
                    self.column_sort_date(citation),
                    self.column_sort_confidence(citation),
                    handle,
                ]
            )

    def column_date(self, citation):
        retval = get_date(citation)
        if not get_date_valid(citation):
            return invalid_date_format % escape(retval)
        else:
            return retval

    def column_sort_date(self, citation):
        date = citation.get_date_object()
        if date:
            return "%09d" % date.get_sort_value()
        else:
            return ""

    def column_sort_confidence(self, citation):
        confidence = citation.get_confidence_level()
        return confidence
