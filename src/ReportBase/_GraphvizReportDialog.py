#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2007-2009  Stephane Charette
# Copyright (C) 2009       Gary Burton
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

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
from cStringIO import StringIO
import tempfile
import threading
import time
from types import ClassType, InstanceType
from gettext import gettext as _

#-------------------------------------------------------------------------------
#
# GTK+ modules
#
#-------------------------------------------------------------------------------
import gtk
import gobject

#-------------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------------
import Utils
from gen.plug.docgen import BaseDoc, GVDoc 
import Config
from ReportBase import CATEGORY_GRAPHVIZ
from _ReportDialog import ReportDialog
from _PaperMenu import PaperFrame
from gen.plug.menu import NumberOption, TextOption, EnumeratedListOption, \
                          BooleanOption

#-------------------------------------------------------------------------------
#
# Private Contstants
#
#-------------------------------------------------------------------------------
_FONTS = [ { 'name' : _("Default"),                   'value' : ""          },
           { 'name' : _("PostScript / Helvetica"),    'value' : "Helvetica" },
           { 'name' : _("TrueType / FreeSans"),       'value' : "FreeSans"  }  ]

_RANKDIR = [ { 'name' : _("Vertical (top to bottom)"),      'value' : "TB" },
             { 'name' : _("Vertical (bottom to top)"),      'value' : "BT" },
             { 'name' : _("Horizontal (left to right)"),    'value' : "LR" },
             { 'name' : _("Horizontal (right to left)"),    'value' : "RL" } ]

_PAGEDIR = [ { 'name' : _("Bottom, left"),                  'value' :"BL" },
             { 'name' : _("Bottom, right"),                 'value' :"BR" },
             { 'name' : _("Top, left"),                     'value' :"TL" },
             { 'name' : _("Top, Right"),                    'value' :"TR" },
             { 'name' : _("Right, bottom"),                 'value' :"RB" },
             { 'name' : _("Right, top"),                    'value' :"RT" },
             { 'name' : _("Left, bottom"),                  'value' :"LB" },
             { 'name' : _("Left, top"),                     'value' :"LT" } ]

_RATIO = [ { 'name' : _("Minimal size"),                'value': "compress" },
           { 'name' : _("Fill the given area"),         'value': "fill"      },
           { 'name' : _("Use optimal number of pages"), 'value': "expand"    } ]

_NOTELOC = [ { 'name' : _("Top"),    'value' : "t" },
             { 'name' : _("Bottom"), 'value' : "b" }]

if os.sys.platform == "win32":
    _DOT_FOUND = Utils.search_for("dot.exe")
    
    if Utils.search_for("gswin32c.exe") == 1:
        _GS_CMD = "gswin32c.exe"
    elif Utils.search_for("gswin32.exe") == 1:
        _GS_CMD = "gswin32.exe"
    else:
        _GS_CMD = ""
else:
    _DOT_FOUND = Utils.search_for("dot")
    
    if Utils.search_for("gs") == 1:
        _GS_CMD = "gs"
    else:
        _GS_CMD = ""
        
#-------------------------------------------------------------------------------
#
# Private Functions
#
#-------------------------------------------------------------------------------
def _run_long_process_in_thread(func, header):
    """
    This function will spawn a new thread to execute the provided function.
    While the function is running, a progress bar will be created. 
    The progress bar will show activity while the function executes.
    
    @param func: A function that will take an unknown amount of time to 
        complete. 
    @type category: callable
    @param header: A header for the progress bar.
        Example: "Updating Data"
    @type name: string
    @return: nothing
    
    """
    pbar = Utils.ProgressMeter(_('Processing File'))
    pbar.set_pass(total=40, 
                  mode=Utils.ProgressMeter.MODE_ACTIVITY, 
                  header=header)
    
    sys_thread = threading.Thread(target=func)
    sys_thread.start()
    
    while sys_thread.isAlive():
        # The loop runs 20 times per second until the thread completes.
        # With the progress pass total set at 40, it should move across the bar
        # every two seconds.
        time.sleep(0.05)
        pbar.step()   
    
    pbar.close()

