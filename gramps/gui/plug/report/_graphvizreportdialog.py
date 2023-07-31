#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2017       Nick Hall
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

"""class for generating dialogs for graphviz-based reports """

# -------------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------------
from ._graphreportdialog import GraphReportDialog, BaseFormatComboBox
from gramps.gen.plug.report import CATEGORY_GRAPHVIZ
import gramps.gen.plug.docgen.graphdoc as graphdoc


# -----------------------------------------------------------------------
#
# GraphvizReportDialog
#
# -----------------------------------------------------------------------
class GraphvizReportDialog(GraphReportDialog):
    def make_doc_menu(self):
        """
        Build a menu of document types that are appropriate for
        this graph report.
        """
        self.format_menu = GraphvizFormatComboBox()

    def get_category(self):
        """
        Return the report category.
        """
        return CATEGORY_GRAPHVIZ

    def get_options(self):
        """
        Return the graph options.
        """
        return graphdoc.GVOptions()

    def doc_type_changed(self, obj):
        """
        This routine is called when the user selects a new file
        format for the report.  It adjusts the various dialog sections
        to reflect the appropriate values for the currently selected
        file format.  For example, a HTML document doesn't need any
        paper size/orientation options, but it does need a template
        file.  Those changes are made here.
        """
        GraphReportDialog.doc_type_changed(self, obj)

        output_format_str = obj.get_clname()
        if output_format_str in ["gvpdf", "gspdf", "ps"]:
            # Always use 72 DPI for PostScript and PDF files.
            self._goptions.dpi.set_value(72)
            self._goptions.dpi.set_available(False)
        else:
            self._goptions.dpi.set_available(True)

        if output_format_str in ["gspdf", "dot"]:
            # Multiple pages only valid for dot and PDF via GhostsScript.
            self._goptions.h_pages.set_available(True)
            self._goptions.v_pages.set_available(True)
        else:
            self._goptions.h_pages.set_value(1)
            self._goptions.v_pages.set_value(1)
            self._goptions.h_pages.set_available(False)
            self._goptions.v_pages.set_available(False)


# -------------------------------------------------------------------------------
#
# GraphvizFormatComboBox
#
# -------------------------------------------------------------------------------
class GraphvizFormatComboBox(BaseFormatComboBox):
    FORMATS = graphdoc.FORMATS
