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
# $Id$

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
from cStringIO import StringIO
import tempfile
from types import ClassType, InstanceType

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
from _PaperMenu import PaperFrame
from PluginUtils import NumberOption, FloatOption, EnumeratedListOption, TextOption, BooleanOption

#-------------------------------------------------------------------------------
#
# Private Contstants
#
#-------------------------------------------------------------------------------
_FONTS = [ { 'name' : _("Default"),                'value' : ""          },
           { 'name' : _("Postscript / Helvetica"), 'value' : "Helvetica" },
           { 'name' : _("Truetype / FreeSans"),    'value' : "FreeSans"  }  ]

_RANKDIR = [ { 'name' : _("Vertical"),             'value' : "TB" },
             { 'name' : _("Horizontal"),           'value' : "LR" } ]

_PAGEDIR = [ { 'name' : _("Bottom, left"),         'value' :"BL" },
             { 'name' : _("Bottom, right"),        'value' :"BR" },
             { 'name' : _("Top, left"),            'value' :"TL" },
             { 'name' : _("Top, Right"),           'value' :"TR" },
             { 'name' : _("Right, bottom"),        'value' :"RB" },
             { 'name' : _("Right, top"),           'value' :"RT" },
             { 'name' : _("Left, bottom"),         'value' :"LB" },
             { 'name' : _("Left, top"),            'value' :"LT" } ]

_RATIO = [ { 'name' : _("Minimal size"),                'value' : "compress" },
           { 'name' : _("Fill the given area"),         'value': "fill"      },
           { 'name' : _("Use optimal number of pages"), 'value': "expand"    } ]


_NOTELOC = [ { 'name' : _("Top"),    'value' : "t" },
             { 'name' : _("Bottom"), 'value' : "b" }]

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
    def __init__(self,options,paper_style):
        BaseDoc.BaseDoc.__init__(self,None,paper_style,None)

        self.options        = options.handler.options_dict
        self.dot            = StringIO()
        self.paper          = paper_style

        self.dpi            =           self.options['dpi'          ]
        self.fontfamily     = _FONTS[   self.options['font_family'  ]]['value']
        self.fontsize       =           self.options['font_size'    ]
        self.hpages         =           self.options['h_pages'      ]
        self.nodesep        =           self.options['nodesep'      ]
        self.noteloc        =           self.options['noteloc'      ]
        self.notesize       =           self.options['notesize'     ]
        self.note           =           self.options['note'         ]
        self.pagedir        = _PAGEDIR[ self.options['page_dir'     ]]['value']
        self.rankdir        = _RANKDIR[ self.options['rank_dir'     ]]['value']
        self.ranksep        =           self.options['ranksep'      ]
        self.ratio          = _RATIO[   self.options['ratio'        ]]['value']
        self.usesubgraphs   =           self.options['usesubgraphs' ]
        self.vpages         =           self.options['v_pages'      ]

        paper_size          = paper_style.get_size()
        pheight             = paper_size.get_height_inches()
        pwidth              = paper_size.get_width_inches()

        if self.fontfamily == "":
            self.fontfamily = "FreeSans"

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
        
        sizew = sizew * self.hpages         
        sizeh = sizeh * self.vpages
                      
        self.dot.write( 'digraph GRAMPS_graph\n'            )
        self.dot.write( '{\n'                               )
        self.dot.write( '  bgcolor=white;\n'                )
        self.dot.write( '  center="true"; \n'               )
        self.dot.write( '  charset="iso-8859-1";\n'         )
        self.dot.write( '  concentrate="false";\n'          )
        self.dot.write( '  dpi="%d";\n'                     % self.dpi          )
        self.dot.write( '  graph [fontsize=%d];\n'          % self.fontsize     )
        self.dot.write( '  mclimit="99";\n'                 )
        self.dot.write( '  nodesep="%.2f";\n'               % self.nodesep      )
        self.dot.write( '  outputorder="edgesfirst";\n'     )
        self.dot.write( '  page="%3.2f,%3.2f"; \n'          % (pwidth, pheight) )
        self.dot.write( '  pagedir="%s"; \n'                % self.pagedir      )
        self.dot.write( '  rankdir="%s"; \n'                % self.rankdir      )
        self.dot.write( '  ranksep="%.2f";\n'               % self.ranksep      )
        self.dot.write( '  ratio="%s"; \n'                  % self.ratio        )
        self.dot.write( '  rotate="%d"; \n'                 % rotate            )
        self.dot.write( '  searchsize="100";\n'             )
        self.dot.write( '  size="%3.2f,%3.2f"; \n'          % (sizew, sizeh)    )
        self.dot.write( '  splines="true";\n'               )
        self.dot.write( '\n'                                )