#-------------------------------------------------------------------------------
#
# GVDocBase
#
#-------------------------------------------------------------------------------
class GVDocBase(BaseDoc, GVDoc):
    """
    Base document generator for all Graphiz document generators. Classes that
    inherit from this class will only need to implement the close function.
    The close function will generate the actual file of the appropriate type.
    """
    def __init__(self, options, paper_style):
        BaseDoc.__init__(self, None, paper_style, None)

        self._filename      = None
        self._dot           = StringIO()
        self._paper         = paper_style
        
        menu = options.menu

        self.dpi           = menu.get_option_by_name('dpi').get_value()
        self.fontfamily    = menu.get_option_by_name('font_family').get_value()
        self.fontsize      = menu.get_option_by_name('font_size').get_value()
        self.hpages        = menu.get_option_by_name('h_pages').get_value()
        self.nodesep       = menu.get_option_by_name('nodesep').get_value()
        self.noteloc       = menu.get_option_by_name('noteloc').get_value()
        self.notesize      = menu.get_option_by_name('notesize').get_value()
        self.note          = menu.get_option_by_name('note').get_value()
        self.pagedir       = menu.get_option_by_name('page_dir').get_value()
        self.rankdir       = menu.get_option_by_name('rank_dir').get_value()
        self.ranksep       = menu.get_option_by_name('ranksep').get_value()
        self.ratio         = menu.get_option_by_name('ratio').get_value()
        self.vpages        = menu.get_option_by_name('v_pages').get_value()
        self.usesubgraphs  = menu.get_option_by_name('usesubgraphs').get_value()

        paper_size          = paper_style.get_size()

        # Subtract 0.01" from the drawing area to make some room between
        # this area and the margin in order to compensate for different
        # rounding errors internally in dot
        sizew = ( paper_size.get_width()       - 
                  self._paper.get_left_margin() - 
                  self._paper.get_right_margin() ) / 2.54 - 0.01
        sizeh = ( paper_size.get_height()      - 
                  self._paper.get_top_margin()  -
                  self._paper.get_bottom_margin() ) / 2.54 - 0.01
                  
        pheight = paper_size.get_height_inches()
        pwidth = paper_size.get_width_inches()
        
        xmargin = self._paper.get_left_margin() / 2.54
        ymargin = self._paper.get_top_margin() / 2.54

        sizew = sizew * self.hpages         
        sizeh = sizeh * self.vpages
                      
        self.write( 'digraph GRAMPS_graph\n'        )
        self.write( '{\n'                           )
        self.write( '  bgcolor=white;\n'            )
        self.write( '  center="true"; \n'           )
        self.write( '  charset="utf8";\n'     )
        self.write( '  concentrate="false";\n'      )
        self.write( '  dpi="%d";\n'                 % self.dpi          )
        self.write( '  graph [fontsize=%d];\n'      % self.fontsize     )
        self.write( '  margin="%3.2f,%3.2f"; \n'    % (xmargin, ymargin))
        self.write( '  mclimit="99";\n'             )
        self.write( '  nodesep="%.2f";\n'           % self.nodesep      )
        self.write( '  outputorder="edgesfirst";\n' )
        if self.hpages == 1 and self.vpages == 1:
            self.write( '#' )   # comment out "page=" if the graph is on 1 page (bug #2121)
        self.write( '  page="%3.2f,%3.2f";\n'       % (pwidth, pheight) )
        self.write( '  pagedir="%s";\n'             % self.pagedir      )
        self.write( '  rankdir="%s";\n'             % self.rankdir      )
        self.write( '  ranksep="%.2f";\n'           % self.ranksep      )
        self.write( '  ratio="%s";\n'               % self.ratio        )
        self.write( '  searchsize="100";\n'         )
        self.write( '  size="%3.2f,%3.2f"; \n'      % (sizew, sizeh)    )
        self.write( '  splines="true";\n'           )
        self.write( '\n'                            )
        self.write( '  edge [len=0.5 style=solid arrowhead=none '
                            'arrowtail=normal fontsize=%d];\n' % self.fontsize )
        if self.fontfamily:
            self.write( '  node [style=filled fontname="%s" fontsize=%d];\n' 
                            % ( self.fontfamily, self.fontsize ) )
        else:
            self.write( '  node [style=filled fontsize=%d];\n' 
                            % self.fontsize )
        self.write( '\n' )

    def write(self, text):
        """ Write text to the dot file """
        self._dot.write(text.encode('utf8', 'xmlcharrefreplace'))

    def open(self, filename):
        """ Implement BaseDoc.open() """
        self._filename = os.path.normpath(os.path.abspath(filename))

    def close(self):
        """
        This isn't useful by itself. Other classes need to override this and
        actually generate a file.
        """
        if self.note:
            # build up the label
            label = u''
            for line in self.note:  # for every line in the note...
                line = line.strip() # ...strip whitespace from this line...
                if line != '':      # ...and if we still have a line...
                    if label != '': # ...see if we need to insert a newline...
                        label += '\\n'
                    label += line.replace('"', '\\\"')

            # after all that, see if we have a label to display
            if label != '':
                self.write( '\n')
                self.write( '  label="%s";\n'    % label         )
                self.write( '  labelloc="%s";\n' % self.noteloc  )
                self.write( '  fontsize="%d";\n' % self.notesize )

        self.write( '}\n\n' )

    def add_node(self, node_id, label, shape="", color="", 
                 style="", fillcolor="", url="", htmloutput=False):
        """
        Add a node to this graph. Nodes can be different shapes like boxes and
        circles.
        
        Implements GVDoc.add_node().
        """
        text = '['

        if shape:
            text += ' shape="%s"'       % shape
            
        if color:
            text += ' color="%s"'       % color
            
        if fillcolor:
            text += ' fillcolor="%s"'   % fillcolor

        if style:
            text += ' style="%s"'       % style

        # note that we always output a label -- even if an empty string --
        # otherwise GraphViz uses the node ID as the label which is unlikely
        # to be what the user wants to see in the graph
        if label.startswith("<") or htmloutput:
            text += ' label=<%s>'       % label
        else:
            text += ' label="%s"'       % label

        if url:
            text += ' URL="%s"'         % url

        text += " ]"
        self.write('  %s %s;\n' % (node_id, text))

    def add_link(self, id1, id2, style="", head="", tail="", comment=""):
        """
        Add a link between two nodes.
        
        Implementes GVDoc.add_link().
        """
        self.write('  %s -> %s' % (id1, id2))
        
        if style or head or tail:
            self.write(' [')
            
            if style:
                self.write(' style=%s' % style)
            if head:
                self.write(' arrowhead=%s' % head)
            if tail:
                self.write(' arrowtail=%s' % tail)
                
            self.write(' ]')

        self.write(';')

        if comment:
            self.write(' // %s' % comment)

        self.write('\n')

    def add_comment(self, comment):
        """
        Add a comment.
        
        Implementes GVDoc.add_comment().
        """
        tmp = comment.split('\n')
        for line in tmp:
            text = line.strip()
            if text == "":
                self.write('\n')
            elif text.startswith('#'):
                self.write('%s\n' % text)
            else:
                self.write('# %s\n' % text)

    def start_subgraph(self, graph_id):
        """ Implement GVDoc.start_subgraph() """
        self.write('  subgraph cluster_%s\n' % graph_id)
        self.write('  {\n')
        self.write('  style="invis";\n') # no border around subgraph (#0002176)
    
    def end_subgraph(self):
        """ Implement GVDoc.end_subgraph() """
        self.write('  }\n')

