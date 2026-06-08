# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       Dave Khuon
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""Reports/Graphical Reports/Import Document"""

from __future__ import annotations
import os
from typing import Any

# ------------------------------------------------------------------------
# Gramps modules
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

from gramps.gen.plug.menu import DestinationOption
from gramps.gen.plug.report import Report, MenuReportOptions
from gramps.gen.ggettext import dgettext as _


# ------------------------------------------------------------------------
# Import Document Execution Class
# ------------------------------------------------------------------------
class ImportDocument(Report):
    """ImportDocument Report"""

    def __init__(self, database, options_class, user):
        Report.__init__(self, database, options_class, user)
        self.document_path = ""

    def get_subject(self):
        """
        Gramps calls this to identify the item's target.
        By returning the filename here, Gramps will automatically
        append it to your book list entry name!
        """
        try:
            path_option = self.options.menu.get_option_by_name("document_file")
            current_path = path_option.get_value()
            if current_path:
                return os.path.basename(current_path)
        except Exception:
            pass
        return ""

    def begin_report(self):
        """Initializes report properties and reads the browser path destination."""
        try:
            self.document_path = self.options.menu.get_option_by_name(
                "document_file"
            ).get_value()
        except Exception:
            self.document_path = ""

    def write_report(self):
        """Executes the rendering pipeline loop inside the Book compilation stream."""
        self.doc.start_page()

        try:
            # Use the universally recognized built-in style name
            style_name = "Normal"

            if not self.document_path:
                self.doc.draw_text(
                    style_name, "Document Source: No file targeted.", 2.0, 2.0
                )
                self.doc.end_page()
                return

            # Extract the raw filename for our canvas header
            filename = os.path.basename(self.document_path)

            # 1. Print the clean tracking header banner at the top of the sheet
            self.doc.draw_text(style_name, f"Imported Document: {filename}", 2.0, 2.0)
            self.doc.draw_text(
                style_name, f"Source Path: {self.document_path}", 2.0, 2.8
            )

            # 2. Draw our verified anchor box frame beneath the text
            self.doc.draw_line(style_name, 2.0, 4.0, 18.0, 4.0)
            self.doc.draw_line(style_name, 18.0, 4.0, 18.0, 20.0)
            self.doc.draw_line(style_name, 18.0, 20.0, 2.0, 20.0)
            self.doc.draw_line(style_name, 2.0, 20.0, 2.0, 4.0)

        except Exception as err:
            print(f"Canvas layout rendering error: {str(err)}")

        self.doc.end_page()


# ------------------------------------------------------------------------
# Import Document User Configuration Interface Menu
# ------------------------------------------------------------------------
class ImportDocumentOptions(MenuReportOptions):
    """Defines options and provides handling interface."""

    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)
        # Tells Gramps this book item doesn't require an active person/family subject
        self.use_active = False

    def add_menu_options(self, menu):
        """Builds the option block configuration layout."""
        category_name = _("Document Source")

        # DestinationOption builds a text entry line PLUS a live native OS "Browse..." button
        self.file_browser = DestinationOption(
            _("Select Document"),
            "C:sample.pdf",
        )
        self.file_browser.set_help(
            _(
                "Click 'Browse...' to visually navigate to your PDF or Word document file."
            )
        )

        menu.add_option(category_name, "document_file", self.file_browser)
