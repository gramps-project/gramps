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
from gen.ggettext import gettext as _
import sys

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
import libcairodoc
from gen.plug.docgen import INDEX_TYPE_ALP, INDEX_TYPE_TOC
from gen.plug.report.toc_index import write_toc, write_index
import Errors

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

        # get index options
        include_toc = self.index_options.get_include_toc()
        include_index = self.index_options.get_include_index()

        # create cairo context and pango layout
        filename = self._backend.filename.encode(sys.getfilesystemencoding())
        try:
            surface = cairo.PDFSurface(filename, paper_width, paper_height)
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % filename, msg)
            raise Errors.ReportError(errmsg)
        except:
            raise Errors.ReportError(_("Could not create %s") % filename)
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
        self.paginate_document(layout, page_width, page_height, DPI, DPI)
        body_pages = self._pages

        # build the table of contents and alphabetical index
        toc = []
        index = {}
        for page_nr, page in enumerate(body_pages):
            for mark in page.get_marks():
                if mark.type == INDEX_TYPE_ALP:
                    if mark.key in index:
                        if page_nr not in index[mark.key]:
                            index[mark.key].append(page_nr)
                    else:
                        index[mark.key] = [page_nr]
                elif mark.type == INDEX_TYPE_TOC:
                    toc.append([mark, page_nr])

        # paginate the table of contents
        if include_toc:
            toc_pages = self.__generate_toc(layout, page_width, page_height, 
                                            toc)
        else:
            toc_pages = []
        
        # paginate the index
        if include_index:
            index_pages = self.__generate_index(layout, page_width, page_height,
                                                index, len(toc_pages))
        else:
            index_pages = []

        # render the pages
        self._pages = toc_pages + body_pages + index_pages
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

    def __generate_toc(self, layout, page_width, page_height, toc):
        '''
        Generate the table of contents
        '''
        self._doc = libcairodoc.GtkDocDocument()
        self._active_element = self._doc
        self._pages = []
        write_toc(toc, self, 1) # assume single page
        self.paginate_document(layout, page_width, page_height, DPI, DPI)
        toc_pages = self._pages

        # re-generate if table spans more than one page
        offset = len(toc_pages)
        if offset != 1:
            self._doc = libcairodoc.GtkDocDocument()
            self._active_element = self._doc
            self._pages = []
            write_toc(toc, self, offset)
            self.paginate_document(layout, page_width, page_height, DPI, DPI)
            toc_pages = self._pages
            
        return self._pages

    def __generate_index(self, layout, page_width, page_height, index, offset):
        '''
        Generate the index
        '''
        self._doc = libcairodoc.GtkDocDocument()
        self._active_element = self._doc
        self._pages = []
        write_index(index, self, offset)
        self.paginate_document(layout, page_width, page_height, DPI, DPI)
        return self._pages
        