#-------------------------------------------------------------------------------
#
# GVDotDoc
#
#-------------------------------------------------------------------------------
class GVDotDoc(GVDocBase):
    """ GVDoc implementation that generates a .gv text file. """
    
    def close(self):
        """ Implements GVDocBase.close() """
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self._filename[-3:] != ".gv":
            self._filename += ".gv"
        
        _run_long_process_in_thread(self.__generate, self._filename)
        
    def __generate(self):
        """
        This function will generate the actual file. 
        It is nice to run this function in the background so that the 
        application does not appear to hang.
        """
        dotfile = open(self._filename, "w")
        dotfile.write(self._dot.getvalue())
        dotfile.close()
        
        if self.open_req:
            Utils.open_file_with_default_application(self._filename) 

#-------------------------------------------------------------------------------
#
# GVPsDoc
#
#-------------------------------------------------------------------------------
class GVPsDoc(GVDocBase):
    """ GVDoc implementation that generates a .ps file using Graphviz. """
    
    def __init__(self, options, paper_style):
        # DPI must always be 72 for PDF. 
        # GV documentation says dpi is only for image formats.
        options.menu.get_option_by_name('dpi').set_value(72)
        GVDocBase.__init__(self, options, paper_style)
        # GV documentation allow multiple pages only for ps format,
        # But it does not work with -Tps:cairo in order to
        # show Non Latin-1 letters. Force to only 1 page.
        # See bug tracker issue 2815
        options.menu.get_option_by_name('v_pages').set_value(1)
        options.menu.get_option_by_name('h_pages').set_value(1)
        GVDocBase.__init__(self, options, paper_style)
    
    def close(self):
        """ Implements GVDocBase.close() """
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self._filename[-3:] != ".ps":
            self._filename += ".ps"
        
        _run_long_process_in_thread(self.__generate, self._filename)
        
    def __generate(self):
        """
        This function will generate the actual file. 
        It is nice to run this function in the background so that the 
        application does not appear to hang.
        """
        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self._dot.getvalue())
        dotfile.close()
        
        # Generate the PS file.
        # Reason for using -Tps:cairo. Needed for Non Latin-1 letters
        # Some testing with Tps:cairo. Non Latin-1 letters are OK i all cases:
        # Output format:   ps       PDF-GostScript  PDF-GraphViz
        # Single page      OK           OK              OK
        # Multip page    1 page,        OK             1 page,
        #               corrupted                    set by gramps
        # If I take a correct multip page PDF and convert it with pdf2ps I get multip pages,
        # but the output is clipped, some margins have disappeared. I used 1 inch margins always.
        # See bug tracker issue 2815

        os.system( 'dot -Tps:cairo -o"%s" "%s"' % (self._filename, tmp_dot) )
        # Delete the temporary dot file
        os.remove(tmp_dot)
        
        if self.open_req:
            Utils.open_file_with_default_application(self._filename)

