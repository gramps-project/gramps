#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Brian G. Matherly
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
# $Id:  $

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
from cStringIO import StringIO
import tempfile

#-------------------------------------------------------------------------------
#
# GTK+ modules
#
#-------------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------------
import Mime
import Utils
import BaseDoc
import Config
from _Constants import CATEGORY_GRAPHVIZ
from _ReportDialog import ReportDialog

#-------------------------------------------------------------------------------
#
# Private Contstants
#
#-------------------------------------------------------------------------------
_dot_found = 0
_gs_cmd = ""

if os.sys.platform == "win32":
    _dot_found = Utils.search_for("dot.exe")
    
    if Utils.search_for("gswin32c.exe") == 1:
        _gs_cmd = "gswin32c.exe"
    elif Utils.search_for("gswin32.exe") == 1:
        _gs_cmd = "gswin32.exe"
else:
    _dot_found = Utils.search_for("dot")
    
    if Utils.search_for("gs") == 1:
        _gs_cmd = "gs"

#-------------------------------------------------------------------------------
#
# GVDocBase
#
#-------------------------------------------------------------------------------
class GVDocBase(BaseDoc.BaseDoc,BaseDoc.GVDoc):
    """
    Base document generator for all Graphiz codument generators. Classes that
    inherit from this class will only need to implement the close function.
    The close function will generate the actual file of the appropriate type.
    """
    def __init__(self,styles,paper_style,template):
        BaseDoc.BaseDoc.__init__(self,styles,paper_style,template)
        
        self.dot = StringIO()
        self.paper = paper_style
        paper_size = paper_style.get_size()
        pheight = paper_size.get_height_inches()
        pwidth = paper_size.get_width_inches()
        
        # graph size
        if self.paper.get_orientation() == BaseDoc.PAPER_LANDSCAPE:
            rotate = 90
            sizew = ( paper_size.get_height()      - 
                      self.paper.get_top_margin()  -
                      self.paper.get_bottom_margin() ) / 2.54
            sizeh = ( paper_size.get_width()       - 
                      self.paper.get_left_margin() - 
                      self.paper.get_right_margin() ) / 2.54
        else:
            rotate = 0
            sizew = ( paper_size.get_width()       - 
                      self.paper.get_left_margin() - 
                      self.paper.get_right_margin() ) / 2.54
            sizeh = ( paper_size.get_height()      - 
                      self.paper.get_top_margin()  -
                      self.paper.get_bottom_margin() ) / 2.54
                      
        self.dot.write( 'digraph GRAMPS_graph { \n' )
        self.dot.write( '  bgcolor=white; \n' )
        self.dot.write( '  center=1; \n' )
        self.dot.write( '  rankdir="TB"; \n' )
        self.dot.write( '  mclimit=2.0; \n' )
        self.dot.write( '  pagedir="BL"; \n' )
        self.dot.write( '  page="%3.2f,%3.2f"; \n' % ( pwidth, pheight ) )
        self.dot.write( '  size="%3.2f,%3.2f"; \n' % ( sizew, sizeh ) )
        self.dot.write( '  rotate=%d; \n' % rotate )
        self.dot.write( '  nodesep=0.25; \n'  )
        
    def open(self, filename):
        self.filename = os.path.normpath(os.path.abspath(filename))

    def close(self):
        """
        This isn't useful by itself. Other classes need to override this and
        actually generate a file.
        """
        self.dot.write( '}'  )
    
    def add_node(self, id, label, shape="box", fillcolor="white", url=""):
        """
        Add a node to this graph. Nodes can be different shapes like boxes and
        circles.
        
        Implementes BaseDoc.GVDoc.add_node().
        """
        line = '  "%s" [style=filled label="%s", shape="%s", fillcolor="%s",'  \
               ' URL="%s"];\n'                                               % \
                (id, label, shape, fillcolor, url)
        self.dot.write(line)
        
    def add_link(self, id1, id2):
        """
        Add a link between two nodes.
        
        Implementes BaseDoc.GVDoc.add_link().
        """
        self.dot.write('  "%s" -> "%s";\n' % (id1, id2))

#-------------------------------------------------------------------------------
#
# GVDotDoc
#
#-------------------------------------------------------------------------------
class GVDotDoc(GVDocBase):
    def close(self):
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self.filename[-4:] != ".dot":
            self.filename += ".dot"

        file = open(self.filename,"w")
        file.write(self.dot.getvalue())
        file.close()
        
        if self.print_req:
            app = Mime.get_application("text/x-graphviz")
            Utils.launch(app[0], self.filename) 

