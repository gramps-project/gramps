#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

"Printing interface based on gtk.Print*"

__revision__ = "$Revision$"

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
import BaseDoc
from PluginUtils import register_text_doc, register_draw_doc, register_book_doc
import Errors

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".GtkDoc")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
##import pygtk
import gtk
import cairo
import pango

##if not hasattr(gtk, "PrintOperation"):
if gtk.pygtk_version < (2,10,0):
    raise Errors.UnavailableError(
        _("Cannot be loaded because PyGtk 2.10 or later is not installed"))

#------------------------------------------------------------------------
#
# PreviewCanvas and PreviewWindow
#
# These classes provide a simple print preview functionality.
# They do not actually render anything themselves, they rely
# upon the Print opertaion to do the rendering.
#
#------------------------------------------------------------------------
class PreviewCanvas(gtk.DrawingArea):
    """This provides a simple widget for displaying a
    cairo rendering used to show print preview windows.
    """
    
    def __init__(self,
                 operation,
                 preview_operation,
                 print_context):
        gtk.DrawingArea.__init__(self)
        self._operation = operation
        self._preview_operation = preview_operation
        self._print_context = print_context

        self.connect("expose_event",self.expose)
        self.connect("realize",self.realize)
        
        self._page_no = 1 # always start on page 1


    def set_page(self,page):
        """Change which page is displayed"""
        if page > 0:
            self._page_no = page
            self.queue_draw()
        
    def realize(self, dummy=None):
        """Generate the cairo context for this drawing area
        and pass it to the print context."""
        gtk.DrawingArea.realize(self)
        self._context = self.window.cairo_create()
        self._print_context.set_cairo_context(self._context,72,72)

    def expose(self, widget, event):
        """Ask the print operation to actually draw the page."""
        self.window.clear()
        self._preview_operation.render_page(self._page_no)

        # need to calculate how large the widget now is and
        # set it so that the scrollbars are updated.
        # I can't work out how to do this.
        #self.set_size_request(200, 300)

    
class PreviewWindow(gtk.Window):
    """A dialog to show a print preview."""
    
    def __init__(self,
                 operation,
                 preview_operation,
                 print_context,
                 parent):
        gtk.Window.__init__(self)
        self.set_default_size(640, 480)

        self._operation = operation
        self._preview_operation = preview_operation

        self.connect("delete_event", self.delete_event)

        self.set_title("Print Preview")
        self.set_transient_for(parent)

        # Setup widgets
        self._vbox = gtk.VBox()
        self.add(self._vbox)
        self._spin = gtk.SpinButton()
        self._spin.set_value(1)
        
        self._close_bt = gtk.Button(stock=gtk.STOCK_CLOSE)
        self._close_bt.connect("clicked",self.close)
                               
        self._hbox = gtk.HBox()
        self._hbox.pack_start(self._spin)
        self._hbox.pack_start(self._close_bt,expand=False)
        self._vbox.pack_start(self._hbox,expand=False)


        self._scroll = gtk.ScrolledWindow(None,None)
        self._canvas = PreviewCanvas(operation,preview_operation,print_context)
        self._scroll.add_with_viewport(self._canvas)
        self._vbox.pack_start(self._scroll,expand=True,fill=True)

        # The print operation does not know how many pages there are until
        # after the first expose event, so we use the expose event to
        # trigger an update of the spin box.
        # This still does not work properly, sometimes the first expose event
        # happends before this gets connected and the spin box does not get
        # updated, I am probably just not doing it very cleverly.
        self._change_n_pages_connect_id = self._canvas.connect("expose_event", self.change_n_pages)
        self._spin.connect("value-changed",
                           lambda spinbutton: self._canvas.set_page(spinbutton.get_value_as_int()))
        
        self._canvas.set_double_buffered(False)

        self.show_all()



    def change_n_pages(self, widget, event ):
        """Update the spin box to have the correct number of pages for the
        print operation"""
        n_pages = self._preview_operation.get_property("n_pages")
        
        if n_pages != -1:
            # As soon as we have a valid number of pages we no
            # longer need this call back so we can disconnect it.
            self._canvas.disconnect(self._change_n_pages_connect_id)
            
        value = int(self._spin.get_value())
        if value == -1: value = 1
        self._spin.configure(gtk.Adjustment(value,1,
                                            n_pages,
                                            1,1,1),1,0)

    def end_preview(self):
        self._operation.end_preview()
        
    def delete_event(self, widget, event, data=None):
        self.end_preview()
        return False

    def close(self,btn):
        self.end_preview()
        self.destroy()

        # I am not sure that this is the correct way to do this
        # but I expect the print dialog to reappear after I
        # close the print preview button.
        self._operation.do_print()
        return False       

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def paperstyle_to_pagesetup(paper_style):
    """convert a gramps paper_style instance into a gtk.PageSetup instance.
    """
    page_setup = gtk.PageSetup()
    if paper_style.get_orientation() == BaseDoc.PAPER_PORTRAIT:
        page_setup.set_orientation(gtk.PAGE_ORIENTATION_PORTRAIT)
    else:
        page_setup.set_orientation(gtk.PAGE_ORIENTATION_LANDSCAPE)

    gpaper_size = paper_style.get_size()

    # This causes my gtk to seg fault.
    paper_size = gtk.PaperSize('na_'+paper_style.get_size().get_name().lower())
    if paper_size.is_custom():
        paper_size.set_size(paper_style.get_width()*10,
                            paper_style.get_height()*10,
                            gtk.UNIT_MM)
        
    # So we just to this instead.
    # This does not appear to work either, it reports an
    # GtkWarning: gtk_paper_size_set_size: assertion `size->is_custom' failed
    # But I don't know how to tell it that it is custom without it segfaulting.