#-------------------------------------------------------------------------------
#
# GVSvgDoc
#
#-------------------------------------------------------------------------------
class GVSvgDoc(GVDocBase):
    """ GVDoc implementation that generates a .svg file using Graphviz. """

    def __init__(self, options, paper_style):
        # GV documentation allow multiple pages only for ps format,
        # which also includes pdf via ghostscript.
        options.menu.get_option_by_name('v_pages').set_value(1)
        options.menu.get_option_by_name('h_pages').set_value(1)
        GVDocBase.__init__(self, options, paper_style)
    
    def close(self):
        """ Implements GVDocBase.close() """
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self._filename[-4:] != ".svg":
            self._filename += ".svg"
        
        _run_long_process_in_thread(self.__generate, self._filename)
        
    def __generate(self):
        """
        This function will generate the actual file. 
        It is nice to run this function in the background so that the 
        application does not appear to hang.
        """
        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self._dot.getvalue())
        dotfile.close()

        # Generate the SVG file.
        os.system( 'dot -Tsvg -o"%s" "%s"' % (self._filename, tmp_dot) )
        
        # Delete the temporary dot file
        os.remove(tmp_dot)
        
        if self.open_req:
            Utils.open_file_with_default_application(self._filename)
            
#-------------------------------------------------------------------------------
#
# GVSvgzDoc
#
#-------------------------------------------------------------------------------
class GVSvgzDoc(GVDocBase):
    """ GVDoc implementation that generates a .svg file using Graphviz. """

    def __init__(self, options, paper_style):
        # GV documentation allow multiple pages only for ps format,
        # which also includes pdf via ghostscript.
        options.menu.get_option_by_name('v_pages').set_value(1)
        options.menu.get_option_by_name('h_pages').set_value(1)
        GVDocBase.__init__(self, options, paper_style)
    
    def close(self):
        """ Implements GVDocBase.close() """
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self._filename[-5:] != ".svgz":
            self._filename += ".svgz"
        
        _run_long_process_in_thread(self.__generate, self._filename)
        
    def __generate(self):
        """
        This function will generate the actual file. 
        It is nice to run this function in the background so that the 
        application does not appear to hang.
        """
        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self._dot.getvalue())
        dotfile.close()
        
        # Generate the SVGZ file.
        os.system( 'dot -Tsvgz -o"%s" "%s"' % (self._filename, tmp_dot) )
        
        # Delete the temporary dot file
        os.remove(tmp_dot)
        
        if self.open_req:
            Utils.open_file_with_default_application(self._filename)

#-------------------------------------------------------------------------------
#
# GVPngDoc
#
#-------------------------------------------------------------------------------
class GVPngDoc(GVDocBase):
    """ GVDoc implementation that generates a .png file using Graphviz. """

    def __init__(self, options, paper_style):
        # GV documentation allow multiple pages only for ps format,
        # which also includes pdf via ghostscript.
        options.menu.get_option_by_name('v_pages').set_value(1)
        options.menu.get_option_by_name('h_pages').set_value(1)
        GVDocBase.__init__(self, options, paper_style)
    
    def close(self):
        """ Implements GVDocBase.close() """
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self._filename[-4:] != ".png":
            self._filename += ".png"
        
        _run_long_process_in_thread(self.__generate, self._filename)
        
    def __generate(self):
        """
        This function will generate the actual file. 
        It is nice to run this function in the background so that the 
        application does not appear to hang.
        """
        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self._dot.getvalue())
        dotfile.close()
        
        # Generate the PNG file.
        os.system( 'dot -Tpng -o"%s" "%s"' % (self._filename, tmp_dot) )
        
        # Delete the temporary dot file
        os.remove(tmp_dot)
        
        if self.open_req:
            Utils.open_file_with_default_application(self._filename)     

#-------------------------------------------------------------------------------
#
# GVJpegDoc
#
#-------------------------------------------------------------------------------
class GVJpegDoc(GVDocBase):
    """ GVDoc implementation that generates a .jpg file using Graphviz. """

    def __init__(self, options, paper_style):
        # GV documentation allow multiple pages only for ps format,
        # which also includes pdf via ghostscript.
        options.menu.get_option_by_name('v_pages').set_value(1)
        options.menu.get_option_by_name('h_pages').set_value(1)
        GVDocBase.__init__(self, options, paper_style)
    
    def close(self):
        """ Implements GVDocBase.close() """
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self._filename[-4:] != ".jpg":
            self._filename += ".jpg"
        
        _run_long_process_in_thread(self.__generate, self._filename)
        
    def __generate(self):
        """
        This function will generate the actual file. 
        It is nice to run this function in the background so that the 
        application does not appear to hang.
        """
        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self._dot.getvalue())
        dotfile.close()
        
        # Generate the JPEG file.
        os.system( 'dot -Tjpg -o"%s" "%s"' % (self._filename, tmp_dot) )
        
        # Delete the temporary dot file
        os.remove(tmp_dot)
        
        if self.open_req:
            Utils.open_file_with_default_application(self._filename)

