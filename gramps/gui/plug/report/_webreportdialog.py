#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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
# Gramps modules
#
# -------------------------------------------------------------------------
from ._reportdialog import ReportDialog
from gramps.gen.plug.report import CATEGORY_WEB


# -------------------------------------------------------------------------
#
# WebReportDialog class
#
# -------------------------------------------------------------------------
class WebReportDialog(ReportDialog):
    """
    The WebReportDialog base class.  This is a base class for generating
    dialogs for web page reports.
    """

    def __init__(self, dbstate, uistate, option_class, name, trans_name):
        """Initialize a dialog"""
        self.category = CATEGORY_WEB
        ReportDialog.__init__(self, dbstate, uistate, option_class, name, trans_name)
        self.options.handler.set_format_name("html")

    def setup_init(self):
        pass

    def setup_target_frame(self):
        """Target frame is not used."""
        pass

    def parse_target_frame(self):
        """Target frame is not used."""
        return 1
