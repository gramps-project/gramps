# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2002       Gary Shao
# Copyright (C) 2007       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2017       Jonathan Biegert <azrdev@qrdn.de>
# Copyright (C) 2017       Mindaugas Baranauskas
# Copyright (C) 2017       Paul Culley
# Copyright (C) 2018       Christophe aka khrys63
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
""" Graphviz adapter for Graphs """
#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
import os
from io import BytesIO
import tempfile
from subprocess import Popen, PIPE

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from ...utils.file import search_for, where_is
from . import BaseDoc
from ..menu import NumberOption, TextOption, EnumeratedListOption, \
    BooleanOption
from ...constfunc import win

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".graphdoc")

#-------------------------------------------------------------------------
#
# Private Constants
#
#-------------------------------------------------------------------------
_FONTS = [{'name' : _("Default"), 'value' : "serif"},
          {'name' : _("PostScript / Helvetica"), 'value' : "Helvetica"},
          {'name' : _("TrueType / FreeSans"), 'value' : "FreeSans"}]

_RANKDIR = [{'name' : _("Vertical (↓)"), 'value'   : "TB"},
            {'name' : _("Vertical (↑)"), 'value'   : "BT"},
            {'name' : _("Horizontal (→)"), 'value' : "LR"},
            {'name' : _("Horizontal (←)"), 'value' : "RL"}]

_NODE_PORTS = {"TB" : ("n", "s"),
               "BT" : ("s", "n"),
               "LR" : ("w", "e"),
               "RL" : ("e", "w")}

_PAGEDIR = [{'name' : _("Bottom, left"), 'value'  : "BL"},
            {'name' : _("Bottom, right"), 'value' : "BR"},
            {'name' : _("Top, left"), 'value'     : "TL"},
            {'name' : _("Top, Right"), 'value'    : "TR"},
            {'name' : _("Right, bottom"), 'value' : "RB"},
            {'name' : _("Right, top"), 'value'    : "RT"},
            {'name' : _("Left, bottom"), 'value'  : "LB"},
            {'name' : _("Left, top"), 'value'     : "LT"}]

_RATIO = [{'name' : _("Compress to minimal size"), 'value': "compress"},
          {'name' : _("Fill the given area"), 'value': "fill"},
          {'name' : _("Expand uniformly"), 'value': "expand"}]

_NOTELOC = [{'name' : _("Top"), 'value' : "t"},
            {'name' : _("Bottom"), 'value' : "b"}]

_SPLINE = [{'name' : _("Straight"), 'value' : "false"},
           {'name' : _("Curved"), 'value' : "true", },
           {'name' : _("Orthogonal"), 'value' : 'ortho'}]

if win():
    _DOT_FOUND = search_for("dot.exe")

    if search_for("gswin32c.exe") == 1:
        _GS_CMD = "gswin32c.exe"
    elif search_for("gswin32.exe") == 1:
        _GS_CMD = "gswin32.exe"
    else:
        _GS_CMD = ""
else:
    _DOT_FOUND = search_for("dot")
    _GS_CMD = where_is("gs")


