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

#-------------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------------
from ._graphreportdialog import GraphReportDialog, BaseFormatComboBox
from gramps.gen.plug.report import CATEGORY_TREE
import gramps.gen.plug.docgen.treedoc as treedoc

#-----------------------------------------------------------------------
#
# TreeReportDialog
#
#-----------------------------------------------------------------------
class TreeReportDialog(GraphReportDialog):

    def make_doc_menu(self):
        """
        Build a menu of document types that are appropriate for
        this graph report.
        """
        self.format_menu = TreeFormatComboBox()

    def get_category(self):
        """
        Return the report category.
        """
        return CATEGORY_TREE

    def get_options(self):
        """
        Return the graph options.
        """
        return treedoc.TreeOptions()

#-------------------------------------------------------------------------------
#
# TreeFormatComboBox
#
#-------------------------------------------------------------------------------
class TreeFormatComboBox(BaseFormatComboBox):
    FORMATS = treedoc.FORMATS
