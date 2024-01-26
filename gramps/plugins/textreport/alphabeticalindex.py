# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012       Nick Hall
# Copyright (C) 2012       Brian G. Matherly
# Copyright (C) 2012-2014  Paul Franklin
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

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.plug.docgen import (
    FontStyle,
    ParagraphStyle,
    TableStyle,
    TableCellStyle,
    FONT_SANS_SERIF,
    IndexMark,
    INDEX_TYPE_TOC,
)


# ------------------------------------------------------------------------
#
# AlphabeticalIndex
#
# ------------------------------------------------------------------------
class AlphabeticalIndex(Report):
    """This report class generates an alphabetical index for a book."""

    def __init__(self, database, options, user):
        """
        Create AlphabeticalIndex object that produces the report.

        The arguments are:

        database        - the Gramps database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance
        """
        Report.__init__(self, database, options, user)
        self._user = user
        self.set_locale(options.menu.get_option_by_name("trans").get_value())

    def write_report(self):
        """Generate the contents of the report"""
        mark = IndexMark(self._("Alphabetical Index"), INDEX_TYPE_TOC, 1)
        self.doc.start_paragraph("IDX-Title")
        self.doc.write_text("", mark)
        self.doc.end_paragraph()
        self.doc.index_title = self._("Index")
        self.doc.insert_index()


# ------------------------------------------------------------------------
#
# AlphabeticalIndexOptions
#
# ------------------------------------------------------------------------
class AlphabeticalIndexOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        self.__db = dbase
        MenuReportOptions.__init__(self, name, dbase)

    def get_subject(self):
        """Return a string that describes the subject of the report."""
        return _("Entire Book")

    def add_menu_options(self, menu):
        """Add the options for this report"""
        category_name = _("Report Options")
        stdoptions.add_localization_option(menu, category_name)

    def make_default_style(self, default_style):
        """Make the default output style for the AlphabeticalIndex report."""
        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=14)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_bottom_margin(0.25)
        para.set_description(_("The style used for the title."))
        default_style.add_paragraph_style("IDX-Title", para)

        table = TableStyle()
        table.set_width(100)
        table.set_columns(2)
        table.set_column_width(0, 80)
        table.set_column_width(1, 20)
        default_style.add_table_style("IDX-Table", table)

        cell = TableCellStyle()
        default_style.add_cell_style("IDX-Cell", cell)

        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=10)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_description(_("The basic style used for the text display."))
        default_style.add_paragraph_style("IDX-Entry", para)
