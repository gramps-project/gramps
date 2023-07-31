# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Martin Hawlisch
# Copyright (C) 2009 Douglas S. Blank
# Copyright (C) 2009-2016 Serge Noiraud
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

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

# the print settings to remember between print sessions
PRINT_SETTINGS = None


# ------------------------------------------------------------------------
#
# CairoPrintSave class
#
# ------------------------------------------------------------------------
class CairoPrintSave:
    """
    Act as an abstract document that can render onto a cairo context.

    It can render the model onto cairo context pages, according to the received
    page style.

    """

    def __init__(self, widthpx, heightpx, drawfunc, parent):
        """
        This class provides the things needed so as to dump a cairo drawing on
        a context to output
        """
        # We try to adapt the cairo dump to an A4 page.
        widthpx += 30
        heightpx += 30
        self.scale = 100.0
        self.widthpx = widthpx
        self.heightpx = heightpx
        self.drawfunc = drawfunc
        self.parent = parent
        self.preview = None

    def run(self):
        """
        Create the physical output from the meta document.

        """
        global PRINT_SETTINGS

        # set up a print operation
        operation = Gtk.PrintOperation()
        operation.connect("draw_page", self.on_draw_page)
        operation.connect("preview", self.on_preview)
        operation.set_n_pages(1)
        page_setup = Gtk.PageSetup()
        if PRINT_SETTINGS is None:
            PRINT_SETTINGS = Gtk.PrintSettings()
        page_setup = Gtk.print_run_page_setup_dialog(None, page_setup, PRINT_SETTINGS)
        paper_size_used = page_setup.get_paper_size()
        if self.widthpx > self.heightpx:
            szw = self.widthpx
            szh = self.heightpx
        else:
            szh = self.widthpx
            szw = self.heightpx
        height_used = paper_size_used.get_height(Gtk.Unit.POINTS)
        width_used = paper_size_used.get_width(Gtk.Unit.POINTS)
        coefx = szw / height_used  # width and height depends on the selected
        # page (A4, A3, ...)
        coefy = szh / width_used
        if coefx < coefy:
            self.scale = 100.0 / coefy
        else:
            self.scale = 100.0 / coefx
        PRINT_SETTINGS.set_scale(self.scale)
        if self.widthpx > self.heightpx:
            page_setup.set_orientation(Gtk.PageOrientation.LANDSCAPE)
        else:
            page_setup.set_orientation(Gtk.PageOrientation.PORTRAIT)
        operation.set_default_page_setup(page_setup)

        if PRINT_SETTINGS is not None:
            operation.set_print_settings(PRINT_SETTINGS)

        # run print dialog
        while True:
            self.preview = None
            res = operation.run(Gtk.PrintOperationAction.PRINT_DIALOG, None)
            if self.preview is None:  # cancel or print
                break
            # set up printing again; can't reuse PrintOperation?
            operation = Gtk.PrintOperation()
            operation.set_default_page_setup(page_setup)
            operation.connect("draw_page", self.on_draw_page)
            operation.connect("preview", self.on_preview)
            # set print settings if it was stored previously
            if PRINT_SETTINGS is not None:
                operation.set_print_settings(PRINT_SETTINGS)

        # store print settings if printing was successful
        if res == Gtk.PrintOperationResult.APPLY:
            PRINT_SETTINGS = operation.get_print_settings()

    def on_draw_page(self, operation, context, page_nr):
        """Draw a page on a Cairo context."""
        dummy_op = operation
        dummy_ct = context
        dummy_pg = page_nr
        ctx = context.get_cairo_context()
        self.drawfunc(self.parent, ctx)

    def on_preview(self, operation, preview, context, parent):
        """Implement custom print preview functionality.
        We provide a dummy holder here, because on_preview crashes if no
        default application is set with gir 3.3.2 (typically evince not
        installed)!
        """
        dummy_op = operation
        dummy_ct = context
        dummy_pr = preview
        dummy_pa = parent
        operation.run(Gtk.PrintOperationAction.PREVIEW, None)
        return False