#------------------------------------------------------------------------------
#
# GVOptions
#
#------------------------------------------------------------------------------
class GVOptions:
    """
    Defines all of the controls necessary
    to configure the graph reports.
    """
    def __init__(self):
        self.h_pages = None
        self.v_pages = None
        self.page_dir = None
        self.dpi = None

    def add_menu_options(self, menu):
        """
        Add all graph related options to the menu.

        :param menu: The menu the options should be added to.
        :type menu: :class:`.Menu`
        :return: nothing
        """
        ################################
        category = _("Graphviz Layout")
        ################################
        font_family = EnumeratedListOption(_("Font family"), "")
        for item in _FONTS:
            font_family.add_item(item["value"], item["name"])
        font_family.set_help(_("Choose the font family. If international "
                               "characters don't show, use FreeSans font. "
                               "FreeSans is available from: "
                               "http://www.nongnu.org/freefont/"))
        menu.add_option(category, "font_family", font_family)

        font_size = NumberOption(_("Font size"), 14, 8, 128)
        font_size.set_help(_("The font size, in points."))
        menu.add_option(category, "font_size", font_size)

        rank_dir = EnumeratedListOption(_("Graph Direction"), "TB")
        for item in _RANKDIR:
            rank_dir.add_item(item["value"], item["name"])
        rank_dir.set_help(_("Whether graph goes from top to bottom "
                            "or left to right."))
        menu.add_option(category, "rank_dir", rank_dir)

        h_pages = NumberOption(_("Number of Horizontal Pages"), 1, 1, 25)
        h_pages.set_help(_("Graphviz can create very large graphs by "
                           "spreading the graph across a rectangular "
                           "array of pages. This controls the number "
                           "pages in the array horizontally. "
                           "Only valid for dot and pdf via Ghostscript."))
        menu.add_option(category, "h_pages", h_pages)

        v_pages = NumberOption(_("Number of Vertical Pages"), 1, 1, 25)
        v_pages.set_help(_("Graphviz can create very large graphs by "
                           "spreading the graph across a rectangular "
                           "array of pages. This controls the number "
                           "pages in the array vertically. "
                           "Only valid for dot and pdf via Ghostscript."))
        menu.add_option(category, "v_pages", v_pages)

        page_dir = EnumeratedListOption(_("Paging Direction"), "BL")
        for item in _PAGEDIR:
            page_dir.add_item(item["value"], item["name"])
        page_dir.set_help(_("The order in which the graph pages are output. "
                            "This option only applies if the horizontal pages "
                            "or vertical pages are greater than 1."))
        menu.add_option(category, "page_dir", page_dir)

        spline = EnumeratedListOption(_("Connecting lines"), "true")
        for item in _SPLINE:
            spline.add_item(item["value"], item["name"])
        spline.set_help(_("How the lines between objects will be drawn."))
        menu.add_option(category, "spline", spline)

        node_ports = BooleanOption(_("Alternate line attachment"), False)
        node_ports.set_help(_("Whether lines attach to nodes differently"))
        menu.add_option(category, "node_ports", node_ports)

        # the page direction option only makes sense when the
        # number of horizontal and/or vertical pages is > 1,
        # so we need to remember these 3 controls for later
        self.h_pages = h_pages
        self.v_pages = v_pages
        self.page_dir = page_dir

        # the page direction option only makes sense when the
        # number of horizontal and/or vertical pages is > 1
        self.h_pages.connect('value-changed', self.pages_changed)
        self.v_pages.connect('value-changed', self.pages_changed)

        ################################
        category = _("Graphviz Options")
        ################################

        aspect_ratio = EnumeratedListOption(_("Aspect ratio"), "fill")
        for item in _RATIO:
            aspect_ratio.add_item(item["value"], item["name"])
        help_text = _(
            'Affects node spacing and scaling of the graph.\n'
            'If the graph is smaller than the print area:\n'
            '  Compress will not change the node spacing. \n'
            '  Fill will increase the node spacing to fit the print area in '
            'both width and height.\n'
            '  Expand will increase the node spacing uniformly to preserve '
            'the aspect ratio.\n'
            'If the graph is larger than the print area:\n'
            '  Compress will shrink the graph to achieve tight packing at the '
            'expense of symmetry.\n'
            '  Fill will shrink the graph to fit the print area after first '
            'increasing the node spacing.\n'
            '  Expand will shrink the graph uniformly to fit the print area.')
        aspect_ratio.set_help(help_text)
        menu.add_option(category, "ratio", aspect_ratio)

        dpi = NumberOption(_("DPI"), 75, 20, 1200)
        dpi.set_help(_("Dots per inch.  When creating images such as "
                       ".gif or .png files for the web, try numbers "
                       "such as 100 or 300 DPI.  PostScript and PDF files "
                       "always use 72 DPI."))
        menu.add_option(category, "dpi", dpi)
        self.dpi = dpi

        nodesep = NumberOption(_("Node spacing"), 0.20, 0.01, 5.00, 0.01)
        nodesep.set_help(_("The minimum amount of free space, in inches, "
                           "between individual nodes.  For vertical graphs, "
                           "this corresponds to spacing between columns.  "
                           "For horizontal graphs, this corresponds to "
                           "spacing between rows."))
        menu.add_option(category, "nodesep", nodesep)

        ranksep = NumberOption(_("Rank spacing"), 0.20, 0.01, 5.00, 0.01)
        ranksep.set_help(_("The minimum amount of free space, in inches, "
                           "between ranks.  For vertical graphs, this "
                           "corresponds to spacing between rows.  For "
                           "horizontal graphs, this corresponds to spacing "
                           "between columns."))
        menu.add_option(category, "ranksep", ranksep)

        use_subgraphs = BooleanOption(_('Use subgraphs'), True)
        use_subgraphs.set_help(_("Subgraphs can help Graphviz position "
                                 "spouses together, but with non-trivial "
                                 "graphs will result in longer lines and "
                                 "larger graphs."))
        menu.add_option(category, "usesubgraphs", use_subgraphs)

        ################################
        category = _("Note")
        ################################

        note = TextOption(_("Note to add to the graph"),
                          [""])
        note.set_help(_("This text will be added to the graph."))
        menu.add_option(category, "note", note)

        noteloc = EnumeratedListOption(_("Note location"), 't')
        for i in range(0, len(_NOTELOC)):
            noteloc.add_item(_NOTELOC[i]["value"], _NOTELOC[i]["name"])
        noteloc.set_help(_("Whether note will appear on top "
                           "or bottom of the page."))
        menu.add_option(category, "noteloc", noteloc)

        notesize = NumberOption(_("Note size"), 32, 8, 128)
        notesize.set_help(_("The size of note text, in points."))
        menu.add_option(category, "notesize", notesize)

    def pages_changed(self):
        """
        This method gets called every time the v_pages or h_pages
        options are changed; when both vertical and horizontal
        pages are set to "1", then the page_dir control needs to
        be unavailable
        """
        if self.v_pages.get_value() > 1 or self.h_pages.get_value() > 1:
            self.page_dir.set_available(True)
        else:
            self.page_dir.set_available(False)


