#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007 Zsolt Foldvari
# Copyright (C) 2008 Brian G. Matherly
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

"""PDF output generator based on Cairo.
"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gui.utils import open_file_with_default_application
import libcairodoc

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".PdfDoc")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import pango
import cairo
import pangocairo

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------

# resolution
DPI = 72.0

#------------------------------------------------------------------------
#
# PdfDoc class
#
#------------------------------------------------------------------------
class PdfDoc(libcairodoc.CairoDoc):
    """Render the document into PDF file using Cairo.
    """
    def run(self):
        """Create the PDF output.
        """
        # get paper dimensions
        paper_width = self.paper.get_size().get_width() * DPI / 2.54
        paper_height = self.paper.get_size().get_height() * DPI / 2.54
        page_width = round(self.paper.get_usable_width() * DPI / 2.54)
        page_height = round(self.paper.get_usable_height() * DPI / 2.54)
        left_margin = self.paper.get_left_margin() * DPI / 2.54
        top_margin = self.paper.get_top_margin() * DPI / 2.54

        # create cairo context and pango layout
        surface = cairo.PDFSurface(self._backend.filename, paper_width, paper_height)
        surface.set_fallback_resolution(300, 300)
        cr = pangocairo.CairoContext(cairo.Context(surface))

        fontmap = pangocairo.cairo_font_map_get_default()
        saved_resolution = fontmap.get_resolution()
        fontmap.set_resolution(DPI)
        
        pango_context = fontmap.create_context()
        options = cairo.FontOptions()
        options.set_hint_metrics(cairo.HINT_METRICS_OFF)
        pangocairo.context_set_font_options(pango_context, options)
        layout = pango.Layout(pango_context)
        cr.update_context(pango_context)
        
        # paginate the document
        finished = self.paginate(layout, page_width, page_height, DPI, DPI)
        while not finished:
            finished = self.paginate(layout, page_width, page_height, DPI, DPI)

        # render the pages
        for page_nr in range(len(self._pages)):
            cr.save()
            cr.translate(left_margin, top_margin)
            self.draw_page(page_nr, cr, layout,
                           page_width, page_height,
                           DPI, DPI)
            cr.show_page()
            cr.restore()
            
        # close the surface (file)
        surface.finish()
        
        # Restore the resolution. On windows, Gramps UI fonts will be smaller
        # if we don't restore the resolution.
        fontmap.set_resolution(saved_resolution)

        # load the result into an external viewer
        if self.open_req:
            open_file_with_default_application(self._backend.filename) 
