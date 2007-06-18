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

from _Constants import CATEGORY_DRAW
from _ReportDialog import ReportDialog
from _DrawFormatComboBox import DrawFormatComboBox

#-----------------------------------------------------------------------
#
# Drawing reports
#
#-----------------------------------------------------------------------
class DrawReportDialog(ReportDialog):
    """A class of ReportDialog customized for drawing based reports."""
    def __init__(self,dbstate,uistate,person,opt,name,translated_name):
        """Initialize a dialog to request that the user select options
        for a basic drawing report.  See the ReportDialog class for
        more information."""
        self.category = CATEGORY_DRAW
        ReportDialog.__init__(self,dbstate,uistate,person,opt,
                              name,translated_name)

    #------------------------------------------------------------------------
    #
    # Functions related to selecting/changing the current file format.
    #
    #------------------------------------------------------------------------
    def make_doc_menu(self,active=None):
        """Build a menu of document types that are appropriate for
        this drawing report."""
        self.format_menu = DrawFormatComboBox()
        self.format_menu.set(False,self.doc_type_changed, None, active)