#------------------------------------------------------------------------------
#
# GVDoc
#
#------------------------------------------------------------------------------
class GVDoc(metaclass=ABCMeta):
    """
    Abstract Interface for Graphviz document generators. Output formats
    for Graphviz reports must implement this interface to be used by the
    report system.
    """

    @abstractmethod
    def add_node(self, node_id, label, shape="", color="",
                 style="", fillcolor="", url="", htmloutput=False):
        """
        Add a node to this graph. Nodes can be different shapes like boxes and
        circles.

        :param node_id: A unique identification value for this node.
            Example: "p55"
        :type node_id: string
        :param label: The text to be displayed in the node.
            Example: "John Smith"
        :type label: string
        :param shape: The shape for the node.
            Examples: "box", "ellipse", "circle"
        :type shape: string
        :param color: The color of the node line.
            Examples: "blue", "lightyellow"
        :type color: string
        :param style: The style of the node.
        :type style: string
        :param fillcolor: The fill color for the node.
            Examples: "blue", "lightyellow"
        :type fillcolor: string
        :param url: A URL for the node.
        :type url: string
        :param htmloutput: Whether the label contains HTML.
        :type htmloutput: boolean
        :return: nothing
        """

    @abstractmethod
    def add_link(self, id1, id2, style="", head="", tail="", comment=""):
        """
        Add a link between two nodes.

        :param id1: The unique identifier of the starting node.
            Example: "p55"
        :type id1: string
        :param id2: The unique identifier of the ending node.
            Example: "p55"
        :type id2: string
        :param comment: A text string displayed at the end of the link line.
            Example: "person C is the son of person A and person B"
        :type comment: string
        :return: nothing
        """

    @abstractmethod
    def add_comment(self, comment):
        """
        Add a comment to the source file.

        :param comment: A text string to add as a comment.
            Example: "Next comes the individuals."
        :type comment: string
        :return: nothing
        """

    @abstractmethod
    def add_samerank(self, id1, id2):
        """
        Force the same line for two linked nodes.

        :param id1: The unique identifier of the starting node.
            Example: "p55"
        :type id1: string
        :param id2: The unique identifier of the ending node.
            Example: "p55"
        :type id2: string
        :return: nothing
        """

    @abstractmethod
    def rewrite_label(self, id, label):
        """
        Rewrite the node label.

        :param id: The unique identifier of the node.
            Example: "p55"
        :type id: string
        :param label: The text to be displayed in the node.
            Example: "John Smith"
        :type label: string
        :return: nothing
        """

    @abstractmethod
    def start_subgraph(self, graph_id):
        """
        Start a subgraph in this graph.

        :param id: The unique identifier of the subgraph.
            Example: "p55"
        :type id1: string
        :return: nothing
        """

    @abstractmethod
    def end_subgraph(self):
        """
        End a subgraph that was previously started in this graph.

        :return: nothing
        """


