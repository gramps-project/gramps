#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
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

from _Constants import CATEGORY_TEXT
from _ReportDialog import ReportDialog
from _TextFormatComboBox import TextFormatComboBox

#-----------------------------------------------------------------------
#
# Textual reports
#
#-----------------------------------------------------------------------
class TextReportDialog(ReportDialog):
    """A class of ReportDialog customized for text based reports."""

    def __init__(self,dbstate,uistate,person,options,name,translated_name):
        """Initialize a dialog to request that the user select options
        for a basic text report.  See the ReportDialog class for more
        information."""
        self.category = CATEGORY_TEXT
        ReportDialog.__init__(self,dbstate,uistate,person,options,
                              name,translated_name)

    #------------------------------------------------------------------------
    #
    # Customization hooks for subclasses
    #
    #------------------------------------------------------------------------
    def doc_uses_tables(self):
        """Does this report require the ability to generate tables in
        the file format.  Override this for documents that do need
        table support."""
        return 0

    #------------------------------------------------------------------------
    #
    # Functions related to selecting/changing the current file format.
    #
    #------------------------------------------------------------------------
    def make_doc_menu(self,active=None):
        """Build a menu of document types that are appropriate for
        this text report.  This menu will be generated based upon
        whether the document requires table support, etc."""
        self.format_menu = TextFormatComboBox()
        self.format_menu.set(self.doc_uses_tables(),
                             self.doc_type_changed, None, active)