#-------------------------------------------------------------------------------
#
# GVGifDoc
#
#-------------------------------------------------------------------------------
class GVGifDoc(GVDocBase):
    """ GVDoc implementation that generates a .gif file using Graphviz. """

    def __init__(self, options, paper_style):
        # GV documentation allow multiple pages only for ps format,
        # which also includes pdf via ghostscript.
        options.menu.get_option_by_name('v_pages').set_value(1)
        options.menu.get_option_by_name('h_pages').set_value(1)
        GVDocBase.__init__(self, options, paper_style)
    
    def close(self):
        """ Implements GVDocBase.close() """
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self._filename[-4:] != ".gif":
            self._filename += ".gif"
        
        _run_long_process_in_thread(self.__generate, self._filename)
        
    def __generate(self):
        """
        This function will generate the actual file. 
        It is nice to run this function in the background so that the 
        application does not appear to hang.
        """
        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self._dot.getvalue())
        dotfile.close()
        
        # Generate the GIF file.
        os.system( 'dot -Tgif -o"%s" "%s"' % (self._filename, tmp_dot) )
        
        # Delete the temporary dot file
        os.remove(tmp_dot)
        
        if self.open_req:
            Utils.open_file_with_default_application(self._filename)     

#-------------------------------------------------------------------------------
#
# GVPdfGvDoc
#
#-------------------------------------------------------------------------------
class GVPdfGvDoc(GVDocBase):
    """ GVDoc implementation that generates a .pdf file using Graphviz. """
    
    def __init__(self, options, paper_style):
        # DPI must always be 72 for PDF. 
        # GV documentation says dpi is only for image formats.
        options.menu.get_option_by_name('dpi').set_value(72)
        # GV documentation allow multiple pages only for ps format,
        # which also includes pdf via ghostscript.
        options.menu.get_option_by_name('v_pages').set_value(1)
        options.menu.get_option_by_name('h_pages').set_value(1)
        GVDocBase.__init__(self, options, paper_style)
    
    def close(self):
        """ Implements GVDocBase.close() """
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self._filename[-4:] != ".pdf":
            self._filename += ".pdf"
        
        _run_long_process_in_thread(self.__generate, self._filename)
        
    def __generate(self):
        """
        This function will generate the actual file. 
        It is nice to run this function in the background so that the 
        application does not appear to hang.
        """
        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self._dot.getvalue())
        dotfile.close()
        
        # Generate the PDF file.
        os.system( 'dot -Tpdf -o"%s" "%s"' % (self._filename, tmp_dot) )
        
        # Delete the temporary dot file
        os.remove(tmp_dot)
        
        if self.open_req:
            Utils.open_file_with_default_application(self._filename)

#-------------------------------------------------------------------------------
#
# GVPdfGsDoc
#
#-------------------------------------------------------------------------------
class GVPdfGsDoc(GVDocBase):
    """ GVDoc implementation that generates a .pdf file using Ghostscript. """
    def __init__(self, options, paper_style):
        # DPI must always be 72 for PDF. 
        # GV documentation says dpi is only for image formats.
        options.menu.get_option_by_name('dpi').set_value(72)
        GVDocBase.__init__(self, options, paper_style)
    
    def close(self):
        """ Implements GVDocBase.close() """
        GVDocBase.close(self)
        
        # Make sure the extension is correct
        if self._filename[-4:] != ".pdf":
            self._filename += ".pdf"
        
        _run_long_process_in_thread(self.__generate, self._filename)
        
    def __generate(self):
        """
        This function will generate the actual file. 
        It is nice to run this function in the background so that the 
        application does not appear to hang.
        """
        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv" )
        dotfile = os.fdopen(handle,"w")
        dotfile.write(self._dot.getvalue())
        dotfile.close()
        
        # Create a temporary PostScript file
        (handle, tmp_ps) = tempfile.mkstemp(".ps" )
        os.close( handle )
        
        # Generate PostScript using dot
        # Reason for using -Tps:cairo. Needed for Non Latin-1 letters
        # See bug tracker issue 2815
        command = 'dot -Tps:cairo -o"%s" "%s"' % ( tmp_ps, tmp_dot )
        os.system(command)
        
        # Add .5 to remove rounding errors.
        paper_size = self._paper.get_size()
        width_pt = int( (paper_size.get_width_inches() * 72) + 0.5 )
        height_pt = int( (paper_size.get_height_inches() * 72) + 0.5 )
        
        # Convert to PDF using ghostscript
        command = '%s -q -sDEVICE=pdfwrite -dNOPAUSE -dDEVICEWIDTHPOINTS=%d' \
                  ' -dDEVICEHEIGHTPOINTS=%d -sOutputFile="%s" "%s" -c quit' \
                  % ( _GS_CMD, width_pt, height_pt, self._filename, tmp_ps )
        os.system(command)
        
        os.remove(tmp_ps)
        os.remove(tmp_dot)
        
        if self.open_req:
            Utils.open_file_with_default_application(self._filename) 