#-------------------------------------------------------------------------------
#
# GVPsDoc
#
#-------------------------------------------------------------------------------
class GVPsDoc(GVDocBase):
    def close(self):
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self.filename[-3:] != ".ps":
            self.filename += ".ps"

        # Create a temporary dot file
        (handle,tmp_dot) = tempfile.mkstemp(".dot" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self.dot.getvalue())
        dotfile.close()

        # Generate the PS file.
        os.system( 'dot -Tps -o"%s" "%s"' % (self.filename,tmp_dot) )
        
        # Delete the temporary dot file
        os.remove(tmp_dot)
        
        if self.print_req:
            app = Mime.get_application("application/postscript")
            Utils.launch(app[0], self.filename)

#-------------------------------------------------------------------------------
#
# GVSvgDoc
#
#-------------------------------------------------------------------------------
class GVSvgDoc(GVDocBase):
    def close(self):
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self.filename[-4:] != ".svg":
            self.filename += ".svg"

        # Create a temporary dot file
        (handle,tmp_dot) = tempfile.mkstemp(".dot" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self.dot.getvalue())
        dotfile.close()

        # Generate the PS file.
        os.system( 'dot -Tsvg -o"%s" "%s"' % (self.filename,tmp_dot) )
        
        # Delete the temporary dot file
        os.remove(tmp_dot)
        
        if self.print_req:
            app = Mime.get_application("image/svg")
            Utils.launch(app[0], self.filename)
            
#-------------------------------------------------------------------------------
#
# GVSvgzDoc
#
#-------------------------------------------------------------------------------
class GVSvgzDoc(GVDocBase):
    def close(self):
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self.filename[-5:] != ".svgz":
            self.filename += ".svgz"

        # Create a temporary dot file
        (handle,tmp_dot) = tempfile.mkstemp(".dot" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self.dot.getvalue())
        dotfile.close()

        # Generate the PS file.
        os.system( 'dot -Tsvgz -o"%s" "%s"' % (self.filename,tmp_dot) )
        
        # Delete the temporary dot file
        os.remove(tmp_dot)
        
        if self.print_req:
            app = Mime.get_application("image/svgz")
            Utils.launch(app[0], self.filename)
            
#-------------------------------------------------------------------------------
#
# GVPngDoc
#
#-------------------------------------------------------------------------------
class GVPngDoc(GVDocBase):
    def close(self):
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self.filename[-4:] != ".png":
            self.filename += ".png"

        # Create a temporary dot file
        (handle,tmp_dot) = tempfile.mkstemp(".dot" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self.dot.getvalue())
        dotfile.close()

        # Generate the PS file.
        os.system( 'dot -Tpng -o"%s" "%s"' % (self.filename,tmp_dot) )
        
        # Delete the temporary dot file
        os.remove(tmp_dot)
        
        if self.print_req:
            app = Mime.get_application("image/png")
            Utils.launch(app[0], self.filename)     
            
#-------------------------------------------------------------------------------
#
# GVJpegDoc
#
#-------------------------------------------------------------------------------
class GVJpegDoc(GVDocBase):
    def close(self):
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self.filename[-5:] != ".jpeg":
            self.filename += ".jpeg"

        # Create a temporary dot file
        (handle,tmp_dot) = tempfile.mkstemp(".dot" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self.dot.getvalue())
        dotfile.close()

        # Generate the PS file.
        os.system( 'dot -Tjpg -o"%s" "%s"' % (self.filename,tmp_dot) )
        
        # Delete the temporary dot file
        os.remove(tmp_dot)
        
        if self.print_req:
            app = Mime.get_application("image/jpeg")
            Utils.launch(app[0], self.filename)
            
#-------------------------------------------------------------------------------
#
# GVGifDoc
#
#-------------------------------------------------------------------------------
class GVGifDoc(GVDocBase):
    def close(self):
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self.filename[-4:] != ".gif":
            self.filename += ".gif"

        # Create a temporary dot file
        (handle,tmp_dot) = tempfile.mkstemp(".dot" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self.dot.getvalue())
        dotfile.close()

        # Generate the PS file.
        os.system( 'dot -Tgif -o"%s" "%s"' % (self.filename,tmp_dot) )
        
        # Delete the temporary dot file
        os.remove(tmp_dot)
        
        if self.print_req:
            app = Mime.get_application("image/gif")
            Utils.launch(app[0], self.filename)     
     