#        self.dot.write( '  edge [len=0.5 style=solid arrowhead=none arrowtail=normal fontsize=12];\n')
#        self.dot.write( '  node [style=filled fontname="FreeSans" fontsize=12];\n'   )
        self.dot.write( '  edge [len=0.5 style=solid arrowhead=none arrowtail=normal fontsize=%d];\n' % self.fontsize )
        self.dot.write( '  node [style=filled fontname="%s" fontsize=%d];\n' % ( self.fontfamily, self.fontsize ) )
        self.dot.write( '\n'                                                         )

    def open(self, filename):
        self.filename = os.path.normpath(os.path.abspath(filename))

    def close(self):
        """
        This isn't useful by itself. Other classes need to override this and
        actually generate a file.
        """
        if self.note:
            self.dot.write( 'labelloc="%s";\n' % self.noteloc )
            self.dot.write( 'label="' )
            for line in self.note:
                self.dot.write( '%s\\n' % line.replace('"', '\\\"') )
            self.dot.write( '";\n')
            self.dot.write( 'fontsize="%d";\n' % self.notesize )
        
        self.dot.write( '}'  )
    
    def add_node(self, id, label, shape="", color = "", 
                 style="", fillcolor="", url="" ):
        """
        Add a node to this graph. Nodes can be different shapes like boxes and
        circles.
        
        Implementes BaseDoc.GVDoc.add_node().
        """
        line  = '  "%s" ['               % id
        line += 'label="%s"'             % label
        
        if shape:
            line += ', shape="%s"'       % shape
            
        if color:
            line += ', color="%s"'       % color
            
        if fillcolor:
            line += ', fillcolor="%s"'   % fillcolor
        
        if style:
            line += ', style="%s"'         % style
        
        if url:
            line += ', URL="%s"'           % url

        line += '];\n'

        self.dot.write(line)
        
    def add_link(self, id1, id2, style="", head="", tail=""):
        """
        Add a link between two nodes.
        
        Implementes BaseDoc.GVDoc.add_link().
        """
        self.dot.write('  "%s" -> "%s"' % (id1, id2))
        
        if style or head or tail:
            self.dot.write(' [')
            
            if style:
                self.dot.write('style=%s' % style)
            if head:
                if style:
                    self.dot.write(', ')
                self.dot.write('arrowhead=%s' % head)
            if tail:
                if style or head:
                    self.dot.write(', ')
                self.dot.write('arrowtail=%s' % tail)
                
            self.dot.write(']')
            
        self.dot.write(';\n')

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
        if self.filename[-4:] != ".jpg":
            self.filename += ".jpg"

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
    
    if _gs_cmd != "":
        _formats += [{ 'type' : "pdf",
                       'descr': _("PDF"), 
                       'mime' : "application/pdf", 
                       'class': GVPdfDoc }]
    
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
    
    _formats += [{ 'type' : "jpg",
                   'descr': _("JPEG image"), 
                   'mime' : "image/jpeg", 
                   'class': GVJpegDoc }]
    
    _formats += [{ 'type' : "gif",
                   'descr': _("GIF image"), 
                   'mime' : "image/gif", 
                   'class': GVGifDoc }]
    
    _formats += [{ 'type' : "png",
                   'descr': _("PNG image"), 
                   'mime' : "image/png", 
                   'class': GVPngDoc }]

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
        
    def init_options(self,option_class):
        if type(option_class) == ClassType:
            self.options = option_class(self.raw_name)
        elif type(option_class) == InstanceType:
            self.options = option_class

        ################################
        category = _("GraphViz Options")
        ################################
        
        font_family = EnumeratedListOption(_("Font family"), 0)
        index = 0
        for item in _FONTS:
            font_family.add_item(index, item["name"])
            index+=1
        font_family.set_help(_("Choose the font family. If international "
                                "characters don't show, use FreeSans font. "
                                "FreeSans is available from: "
                                "http://www.nongnu.org/freefont/"))
        self.options.add_menu_option(category,"font_family",font_family)

        font_size = NumberOption(_("Font size"),14,8,128)
        font_size.set_help(_("The font size, in points."))
        self.options.add_menu_option(category,"font_size",font_size)
        
        rank_dir = EnumeratedListOption(_("Graph Direction"), 0)
        index = 0
        for item in _RANKDIR:
            rank_dir.add_item(index, item["name"])
            index+=1
        rank_dir.set_help(_("Whether graph goes from top to bottom "
                            "or left to right."))
        self.options.add_menu_option(category,"rank_dir",rank_dir)

        dpi = NumberOption(_("DPI"), 75, 20, 1200)
        dpi.set_help(_( "Dots per inch.  When creating images such as "
                        ".gif or .png files for the web, try numbers "
                        "such as 75 or 100 DPI.  For desktop printing, "
                        "try 300 or 600 DPI."))
        self.options.add_menu_option(category, "dpi", dpi)

        nodesep = FloatOption(_("Node spacing"), 0.20, 0.01, 5.00)
        nodesep.set_help(_( "The minimum amount of free space, in inches, "
                            "between individual nodes.  For vertical graphs, "
                            "this corresponds to spacing between columns.  "
                            "For horizontal graphs, this corresponds to "
                            "spacing between rows."))
        self.options.add_menu_option(category, "nodesep", nodesep)

        ranksep = FloatOption(_("Rank spacing"), 0.20, 0.01, 5.00)
        ranksep.set_help(_( "The minimum amount of free space, in inches, "
                            "between ranks.  For vertical graphs, this "
                            "corresponds to spacing between rows.  For "
                            "horizontal graphs, this corresponds to spacing "
                            "between columns."))
        self.options.add_menu_option(category, "ranksep", ranksep)

        aspect_ratio = EnumeratedListOption(_("Aspect ratio"), 0)
        index = 0
        for item in _RATIO:
            aspect_ratio.add_item(index, item["name"])
            index+=1
        aspect_ratio.set_help(_("Affects greatly how the graph is layed out "
                                "on the page. Multiple pages overrides the "
                                "pages settings below."))
        self.options.add_menu_option(category,"ratio",aspect_ratio)
        
        page_dir = EnumeratedListOption(_("Paging Direction"), 0)
        index = 0
        for item in _PAGEDIR:
            page_dir.add_item(index, item["name"])
            index+=1
        page_dir.set_help(_("The order in which the graph pages are output. "
                            "This option only applies if the horizontal pages "
                            "or vertical pages are greater than 1."))
        self.options.add_menu_option(category,"page_dir",page_dir)
        
        h_pages = NumberOption(_("Number of Horizontal Pages"),1,1,25)
        h_pages.set_help(_("GraphViz can create very large graphs by "
                           "spreading the graph across a rectangular "
                           "array of pages. This controls the number "
                           "pages in the array horizontally."))
        self.options.add_menu_option(category,"h_pages",h_pages)
        
        v_pages = NumberOption(_("Number of Vertical Pages"),1,1,25)
        v_pages.set_help(_("GraphViz can create very large graphs by "
                           "spreading the graph across a rectangular "
                           "array of pages. This controls the number "
                           "pages in the array vertically."))
        self.options.add_menu_option(category,"v_pages",v_pages)

        usesubgraphs = BooleanOption(_('Use subgraphs'), False)
        usesubgraphs.set_help(_("Subgraphs can help GraphViz position "
                                "certain linked nodes closer together, "
                                "but with non-trivial graphs will result "
                                "in longer lines and larger graphs."))
        self.options.add_menu_option(category, "usesubgraphs", usesubgraphs)

        ################################
        category = _("Notes")
        ################################
        
        note = TextOption(_("Note to add to the graph"), 
                           [""] )
        note.set_help(_("This text will be added to the graph."))
        self.options.add_menu_option(category,"note",note)
        
        noteloc = EnumeratedListOption(_("Note location"), 't')
        for i in range( 0, len(_NOTELOC) ):
            noteloc.add_item(_NOTELOC[i]["value"], _NOTELOC[i]["name"])
        noteloc.set_help(_("Whether note will appear on top "
                                "or bottom of the page."))
        self.options.add_menu_option(category,"noteloc",noteloc)
        
        notesize = NumberOption(_("Note size"),32,8,128)
        notesize.set_help(_("The size of note text, in points."))
        self.options.add_menu_option(category,"notesize",notesize)

        self.options.load_previous_values()
        
    def init_interface(self):
        ReportDialog.init_interface(self)
        self.doc_type_changed(self.format_menu)

    def setup_format_frame(self):
        """Set up the format frame of the dialog."""

        self.print_report = gtk.CheckButton (_("Open with application"))
        self.tbl.attach(self.print_report,2,4,self.col,self.col+1,
                        yoptions=gtk.SHRINK)
        self.col += 1

        self.format_menu = GraphvizFormatComboBox()
        self.format_menu.set(self.options.handler.get_format_name())
        self.format_menu.connect('changed',self.doc_type_changed)
        label = gtk.Label("%s:" % _("Output Format"))
        label.set_alignment(0.0,0.5)
        self.tbl.attach(label,1,2,self.col,self.col+1,gtk.SHRINK|gtk.FILL)
        self.tbl.attach(self.format_menu,2,4,self.col,self.col+1,
                        yoptions=gtk.SHRINK)
        self.col += 1

        ext = self.format_menu.get_ext()
        if ext == None:
            ext = ""
        else:
            spath = self.get_default_directory()
            if self.get_target_is_directory():
                self.target_fileentry.set_filename(spath)
            else:
                base = self.get_default_basename()
                spath = os.path.normpath("%s/%s%s" % (spath,base,ext))
                self.target_fileentry.set_filename(spath)
                
    def setup_report_options_frame(self):
        self.paper_label = gtk.Label('<b>%s</b>'%_("Paper Options"))
        self.paper_label.set_use_markup(True)

        self.paper_frame = PaperFrame(self.options.handler.get_paper_name(),
                                      self.options.handler.get_orientation())
        self.notebook.insert_page(self.paper_frame,self.paper_label,0)
        self.paper_frame.show_all()

        ReportDialog.setup_report_options_frame(self)

    def doc_type_changed(self, obj):
        """This routine is called when the user selects a new file
        formats for the report.  It adjust the various dialog sections
        to reflect the appropriate values for the currently selected
        file format.  For example, a HTML document doesn't need any
        paper size/orientation options, but it does need a template
        file.  Those chances are made here."""

        label = obj.get_printable()
        if label:
            self.print_report.set_label (label)
            self.print_report.set_sensitive (True)
        else:
            self.print_report.set_label (_("Open with application"))
            self.print_report.set_sensitive (False)
            
        fname = self.target_fileentry.get_full_path(0)
        (spath,ext) = os.path.splitext(fname)

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

        if self.print_report.get_active():
            self.doc.print_requested()
            
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
        
        self.options.handler.set_paper_name(self.paper_frame.get_paper_name())
        self.options.handler.set_orientation(self.paper_frame.get_orientation())

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
        """Required by ReportDialog:BareReportDialog"""
        pass