#-------------------------------------------------------------------------------
#
# Various Graphviz formats.
#
#-------------------------------------------------------------------------------
_FORMATS = []

if _DOT_FOUND:
    
    if _GS_CMD != "":
        _FORMATS += [{ 'type' : "gspdf",
                       'ext'  : "pdf",
                       'descr': _("PDF (Ghostscript)"), 
                       'mime' : "application/pdf", 
                       'class': GVPdfGsDoc }]
        
    _FORMATS += [{ 'type' : "gvpdf",
                   'ext'  : "pdf",
                   'descr': _("PDF (Graphviz)"), 
                   'mime' : "application/pdf", 
                   'class': GVPdfGvDoc }]
    
    _FORMATS += [{ 'type' : "ps",
                   'ext'  : "ps",
                   'descr': _("PostScript"), 
                   'mime' : "application/postscript", 
                   'class': GVPsDoc }]
    
    _FORMATS += [{ 'type' : "svg",
                   'ext'  : "svg",
                   'descr': _("Structured Vector Graphics (SVG)"), 
                   'mime' : "image/svg", 
                   'class': GVSvgDoc }]
    
    _FORMATS += [{ 'type' : "svgz",
                   'ext'  : "svgz",
                   'descr': _("Compressed Structured Vector Graphs (SVG)"), 
                   'mime' : "image/svgz", 
                   'class': GVSvgzDoc }]
    
    _FORMATS += [{ 'type' : "jpg",
                   'ext'  : "jpg",
                   'descr': _("JPEG image"), 
                   'mime' : "image/jpeg", 
                   'class': GVJpegDoc }]
    
    _FORMATS += [{ 'type' : "gif",
                   'ext'  : "gif",
                   'descr': _("GIF image"), 
                   'mime' : "image/gif", 
                   'class': GVGifDoc }]
    
    _FORMATS += [{ 'type' : "png",
                   'ext'  : "png",
                   'descr': _("PNG image"), 
                   'mime' : "image/png", 
                   'class': GVPngDoc }]

_FORMATS += [{ 'type' : "dot",
               'ext'  : "gv",
               'descr': _("Graphviz File"), 
               'mime' : "text/x-graphviz", 
               'class': GVDotDoc }]

#-------------------------------------------------------------------------------
#
# GraphvizFormatComboBox
#
#-------------------------------------------------------------------------------
class GraphvizFormatComboBox(gtk.ComboBox):
    """
    Format combo box class for Graphviz report.
    """
    def set(self, active=None):
        self.store = gtk.ListStore(gobject.TYPE_STRING)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)

        index = 0
        active_index = 0
        for item in _FORMATS:
            name = item["descr"]
            self.store.append(row=[name])
            if item['type'] == active:
                active_index = index
            index = index + 1
        self.set_active(active_index)

    def get_label(self):
        return _FORMATS[self.get_active()]["descr"]

    def get_reference(self):
        return _FORMATS[self.get_active()]["class"]

    def get_paper(self):
        return 1

    def get_styles(self):
        return 0

    def get_ext(self):
        return '.%s' % _FORMATS[self.get_active()]['ext']

    def get_format_str(self):
        return _FORMATS[self.get_active()]["type"]

    def is_file_output(self):
        return True

    def get_clname(self):
        return _FORMATS[self.get_active()]["type"]
    
