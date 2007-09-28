#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Zsolt Foldvari
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

"""PDF output generator based on Cairo and gtk.PrintOperation.
"""

__revision__ = "$Revision$"
__author__   = "Zsolt Foldvari"

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
import os

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from CairoDoc import CairoDoc
from GtkPrint import paperstyle_to_pagesetup
from PluginUtils import register_text_doc, register_draw_doc, register_book_doc
import Errors
import Utils
import Mime

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".PdfDoc")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gtk

if gtk.pygtk_version < (2, 10, 0):
    raise Errors.UnavailableError(_("PyGtk 2.10 or later is required"))

#------------------------------------------------------------------------
#
# PdfDoc class
#
#------------------------------------------------------------------------
class PdfDoc(CairoDoc):
    """Print document via GtkPrint* interface.
    
    Requires Gtk+ 2.10.
    
    """
    def run(self):
        """Run the Gtk Print operation.
        """
        # get a page setup from the paper style we have
        page_setup = paperstyle_to_pagesetup(self.paper)
        
        # set up a print operation
        operation = gtk.PrintOperation()
        operation.set_default_page_setup(page_setup)
        operation.set_export_filename(self._filename)
        operation.connect("begin_print", self.on_begin_print)
        operation.connect("draw_page", self.on_draw_page)
        operation.connect("paginate", self.on_paginate)
        
        # export to PDF file
        operation.run(gtk.PRINT_OPERATION_ACTION_EXPORT, None)
        
    def on_begin_print(self, operation, context):
        """Setup environment for printing.
        """
        # get page size
        self.page_width = round(context.get_width())
        self.page_height = round(context.get_height())
        
    def on_paginate(self, operation, context):
        """Paginate the whole document in chunks.
        """
        layout = context.create_pango_layout()
        dpi_x = context.get_dpi_x()
        dpi_y = context.get_dpi_y()
        
        finished = self.paginate(layout,
                                 self.page_width,
                                 self.page_height,
                                 dpi_x,
                                 dpi_y)
        # update page number
        operation.set_n_pages(len(self._pages))
        
        # load the result into an external viewer
        if finished and self.print_req:
            apptype = 'application/pdf'
            app = Mime.get_application(apptype)
            os.environ["FILE"] = self._filename
            os.system('%s "$FILE" &' % app[0])
            
        return finished

    def on_draw_page(self, operation, context, page_nr):
        """Draw the requested page.
        """
        cr = context.get_cairo_context()
        layout = context.create_pango_layout()
        dpi_x = context.get_dpi_x()
        dpi_y = context.get_dpi_y()

        self.draw_page(page_nr,
                       cr,
                       layout,
                       self.page_width,
                       self.page_height,
                       dpi_x,
                       dpi_y)
        
#------------------------------------------------------------------------
#
# Register the document generator with the GRAMPS plugin system
#
#------------------------------------------------------------------------
print_label = None
try:
    mprog = Mime.get_application("application/pdf")
    mtype = Mime.get_description("application/pdf")
    
    if Utils.search_for(mprog[0]):
        print_label=_("Open in %s") % mprog[1]
    else:
        print_label=None
    register_text_doc(mtype, PdfDoc, 1, 1, 1, ".pdf", print_label)
    register_draw_doc(mtype, PdfDoc, 1, 1,    ".pdf", print_label)
    register_book_doc(mtype,classref=PdfDoc,
                      table=1,paper=1,style=1,ext=".pdf")
except:
    register_text_doc(_('PDF document'), PdfDoc,1, 1, 1,".pdf", None)
    register_draw_doc(_('PDF document'), PdfDoc,1, 1,   ".pdf", None)
    register_book_doc(name=_("PDF document"),classref=PdfDoc,
                      table=1,paper=1,style=1,ext=".pdf")