#-------------------------------------------------------------------------------
#
# GVPdfDoc
#
#-------------------------------------------------------------------------------
class GVPdfDoc(GVDocBase):
    def close(self):
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self.filename[-4:] != ".pdf":
            self.filename += ".pdf"
            
        # Create a temporary dot file
        (handle,tmp_dot) = tempfile.mkstemp(".dot" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self.dot.getvalue())
        dotfile.close()

        # Generate a temporary PS file.
        os.system( 'dot -Tps -o"%s" "%s"' % (self.filename,tmp_dot) )

        # Create a temporary Postscript file
        (handle,tmp_ps) = tempfile.mkstemp(".ps" )
        os.close( handle )

        # Generate Postscript using dot
        command = 'dot -Tps -o"%s" "%s"' % ( tmp_ps, tmp_dot )
        os.system(command)

        # Add .5 to remove rounding errors.
        paper_size = self.paper.get_size()
        width_pt = int( (paper_size.get_width_inches() * 72) + 0.5 )
        height_pt = int( (paper_size.get_height_inches() * 72) + 0.5 )
        
        # Convert to PDF using ghostscript
        command = '%s -q -sDEVICE=pdfwrite -dNOPAUSE -dDEVICEWIDTHPOINTS=%d' \
                  ' -dDEVICEHEIGHTPOINTS=%d -sOutputFile="%s" "%s" -c quit' \
                  % ( _gs_cmd, width_pt, height_pt, self.filename, tmp_ps )
        os.system(command)

        os.remove(tmp_ps)
        os.remove(tmp_dot)

        if self.print_req:
            app = Mime.get_application("application/pdf")
            Utils.launch(app[0], self.filename) 
      
#-------------------------------------------------------------------------------
#
# Various Graphviz formats.
#
#-------------------------------------------------------------------------------
_formats = []
_formats += [{ 'type' : "dot",
               'descr': _("Graphviz Dot File"), 
               'mime' : "text/x-graphviz", 
               'class': GVDotDoc }]

if _dot_found:
    _formats += [{ 'type' : "ps",
                   'descr': _("Postscript"), 
                   'mime' : "application/postscript", 
                   'class': GVPsDoc }]
    
    _formats += [{ 'type' : "svg",
                   'descr': _("Structured Vector Graphics (SVG)"), 
                   'mime' : "image/svg", 
                   'class': GVSvgDoc }]
    
    _formats += [{ 'type' : "svgz",
                   'descr': _("Compressed Structured Vector Graphs (SVG)"), 
                   'mime' : "image/svgz", 
                   'class': GVSvgzDoc }]

    _formats += [{ 'type' : "png",
                   'descr': _("PNG image"), 
                   'mime' : "image/png", 
                   'class': GVPngDoc }]
    
    _formats += [{ 'type' : "jpg",
                   'descr': _("JPEG image"), 
                   'mime' : "image/jpeg", 
                   'class': GVJpegDoc }]
    
    _formats += [{ 'type' : "gif",
                   'descr': _("GIF image"), 
                   'mime' : "image/gif", 
                   'class': GVGifDoc }]

if _dot_found and _gs_cmd != "":
    _formats += [{ 'type' : "pdf",
                   'descr': _("PDF"), 
                   'mime' : "application/pdf", 
                   'class': GVPdfDoc }]

#-------------------------------------------------------------------------------
#
# GraphvizFormatComboBox
#
#-------------------------------------------------------------------------------
class GraphvizFormatComboBox(gtk.ComboBox):
    """
    Format combo box class for Graphviz report.
    """
    def set(self,active=None):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)

        out_pref = Config.get(Config.OUTPUT_PREFERENCE)
        index = 0
        active_index = 0
        for item in _formats:
            name = item["descr"]
            self.store.append(row=[name])
            if item['type'] == active:
                active_index = index
            elif not active and name == out_pref:
                active_index = index
            index = index + 1
        self.set_active(active_index)

    def get_label(self):
        return _formats[self.get_active()]["descr"]

    def get_reference(self):
        return _formats[self.get_active()]["class"]

    def get_paper(self):
        return 1

    def get_styles(self):
        return 0

    def get_ext(self):
        return '.%s' % _formats[self.get_active()]["type"]

    def get_format_str(self):
        return _formats[self.get_active()]["type"]

    def get_printable(self):
        _apptype = _formats[self.get_active()]["mime"]
        print_label = None
        try:
            mprog = Mime.get_application(_apptype)
            if Utils.search_for(mprog[0]):
                print_label = _("Open in %(program_name)s") % { 'program_name':
                                                                mprog[1] }
            else:
                print_label = None
        except:
            print_label = None
        return print_label

    def get_clname(self):
        return _formats[self.get_active()]["type"]
    
#-----------------------------------------------------------------------
#
# GraphvizReportDialog
#
#-----------------------------------------------------------------------
class GraphvizReportDialog(ReportDialog):
    """A class of ReportDialog customized for graphviz based reports."""
    def __init__(self,dbstate,uistate,person,opt,name,translated_name):
        """Initialize a dialog to request that the user select options
        for a graphiz report.  See the ReportDialog class for
        more information."""
        self.category = CATEGORY_GRAPHVIZ
        ReportDialog.__init__(self,dbstate,uistate,person,opt,
                              name,translated_name)

    def make_doc_menu(self,active=None):
        """Build a menu of document types that are appropriate for
        a graphiz report."""
        self.format_menu = GraphvizFormatComboBox()
        self.format_menu.set(active)
