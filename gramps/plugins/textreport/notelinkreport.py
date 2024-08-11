#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015       Doug Blank <doug.blank@gmail.com>
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

""""""

# ------------------------------------------------------------------------
#
# standard python modules
#
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.errors import ReportError
from gramps.gen.plug.menu import PersonOption
from gramps.gen.plug.docgen import (
    IndexMark,
    FontStyle,
    ParagraphStyle,
    TableStyle,
    TableCellStyle,
    FONT_SANS_SERIF,
    PARA_ALIGN_CENTER,
    INDEX_TYPE_TOC,
)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.simple import SimpleAccess


# ------------------------------------------------------------------------
#
# NoteLinkReport
#
# ------------------------------------------------------------------------
class NoteLinkReport(Report):
    """
    This report
    """

    def write_report(self):
        """
        The routine that actually creates the report.
        At this point, the document is opened and ready for writing.
        """
        sdb = SimpleAccess(self.database)

        self.doc.start_paragraph("NoteLink-Title")
        title = _("Note Link Check Report")
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()
        self.doc.start_table("NoteLinkTable", "NoteLink-Table")

        self.doc.start_row()

        self.doc.start_cell("NoteLink-TableCell")
        self.doc.start_paragraph("NoteLink-Normal-Bold")
        self.doc.write_text(_("Note ID"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("NoteLink-TableCell")
        self.doc.start_paragraph("NoteLink-Normal-Bold")
        self.doc.write_text(_("Link Type"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("NoteLink-TableCell")
        self.doc.start_paragraph("NoteLink-Normal-Bold")
        self.doc.write_text(_("Links To"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("NoteLink-TableCell")
        self.doc.start_paragraph("NoteLink-Normal-Bold")
        self.doc.write_text(_("Status"))
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.end_row()

        if self._user:
            self._user.begin_progress(
                _("Note Link Check Report"),
                _("Generating report"),
                self.database.get_number_of_notes(),
            )
        for note in self.database.iter_notes():
            if self._user:
                self._user.step_progress()
            for ldomain, ltype, lprop, lvalue in note.get_links():
                if ldomain == "gramps":
                    tagtype = _(ltype)
                    ref_obj = sdb.get_link(ltype, lprop, lvalue)
                    if ref_obj:
                        tagvalue = sdb.describe(ref_obj)
                        tagcheck = _("Ok")
                    else:
                        tagvalue = "%s://%s/%s/%s" % (ldomain, ltype, lprop, lvalue)
                        tagcheck = _("Failed")
                else:
                    tagtype = _("Internet")
                    tagvalue = lvalue
                    tagcheck = ""

                self.doc.start_row()

                self.doc.start_cell("NoteLink-TableCell")
                self.doc.start_paragraph("NoteLink-Normal")
                self.doc.write_text(note.gramps_id)
                self.doc.end_paragraph()
                self.doc.end_cell()

                self.doc.start_cell("NoteLink-TableCell")
                self.doc.start_paragraph("NoteLink-Normal")
                self.doc.write_text(tagtype)
                self.doc.end_paragraph()
                self.doc.end_cell()

                self.doc.start_cell("NoteLink-TableCell")
                self.doc.start_paragraph("NoteLink-Normal")
                self.doc.write_text(tagvalue)
                self.doc.end_paragraph()
                self.doc.end_cell()

                self.doc.start_cell("NoteLink-TableCell")
                self.doc.start_paragraph("NoteLink-Normal")
                self.doc.write_text(tagcheck)
                self.doc.end_paragraph()
                self.doc.end_cell()

                self.doc.end_row()
        if self._user:
            self._user.end_progress()

        self.doc.end_table()


# ------------------------------------------------------------------------
#
# NoteLinkOptions
#
# ------------------------------------------------------------------------
class NoteLinkOptions(MenuReportOptions):
    def get_subject(self):
        """Return a string that describes the subject of the report."""
        return _("Entire Database")

    def add_menu_options(self, menu):
        """
        Add options to the menu for the tag report.
        """
        pass

    def make_default_style(self, default_style):
        """Make the default output style for the Note Link Report."""
        # Paragraph Styles
        f = FontStyle()
        f.set_size(16)
        f.set_type_face(FONT_SANS_SERIF)
        f.set_bold(1)
        p = ParagraphStyle()
        p.set_header_level(1)
        p.set_bottom_border(1)
        p.set_top_margin(utils.pt2cm(3))
        p.set_bottom_margin(utils.pt2cm(3))
        p.set_font(f)
        p.set_alignment(PARA_ALIGN_CENTER)
        p.set_description(_("The style used for the title."))
        default_style.add_paragraph_style("NoteLink-Title", p)

        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=14, italic=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_description(_("The style used for the section headers."))
        default_style.add_paragraph_style("NoteLink-Heading", para)

        font = FontStyle()
        font.set_size(12)
        p = ParagraphStyle()
        p.set(first_indent=-0.75, lmargin=0.75)
        p.set_font(font)
        p.set_top_margin(utils.pt2cm(3))
        p.set_bottom_margin(utils.pt2cm(3))
        p.set_description(_("The basic style used for the text display."))
        default_style.add_paragraph_style("NoteLink-Normal", p)

        font = FontStyle()
        font.set_size(12)
        font.set_bold(True)
        p = ParagraphStyle()
        p.set(first_indent=-0.75, lmargin=0.75)
        p.set_font(font)
        p.set_top_margin(utils.pt2cm(3))
        p.set_bottom_margin(utils.pt2cm(3))
        p.set_description(_("The basic style used for table headings."))
        default_style.add_paragraph_style("NoteLink-Normal-Bold", p)

        # Table Styles
        cell = TableCellStyle()
        default_style.add_cell_style("NoteLink-TableCell", cell)

        table = TableStyle()
        table.set_width(100)
        table.set_columns(4)
        table.set_column_width(0, 10)
        table.set_column_width(1, 15)
        table.set_column_width(2, 65)
        table.set_column_width(3, 10)
        default_style.add_table_style("NoteLink-Table", table)