##     paper_size = gtk.PaperSize()
##     paper_size.set_size(gpaper_size.get_width()*10,
##                         gpaper_size.get_height()*10,
##                         gtk.UNIT_MM)

    page_setup.set_paper_size(paper_size)

    return page_setup
    
class PrintFacade(gtk.PrintOperation):
    """Provides the main print operation functions."""
    
    def __init__(self, renderer,page_setup):
        """
        render must be an object with the following interface:
           render: callable that takes (operation, context, page_nr)
                   it should render the page_nr page onto the provided context.
           get_n_pages: a callable that takes (operation, context) and
                        returns the number of pages that would be needed to render
                        onto the given context.
        """
        gtk.PrintOperation.__init__(self)

        self._renderer = renderer
        
        self.set_default_page_setup(page_setup)
        
        self.connect("begin_print", self.begin_print)
        self.connect("draw_page", self.draw_page)
        self.connect("paginate", self.paginate)
        self.connect("preview", self.preview)        

        self._settings = None
        self._print_op = None
        
    def begin_print(self,operation, context):
        operation.set_n_pages(self._renderer.get_n_pages(operation, context))

    def paginate(self, operation, context):
        return True

    def preview(self, operation, preview, context, parent, dummy=None):
        preview = PreviewWindow(self,preview,context,parent)
        return True
        
    def draw_page(self,operation, context, page_nr):
        self._renderer.render(operation, context, page_nr)
        
    def do_print(self, widget=None, data=None):
        """This is the method that actually runs the Gtk Print operation."""

        # We need to store the settings somewhere so that they are remembered
        # each time the dialog is restarted.
        if self._settings != None:
            self.set_print_settings(self._settings)

        res = self.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG, None)
        
        if res == gtk.PRINT_OPERATION_RESULT_APPLY:
            self._settings = self.get_print_settings()


#------------------------------------------------------------------------
#
# CairoJob and GtkDoc
#
# These classes to the real work. GtkDoc provides the BaseDoc interface
# and CairoJob performs the job that gnomeprintjob does. It has to
# maintain an abstract model of the document and then render it onto
# a cairo context when asked.
#
#------------------------------------------------------------------------
class CairoJob(object):
    """Class to act as a abstract document that can render onto a
    cairo context."""

    def __init__(self):
        self._doc = []

    #
    # interface required for PrintFacade
    #
    def render(self, operation, context, page_nr):
        """Renders the document on the cairo context.
        A useful reference is: http://www.tortall.net/mu/wiki/CairoTutorial
        """
        cr = context.get_cairo_context()

        y = 20
        x = 30

        text="\n".join(self._doc)
        
        # Draw some text
        layout = context.create_pango_layout()
        layout.set_text(text)
        desc = pango.FontDescription("sans 28")
        layout.set_font_description(desc)

        cr.move_to(x, y)
        cr.show_layout(layout)


    def get_n_pages(self, operation, context):
        """return the number of pages required to print onto the
        provided context."""

        return 3
    
    #
    # methods to add content to abstract document.
    #

    def write_text(self,text):
        self._doc.append(text)
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class GtkDoc(BaseDoc.BaseDoc,BaseDoc.TextDoc,BaseDoc.DrawDoc):

    def open(self,filename):
        self._job = CairoJob()
    
    def close(self):
        PrintFacade(self._job,
                    paperstyle_to_pagesetup(self.paper)).do_print()
        
    def page_break(self):
        pass

    def start_paragraph(self,style_name,leader=None):
        pass
    
    def end_paragraph(self):
        pass
    
    def start_bold(self):
        pass
    
    def end_bold(self):
        pass
    
    def start_superscript(self):
        pass
    
    def end_superscript(self):
        pass
    
    def start_table(self,name,style_name):
        pass
    
    def end_table(self):
        pass
    
    def start_row(self):
        pass
    
    def end_row(self):
        pass
    
    def start_cell(self,style_name,span=1):
        pass
    
    def end_cell(self):
        pass
    
    def add_media_object(self,name,pos,x_cm,y_cm):
        pass
    
    def write_note(self,text,format,style_name):
        print "write_note: ", text
        self._job.write_text(text)
    
    def write_text(self,text,mark=None):
        print "write_text: ", text
        self._job.write_text(text)
    
    def start_page(self):
        pass
    
    def end_page(self):
        pass
    
    def draw_line(self,style,x1,y1,x2,y2):
        pass

    def draw_path(self,style,path):
        pass
        
    def draw_box(self,style,text,x,y, w, h):
        pass
    
    def draw_text(self,style,text,x,y):
        pass
    
    def rotate_text(self,style,text,x,y,angle):
        pass
    
    def center_text(self,style,text,x,y):
        pass
    
    def center_print(self,lines,font,x,y,w,h):
        pass
    
    def left_print(self,lines,font,x,y):
        pass
    

#------------------------------------------------------------------------
#
# Register the document generator with the GRAMPS plugin system
#
#------------------------------------------------------------------------
register_text_doc(_('GtkPrint'), GtkDoc, 1, 1, 1, "", None)
register_draw_doc(_('GtkPrint'), GtkDoc, 1, 1, "", None)
register_book_doc(_("GtkPrint"), GtkDoc, 1, 1, 1, "", None)