#------------------------------------------------------------------------------
#
# GVDocBase
#
#------------------------------------------------------------------------------
class GVDocBase(BaseDoc, GVDoc):
    """
    Base document generator for all Graphviz document generators. Classes that
    inherit from this class will only need to implement the close function.
    The close function will generate the actual file of the appropriate type.
    """
    def __init__(self, options, paper_style, uistate=None):
        BaseDoc.__init__(self, None, paper_style, uistate=uistate)

        self._filename = None
        self._dot = BytesIO()
        self._paper = paper_style

        get_option = options.menu.get_option_by_name

        self.dpi = get_option('dpi').get_value()
        self.fontfamily = get_option('font_family').get_value()
        self.fontsize = get_option('font_size').get_value()
        self.hpages = get_option('h_pages').get_value()
        self.nodesep = get_option('nodesep').get_value()
        self.noteloc = get_option('noteloc').get_value()
        self.notesize = get_option('notesize').get_value()
        self.note = get_option('note').get_value()
        self.pagedir = get_option('page_dir').get_value()
        self.rankdir = get_option('rank_dir').get_value()
        self.ranksep = get_option('ranksep').get_value()
        self.ratio = get_option('ratio').get_value()
        self.vpages = get_option('v_pages').get_value()
        self.usesubgraphs = get_option('usesubgraphs').get_value()
        self.spline = get_option('spline').get_value()
        self.node_ports = get_option('node_ports').get_value()

        paper_size = paper_style.get_size()

        # Subtract 0.01" from the drawing area to make some room between
        # this area and the margin in order to compensate for different
        # rounding errors internally in dot
        sizew = (paper_size.get_width() -
                 self._paper.get_left_margin() -
                 self._paper.get_right_margin()) / 2.54 - 0.01
        sizeh = (paper_size.get_height() -
                 self._paper.get_top_margin() -
                 self._paper.get_bottom_margin()) / 2.54 - 0.01

        pheight = paper_size.get_height_inches()
        pwidth = paper_size.get_width_inches()

        xmargin = self._paper.get_left_margin() / 2.54
        ymargin = self._paper.get_top_margin() / 2.54

        sizew *= self.hpages
        sizeh *= self.vpages

        self.write(
            'digraph GRAMPS_graph\n'
            '{\n'
            '  bgcolor=white;\n'
            '  center="true"; \n'
            '  charset="utf8";\n'
            '  concentrate="false";\n' +
            '  dpi="%d";\n' % self.dpi +
            '  graph [fontsize=%d];\n' % self.fontsize +
            '  margin="%3.2f,%3.2f"; \n' % (xmargin, ymargin) +
            '  mclimit="99";\n' +
            '  nodesep="%.2f";\n' % self.nodesep +
            '  outputorder="edgesfirst";\n' +
            ('#' if self.hpages == self.vpages == 1 else '') +
            # comment out "page=" if the graph is on 1 page (bug #2121)
            '  page="%3.2f,%3.2f";\n' % (pwidth, pheight) +
            '  pagedir="%s";\n' % self.pagedir +
            '  rankdir="%s";\n' % self.rankdir +
            '  ranksep="%.2f";\n' % self.ranksep +
            '  ratio="%s";\n' % self.ratio +
            '  searchsize="100";\n' +
            '  size="%3.2f,%3.2f"; \n' % (sizew, sizeh) +
            '  splines="%s";\n' % self.spline +
            '\n' +
            '  edge [len=0.5 style=solid fontsize=%d];\n' % self.fontsize)
        if self.node_ports:
            self.write('  edge [headport=%s tailport=%s];\n'
                           % _NODE_PORTS[self.rankdir])

        if self.fontfamily:
            self.write('  node [style=filled fontname="%s" fontsize=%d];\n'
                       % (self.fontfamily, self.fontsize))
        else:
            self.write('  node [style=filled fontsize=%d];\n'
                       % self.fontsize)
        self.write('\n')

    def write(self, text):
        """ Write text to the dot file """
        self._dot.write(text.encode('utf8', 'xmlcharrefreplace'))

    def open(self, filename):
        """ Implement GVDocBase.open() """
        self._filename = os.path.normpath(os.path.abspath(filename))

    def close(self):
        """
        This isn't useful by itself. Other classes need to override this and
        actually generate a file.
        """
        if self.note:
            # build up the label
            label = ''
            for line in self.note:   # for every line in the note...
                line = line.strip()  # ...strip whitespace from this line...
                if line != '':       # ...and if we still have a line...
                    if label != '':  # ...see if we need to insert a newline...
                        label += '\\n'
                    label += line.replace('"', '\\\"')

            # after all that, see if we have a label to display
            if label != '':
                self.write(
                    '\n' +
                    '  label="%s";\n' % label +
                    '  labelloc="%s";\n' % self.noteloc +
                    '  fontsize="%d";\n' % self.notesize)

        self.write('}\n\n')

    def add_node(self, node_id, label, shape="", color="",
                 style="", fillcolor="", url="", htmloutput=False):
        """
        Add a node to this graph. Nodes can be different shapes like boxes and
        circles.

        Implements GVDocBase.add_node().
        """
        text = '['

        if shape:
            text += ' shape="%s"' % shape

        if color:
            text += ' color="%s"' % color

        if fillcolor:
            text += ' fillcolor="%s"' % fillcolor

        if style:
            text += ' style="%s"' % style

        # note that we always output a label -- even if an empty string --
        # otherwise Graphviz uses the node ID as the label which is unlikely
        # to be what the user wants to see in the graph
        if label.startswith("<") or htmloutput:
            text += ' label=<%s>' % label
        else:
            text += ' label="%s"' % label

        if url:
            text += ' URL="%s"' % url

        text += " ]"
        self.write('  "%s" %s;\n' % (node_id, text))

    def add_link(self, id1, id2, style="", head="", tail="", comment=""):
        """
        Add a link between two nodes.

        Implements GVDocBase.add_link().
        """
        self.write('  "%s" -> "%s"' % (id1, id2))

        if style or head or tail:
            self.write(' [')

            if style:
                self.write(' style=%s' % style)
            if head:
                self.write(' arrowhead=%s' % head)
            if tail:
                self.write(' arrowtail=%s' % tail)
            if head:
                if tail:
                    self.write(' dir=both')
                else:
                    self.write(' dir=forward')
            else:
                if tail:
                    self.write(' dir=back')
                else:
                    self.write(' dir=none')
            self.write(' ]')

        self.write(';')

        if comment:
            self.write(' // %s' % comment)

        self.write('\n')

    def add_comment(self, comment):
        """
        Add a comment.

        Implements GVDocBase.add_comment().
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

    def add_samerank(self, id1, id2):
        """
        Force the same line for two linked nodes.

        Implements GVDocBase.add_samerank().
        """
        self.write('  {rank=same "%s" "%s"}\n' % (id1, id2))

    def rewrite_label(self, id, label):
        """
        Rewrite the node label.

        Implements GVDocBase.rewrite_label().
        """
        self.write('  "%s" [label = "%s"]\n' % (id, label))

    def start_subgraph(self, graph_id):
        """ Implement GVDocBase.start_subgraph() """
        graph_id = graph_id.replace(' ', '_')  # for user-defined ID with space
        self.write(
            '  subgraph cluster_%s\n' % graph_id +
            '  {\n' +
            '  style="invis";\n')  # no border around subgraph (#0002176)

    def end_subgraph(self):
        """ Implement GVDocBase.end_subgraph() """
        self.write('  }\n')


#------------------------------------------------------------------------------
#
# GVDotDoc
#
#------------------------------------------------------------------------------
class GVDotDoc(GVDocBase):
    """ GVDoc implementation that generates a .gv text file. """

    def close(self):
        """ Implements GVDotDoc.close() """
        GVDocBase.close(self)

        # Make sure the extension is correct
        if self._filename[-3:] != ".gv":
            self._filename += ".gv"

        with open(self._filename, "wb") as dotfile:
            dotfile.write(self._dot.getvalue())


#------------------------------------------------------------------------------
#
# GVPsDoc
#
#------------------------------------------------------------------------------
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
        """ Implements GVPsDoc.close() """
        GVDocBase.close(self)

        # Make sure the extension is correct
        if self._filename[-3:] != ".ps":
            self._filename += ".ps"

        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv")
        dotfile = os.fdopen(handle, "wb")
        dotfile.write(self._dot.getvalue())
        dotfile.close()

        # Generate the PS file.
        # Reason for using -Tps:cairo. Needed for Non Latin-1 letters
        # Some testing with Tps:cairo. Non Latin-1 letters are OK i all cases:
        # Output format:   ps       PDF-GostScript  PDF-Graphviz
        # Single page      OK           OK              OK
        # Multip page    1 page,        OK             1 page,
        #               corrupted                    set by gramps
        # If I take a correct multip page PDF and convert it with pdf2ps I get
        # multip pages, but the output is clipped, some margins have
        # disappeared. I used 1 inch margins always.
        # See bug tracker issue 2815
        # :cairo does not work with Graphviz 2.26.3 and later See issue 4164
        # recent versions of Graphviz doesn't even try, just puts out a single
        # large page.

        command = 'dot -Tps:cairo -o"%s" "%s"' % (self._filename, tmp_dot)
        dotversion = str(Popen(['dot', '-V'],
                               stderr=PIPE).communicate(input=None)[1])
        # Problem with dot 2.26.3 and later and multiple pages, which gives
        # "cairo: out of memory" If the :cairo is skipped for these cases it
        # gives bad result for non-Latin-1 characters (utf-8).
        if (dotversion.find('2.26.3') or dotversion.find('2.28.0') != -1) and \
                (self.vpages * self.hpages) > 1:
            command = command.replace(':cairo', '')
        os.system(command)
        # Delete the temporary dot file
        os.remove(tmp_dot)


#------------------------------------------------------------------------------
#
# GVSvgDoc
#
#------------------------------------------------------------------------------
class GVSvgDoc(GVDocBase):
    """ GVDoc implementation that generates a .svg file using Graphviz. """

    def __init__(self, options, paper_style):
        # GV documentation allow multiple pages only for ps format,
        # which also includes pdf via ghostscript.
        options.menu.get_option_by_name('v_pages').set_value(1)
        options.menu.get_option_by_name('h_pages').set_value(1)
        GVDocBase.__init__(self, options, paper_style)

    def close(self):
        """ Implements GVSvgDoc.close() """
        GVDocBase.close(self)

        # Make sure the extension is correct
        if self._filename[-4:] != ".svg":
            self._filename += ".svg"

        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv")
        dotfile = os.fdopen(handle, "wb")
        dotfile.write(self._dot.getvalue())
        dotfile.close()
        # Generate the SVG file.
        os.system('dot -Tsvg:cairo -o"%s" "%s"' % (self._filename, tmp_dot))

        # Delete the temporary dot file
        os.remove(tmp_dot)


#------------------------------------------------------------------------------
#
# GVSvgzDoc
#
#------------------------------------------------------------------------------
class GVSvgzDoc(GVDocBase):
    """ GVDoc implementation that generates a .svg file using Graphviz. """

    def __init__(self, options, paper_style):
        # GV documentation allow multiple pages only for ps format,
        # which also includes pdf via ghostscript.
        options.menu.get_option_by_name('v_pages').set_value(1)
        options.menu.get_option_by_name('h_pages').set_value(1)
        GVDocBase.__init__(self, options, paper_style)

    def close(self):
        """ Implements GVSvgzDoc.close() """
        GVDocBase.close(self)

        # Make sure the extension is correct
        if self._filename[-5:] != ".svgz":
            self._filename += ".svgz"

        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv")
        dotfile = os.fdopen(handle, "wb")
        dotfile.write(self._dot.getvalue())
        dotfile.close()
        # Generate the SVGZ file.
        os.system('dot -Tsvgz -o"%s" "%s"' % (self._filename, tmp_dot))

        # Delete the temporary dot file
        os.remove(tmp_dot)


#------------------------------------------------------------------------------
#
# GVPngDoc
#
#------------------------------------------------------------------------------
class GVPngDoc(GVDocBase):
    """ GVDoc implementation that generates a .png file using Graphviz. """

    def __init__(self, options, paper_style):
        # GV documentation allow multiple pages only for ps format,
        # which also includes pdf via ghostscript.
        options.menu.get_option_by_name('v_pages').set_value(1)
        options.menu.get_option_by_name('h_pages').set_value(1)
        GVDocBase.__init__(self, options, paper_style)

    def close(self):
        """ Implements GVPngDoc.close() """
        GVDocBase.close(self)

        # Make sure the extension is correct
        if self._filename[-4:] != ".png":
            self._filename += ".png"

        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv")
        dotfile = os.fdopen(handle, "wb")
        dotfile.write(self._dot.getvalue())
        dotfile.close()
        # Generate the PNG file.
        os.system('dot -Tpng -o"%s" "%s"' % (self._filename, tmp_dot))

        # Delete the temporary dot file
        os.remove(tmp_dot)


#------------------------------------------------------------------------------
#
# GVJpegDoc
#
#------------------------------------------------------------------------------
class GVJpegDoc(GVDocBase):
    """ GVDoc implementation that generates a .jpg file using Graphviz. """

    def __init__(self, options, paper_style):
        # GV documentation allow multiple pages only for ps format,
        # which also includes pdf via ghostscript.
        options.menu.get_option_by_name('v_pages').set_value(1)
        options.menu.get_option_by_name('h_pages').set_value(1)
        GVDocBase.__init__(self, options, paper_style)

    def close(self):
        """ Implements GVJpegDoc.close() """
        GVDocBase.close(self)

        # Make sure the extension is correct
        if self._filename[-4:] != ".jpg":
            self._filename += ".jpg"

        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv")
        dotfile = os.fdopen(handle, "wb")
        dotfile.write(self._dot.getvalue())
        dotfile.close()
        # Generate the JPEG file.
        os.system('dot -Tjpg -o"%s" "%s"' % (self._filename, tmp_dot))

        # Delete the temporary dot file
        os.remove(tmp_dot)


#------------------------------------------------------------------------------
#
# GVGifDoc
#
#------------------------------------------------------------------------------
class GVGifDoc(GVDocBase):
    """ GVDoc implementation that generates a .gif file using Graphviz. """

    def __init__(self, options, paper_style):
        # GV documentation allow multiple pages only for ps format,
        # which also includes pdf via ghostscript.
        options.menu.get_option_by_name('v_pages').set_value(1)
        options.menu.get_option_by_name('h_pages').set_value(1)
        GVDocBase.__init__(self, options, paper_style)

    def close(self):
        """ Implements GVGifDoc.close() """
        GVDocBase.close(self)

        # Make sure the extension is correct
        if self._filename[-4:] != ".gif":
            self._filename += ".gif"

        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv")
        dotfile = os.fdopen(handle, "wb")
        dotfile.write(self._dot.getvalue())
        dotfile.close()
        # Generate the GIF file.
        os.system('dot -Tgif -o"%s" "%s"' % (self._filename, tmp_dot))

        # Delete the temporary dot file
        os.remove(tmp_dot)


#------------------------------------------------------------------------------
#
# GVPdfGvDoc
#
#------------------------------------------------------------------------------
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
        """ Implements GVPdfGvDoc.close() """
        GVDocBase.close(self)

        # Make sure the extension is correct
        if self._filename[-4:] != ".pdf":
            self._filename += ".pdf"

        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv")
        dotfile = os.fdopen(handle, "wb")
        dotfile.write(self._dot.getvalue())
        dotfile.close()
        fname = self._filename

        # Generate the PDF file.
        os.system('dot -Tpdf -o"%s" "%s"' % (fname, tmp_dot))

        # Delete the temporary dot file
        os.remove(tmp_dot)


#------------------------------------------------------------------------------
#
# GVPdfGsDoc
#
#------------------------------------------------------------------------------
class GVPdfGsDoc(GVDocBase):
    """ GVDoc implementation that generates a .pdf file using Ghostscript. """
    def __init__(self, options, paper_style):
        # DPI must always be 72 for PDF.
        # GV documentation says dpi is only for image formats.
        options.menu.get_option_by_name('dpi').set_value(72)
        GVDocBase.__init__(self, options, paper_style)

    def close(self):
        """ Implements GVPdfGsDoc.close() """
        GVDocBase.close(self)

        # Make sure the extension is correct
        if self._filename[-4:] != ".pdf":
            self._filename += ".pdf"

        # Create a temporary dot file
        (handle, tmp_dot) = tempfile.mkstemp(".gv")
        dotfile = os.fdopen(handle, "wb")
        dotfile.write(self._dot.getvalue())
        dotfile.close()

        # Create a temporary PostScript file
        (handle, tmp_ps) = tempfile.mkstemp(".ps")
        os.close(handle)

        # Generate PostScript using dot
        # Reason for using -Tps:cairo. Needed for Non Latin-1 letters
        # See bug tracker issue 2815
        # :cairo does not work with with multi-page See issue 4164
        # recent versions of Graphviz doesn't even try, just puts out a single
        # large page, so we use Ghostscript to split it up.

        command = 'dot -Tps:cairo -o"%s" "%s"' % (tmp_ps, tmp_dot)
        os.system(command)

        # Add .5 to remove rounding errors.
        paper_size = self._paper.get_size()
        width_pt = int((paper_size.get_width_inches() * 72) + .5)
        height_pt = int((paper_size.get_height_inches() * 72) + .5)
        if (self.vpages * self.hpages) == 1:
            # -dDEVICEWIDTHPOINTS=%d' -dDEVICEHEIGHTPOINTS=%d
            command = '%s -q -sDEVICE=pdfwrite -dNOPAUSE '\
                '-dDEVICEWIDTHPOINTS=%d -dDEVICEHEIGHTPOINTS=%d '\
                '-sOutputFile="%s" "%s" -c quit' % (
                    _GS_CMD, width_pt, height_pt, self._filename, tmp_ps)
            os.system(command)
            os.remove(tmp_ps)
            return
        # Margins (in centimeters) to pixels 72/2.54=28.345
        margin_t = int(28.345 * self._paper.get_top_margin())
        margin_b = int(28.345 * self._paper.get_bottom_margin())
        margin_r = int(28.345 * self._paper.get_right_margin())
        margin_l = int(28.345 * self._paper.get_left_margin())
        margin_x = margin_l + margin_r
        margin_y = margin_t + margin_b
        # Convert to PDF using ghostscript
        list_of_pieces = []

        x_rng = range(1, self.hpages + 1) if 'L' in self.pagedir \
            else range(self.hpages, 0, -1)
        y_rng = range(1, self.vpages + 1) if 'B' in self.pagedir \
            else range(self.vpages, 0, -1)
        if self.pagedir[0] in 'TB':
            the_list = ((__x, __y) for __y in y_rng for __x in x_rng)
        else:
            the_list = ((__x, __y) for __x in x_rng for __y in y_rng)
        for __x, __y in the_list:
            # Slit PS file to pieces of PDF
            page_offset_x = (__x - 1) * (margin_x - width_pt)
            page_offset_y = (__y - 1) * (margin_y - height_pt)
            tmp_pdf_piece = "%s_%d_%d.pdf" % (tmp_ps, __x, __y)
            list_of_pieces.append(tmp_pdf_piece)
            # Generate Ghostscript code
            command = '%s -q -dBATCH -dNOPAUSE -dSAFER '\
                '-dDEVICEWIDTHPOINTS=%d -dDEVICEHEIGHTPOINTS=%d '\
                '-dFIXEDMEDIA -sOutputFile="%s" -sDEVICE=pdfwrite '\
                '-c "<</.HWMargins [%d %d %d %d] /PageOffset [%d %d]>> '\
                'setpagedevice" -f "%s"' % (
                    _GS_CMD, width_pt + 10, height_pt + 10, tmp_pdf_piece,
                    margin_l, margin_b, margin_r, margin_t,
                    page_offset_x + 5, page_offset_y + 5, tmp_ps)
            # Execute Ghostscript
            os.system(command)
        # Merge pieces to single multipage PDF ;
        command = '%s -q -dBATCH -dNOPAUSE '\
            '-sOUTPUTFILE="%s" -sDEVICE=pdfwrite %s '\
            % (_GS_CMD, self._filename, ' '.join(list_of_pieces))
        os.system(command)

        # Clean temporary files
        os.remove(tmp_ps)
        for tmp_pdf_piece in list_of_pieces:
            os.remove(tmp_pdf_piece)
        os.remove(tmp_dot)

#------------------------------------------------------------------------------
#
# Various Graphviz formats.
#
#------------------------------------------------------------------------------
FORMATS = []

if _DOT_FOUND:

    if _GS_CMD != "":
        FORMATS += [{'type' : "gspdf",
                     'ext'  : "pdf",
                     'descr': _("PDF (Ghostscript)"),
                     'mime' : "application/pdf",
                     'class': GVPdfGsDoc}]

    FORMATS += [{'type' : "gvpdf",
                 'ext'  : "pdf",
                 'descr': _("PDF (Graphviz)"),
                 'mime' : "application/pdf",
                 'class': GVPdfGvDoc}]

    FORMATS += [{'type' : "ps",
                 'ext'  : "ps",
                 'descr': _("PostScript"),
                 'mime' : "application/postscript",
                 'class': GVPsDoc}]

    FORMATS += [{'type' : "svg",
                 'ext'  : "svg",
                 'descr': _("Structured Vector Graphics (SVG)"),
                 'mime' : "image/svg",
                 'class': GVSvgDoc}]

    FORMATS += [{'type' : "svgz",
                 'ext'  : "svgz",
                 'descr': _("Compressed Structured Vector Graphs (SVGZ)"),
                 'mime' : "image/svgz",
                 'class': GVSvgzDoc}]

    FORMATS += [{'type' : "jpg",
                 'ext'  : "jpg",
                 'descr': _("JPEG image"),
                 'mime' : "image/jpeg",
                 'class': GVJpegDoc}]

    FORMATS += [{'type' : "gif",
                 'ext'  : "gif",
                 'descr': _("GIF image"),
                 'mime' : "image/gif",
                 'class': GVGifDoc}]

    FORMATS += [{'type' : "png",
                 'ext'  : "png",
                 'descr': _("PNG image"),
                 'mime' : "image/png",
                 'class': GVPngDoc}]

FORMATS += [{'type' : "dot",
             'ext'  : "gv",
             'descr': _("Graphviz File"),
             'mime' : "text/x-graphviz",
             'class': GVDotDoc}]