#-----------------------------------------------------------------------
#
# GraphvizReportDialog
#
#-----------------------------------------------------------------------
class GraphvizReportDialog(ReportDialog):
    """A class of ReportDialog customized for graphviz based reports."""
    def __init__(self, dbstate, uistate, opt, name, translated_name):
        """Initialize a dialog to request that the user select options
        for a graphiz report.  See the ReportDialog class for
        more information."""
        self.category = CATEGORY_GRAPHVIZ
        ReportDialog.__init__(self, dbstate, uistate, opt,
                              name, translated_name)
        
    def init_options(self, option_class):
        try:
            if (issubclass(option_class, object) or     # New-style class
              isinstance(options_class, ClassType)):     # Old-style class
                self.options = option_class(self.raw_name,
                                        self.dbstate.get_database())
        except TypeError:
            self.options = option_class        

        ################################
        category = _("GraphViz Layout")
        ################################
        font_family = EnumeratedListOption(_("Font family"), "")
        index = 0
        for item in _FONTS:
            font_family.add_item(item["value"], item["name"])
            index += 1
        font_family.set_help(_("Choose the font family. If international "
                                "characters don't show, use FreeSans font. "
                                "FreeSans is available from: "
                                "http://www.nongnu.org/freefont/"))
        self.options.add_menu_option(category, "font_family", font_family)

        font_size = NumberOption(_("Font size"), 14, 8, 128)
        font_size.set_help(_("The font size, in points."))
        self.options.add_menu_option(category, "font_size", font_size)
        
        rank_dir = EnumeratedListOption(_("Graph Direction"), "TB")
        index = 0
        for item in _RANKDIR:
            rank_dir.add_item(item["value"], item["name"])
            index += 1
        rank_dir.set_help(_("Whether graph goes from top to bottom "
                            "or left to right."))
        self.options.add_menu_option(category, "rank_dir", rank_dir)

        h_pages = NumberOption(_("Number of Horizontal Pages"), 1, 1, 25)
        h_pages.set_help(_("GraphViz can create very large graphs by "
                           "spreading the graph across a rectangular "
                           "array of pages. This controls the number "
                           "pages in the array horizontally. "
                           "Only valid for dot and pdf via Ghostscript."))
        self.options.add_menu_option(category, "h_pages", h_pages)
        
        v_pages = NumberOption(_("Number of Vertical Pages"), 1, 1, 25)
        v_pages.set_help(_("GraphViz can create very large graphs by "
                           "spreading the graph across a rectangular "
                           "array of pages. This controls the number "
                           "pages in the array vertically. "
                           "Only valid for dot and pdf via Ghostscript."))
        self.options.add_menu_option(category, "v_pages", v_pages)

        page_dir = EnumeratedListOption(_("Paging Direction"), "BL")
        index = 0
        for item in _PAGEDIR:
            page_dir.add_item(item["value"], item["name"])
            index += 1
        page_dir.set_help(_("The order in which the graph pages are output. "
                            "This option only applies if the horizontal pages "
                            "or vertical pages are greater than 1."))
        self.options.add_menu_option(category, "page_dir", page_dir)

        # the page direction option only makes sense when the
        # number of horizontal and/or vertical pages is > 1,
        # so we need to remember these 3 controls for later
        self.h_pages    = h_pages
        self.v_pages    = v_pages
        self.page_dir   = page_dir

        # the page direction option only makes sense when the
        # number of horizontal and/or vertical pages is > 1
        self.h_pages.connect('value-changed', self.pages_changed)
        self.v_pages.connect('value-changed', self.pages_changed)

        ################################
        category = _("GraphViz Options")
        ################################
        
        aspect_ratio = EnumeratedListOption(_("Aspect ratio"), "fill")
        index = 0
        for item in _RATIO:
            aspect_ratio.add_item(item["value"], item["name"])
            index += 1
        aspect_ratio.set_help(_("Affects greatly how the graph is layed out "
                                "on the page."))
        self.options.add_menu_option(category, "ratio", aspect_ratio)

        dpi = NumberOption(_("DPI"), 75, 20, 1200)
        dpi.set_help(_( "Dots per inch.  When creating images such as "
                        ".gif or .png files for the web, try numbers "
                        "such as 100 or 300 DPI.  When creating PostScript "
                        "or PDF files, use 72 DPI."))
        self.options.add_menu_option(category, "dpi", dpi)

        nodesep = NumberOption(_("Node spacing"), 0.20, 0.01, 5.00, 0.01)
        nodesep.set_help(_( "The minimum amount of free space, in inches, "
                            "between individual nodes.  For vertical graphs, "
                            "this corresponds to spacing between columns.  "
                            "For horizontal graphs, this corresponds to "
                            "spacing between rows."))
        self.options.add_menu_option(category, "nodesep", nodesep)

        ranksep = NumberOption(_("Rank spacing"), 0.20, 0.01, 5.00, 0.01)
        ranksep.set_help(_( "The minimum amount of free space, in inches, "
                            "between ranks.  For vertical graphs, this "
                            "corresponds to spacing between rows.  For "
                            "horizontal graphs, this corresponds to spacing "
                            "between columns."))
        self.options.add_menu_option(category, "ranksep", ranksep)

        use_subgraphs = BooleanOption(_('Use subgraphs'), True)
        use_subgraphs.set_help(_("Subgraphs can help GraphViz position "
                                "spouses together, but with non-trivial "
                                "graphs will result in longer lines and "
                                "larger graphs."))
        self.options.add_menu_option(category, "usesubgraphs", use_subgraphs)

        ################################
        category = _("Note")
        ################################
        
        note = TextOption(_("Note to add to the graph"), 
                           [""] )
        note.set_help(_("This text will be added to the graph."))
        self.options.add_menu_option(category, "note", note)
        
        noteloc = EnumeratedListOption(_("Note location"), 't')
        for i in range( 0, len(_NOTELOC) ):
            noteloc.add_item(_NOTELOC[i]["value"], _NOTELOC[i]["name"])
        noteloc.set_help(_("Whether note will appear on top "
                                "or bottom of the page."))
        self.options.add_menu_option(category, "noteloc", noteloc)
        
        notesize = NumberOption(_("Note size"), 32, 8, 128)
        notesize.set_help(_("The size of note text, in points."))
        self.options.add_menu_option(category, "notesize", notesize)

        self.options.load_previous_values()

    def pages_changed(self):
        """
        This method gets called every time the v_pages or h_pages
        options are changed; when both vertical and horizontal
        pages are set to "1", then the page_dir control needs to
        be unavailable
        """
        if  self.v_pages.get_value() > 1 or \
            self.h_pages.get_value() > 1:
            self.page_dir.set_available(True)
        else:
            self.page_dir.set_available(False)

    def init_interface(self):
        ReportDialog.init_interface(self)
        self.doc_type_changed(self.format_menu)

    def setup_format_frame(self):
        """Set up the format frame of the dialog."""
        self.format_menu = GraphvizFormatComboBox()
        self.format_menu.set(self.options.handler.get_format_name())
        self.format_menu.connect('changed', self.doc_type_changed)
        label = gtk.Label("%s:" % _("Output Format"))
        label.set_alignment(0.0, 0.5)
        self.tbl.attach(label, 1, 2, self.row, self.row+1, gtk.SHRINK|gtk.FILL)
        self.tbl.attach(self.format_menu, 2, 4, self.row, self.row+1,
                        yoptions=gtk.SHRINK)
        self.row += 1

        self.open_with_app = gtk.CheckButton(_("Open with default viewer"))
        self.tbl.attach(self.open_with_app, 2, 4, self.row, self.row+1,
                        yoptions=gtk.SHRINK)
        self.row += 1

        ext = self.format_menu.get_ext()
        if ext is None:
            ext = ""
        else:
            spath = self.get_default_directory()
            base = "%s.%s" % (self.raw_name, ext)
            spath = os.path.normpath(os.path.join(spath, base))
            self.target_fileentry.set_filename(spath)
                
    def setup_report_options_frame(self):
        self.paper_label = gtk.Label('<b>%s</b>'%_("Paper Options"))
        self.paper_label.set_use_markup(True)

        self.paper_frame = PaperFrame(
                                  self.options.handler.get_paper_metric(),
                                  self.options.handler.get_paper_name(),
                                  self.options.handler.get_orientation(),
                                  self.options.handler.get_margins(),
                                  self.options.handler.get_custom_paper_size()
                                      )
        self.notebook.insert_page(self.paper_frame, self.paper_label, 0)
        self.paper_frame.show_all()

        ReportDialog.setup_report_options_frame(self)

    def doc_type_changed(self, obj):
        """
        This routine is called when the user selects a new file
        formats for the report.  It adjust the various dialog sections
        to reflect the appropriate values for the currently selected
        file format.  For example, a HTML document doesn't need any
        paper size/orientation options, but it does need a template
        file.  Those chances are made here.
        """
        self.open_with_app.set_sensitive(True)
            
        fname = self.target_fileentry.get_full_path(0)
        (spath, ext) = os.path.splitext(fname)

        ext_val = obj.get_ext()
        if ext_val:
            fname = spath + ext_val
        else:
            fname = spath
        self.target_fileentry.set_filename(fname)
            
    def make_document(self):
        """Create a document of the type requested by the user.
        """
        pstyle = self.paper_frame.get_paper_style()
        
        self.doc = self.format(self.options, pstyle)
        
        self.options.set_document(self.doc)

        if self.open_with_app.get_active():
            self.doc.open_requested()
            
    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices.  Validate
        the output file name before doing anything else.  If there is
        a file name, gather the options and create the report."""

        # Is there a filename?  This should also test file permissions, etc.
        if not self.parse_target_frame():
            self.window.run()

        # Preparation
        self.parse_format_frame()
        self.parse_user_options()

        self.options.handler.set_paper_metric(
                                          self.paper_frame.get_paper_metric())
        self.options.handler.set_paper_name(self.paper_frame.get_paper_name())
        self.options.handler.set_orientation(self.paper_frame.get_orientation())
        self.options.handler.set_margins(self.paper_frame.get_paper_margins())
        self.options.handler.set_custom_paper_size(
                                       self.paper_frame.get_custom_paper_size())
        
        # Create the output document.
        self.make_document()
        
        # Save options
        self.options.handler.save_options()
        
    def parse_format_frame(self):
        """Parse the format frame of the dialog.  Save the user
        selected output format for later use."""
        self.format = self.format_menu.get_reference()
        format_name = self.format_menu.get_clname()
        self.options.handler.set_format_name(format_name)
            
    def setup_style_frame(self):
        """Required by ReportDialog"""
        pass
