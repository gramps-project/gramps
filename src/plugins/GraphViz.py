#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Contributions by Lorenzo Cappelletti <lorenzo.cappelletti@email.it>
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

"Generate files/Relationship graph"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
from gettext import gettext as _
from time import asctime
import tempfile

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".GraphViz")

#------------------------------------------------------------------------
#
# GNOME/gtk
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_CODE, CATEGORY_DRAW, MODE_GUI, MODE_CLI
from ReportBase._ReportDialog import ReportDialog
from ReportBase._CommandLineReport import CommandLineReport
from Filters import GenericFilter, Rules
import RelLib
import DateHandler
import NameDisplay
import const
from BaseDoc import PAPER_LANDSCAPE
from QuestionDialog import ErrorDialog
import Errors
import Utils
import Mime

#------------------------------------------------------------------------
#
# Constant options items
#
#------------------------------------------------------------------------

class _options:
    # internal ID, english option name (for cli), localized option name (for gui)
    formats = (
        ("ps", "Postscript", _("Postscript"), "application/postscript"),
        ("svg", "Structured Vector Graphics (SVG)", _("Structured Vector Graphics (SVG)"), "image/svg"),
        ("svgz", "Compressed Structured Vector Graphics (SVG)", _("Compressed Structured Vector Graphs (SVG)"), "image/svgz"),
        ("png", "PNG image", _("PNG image"), "image/png"),
        ("jpg", "JPEG image", _("JPEG image"), "image/jpeg"),
        ("gif", "GIF image", _("GIF image"), "image/gif"),
    )
    fonts = (
        # Last items tells whether strings need to be converted to Latin1
        ("", "Default", _("Default")),
        ("Helvetica", "Postscript / Helvetica", _("Postscript / Helvetica")),
        ("FreeSans", "Truetype / FreeSans", _("Truetype / FreeSans")),
    )
    colors = (
        ("outline", "B&W Outline", _("B&W outline")),
        ("colored", "Colored outline", _("Colored outline")),
        ("filled", "Color fill", _("Color fill")),
    )
    ratio = (
        ("compress", "Minimal size", _("Minimal size")),
        ("fill", "Fill the given area", _("Fill the given area")),
        ("expand", "Automatically use optimal number of pages",
         _("Automatically use optimal number of pages"))
    )
    rankdir = (
        ("TB", "Vertical", _("Vertical")),
        ("LR", "Horizontal", _("Horizontal")),
    )
    pagedir = (
        ("BL", "Bottom, left",  _("Bottom, left")),
        ("BR", "Bottom, right", _("Bottom, right")),
        ("TL", "Top, left",     _("Top, left")),
        ("TR", "Top, right",    _("Top, Right")),
        ("RB", "Right, bottom", _("Right, bottom")),
        ("RT", "Right, top",    _("Right, top")), 
        ("LB", "Left, bottom",  _("Left, bottom")),
        ("LT", "Left, top",     _("Left, top")),
    )
    noteloc = (
        ("t", "Top", _("Top")),
        ("b", "Bottom", _("Bottom")),
    )
    arrowstyles = (
        ('d', "Descendants <- Ancestors",  _("Descendants <- Ancestors")),
        ('a', "Descendants -> Ancestors",  _("Descendants -> Ancestors")),
        ('da',"Descendants <-> Ancestors", _("Descendants <-> Ancestors")),
        ('',  "Descendants - Ancestors",    _("Descendants - Ancestors")),
    )

gs_cmd = ""

if os.sys.platform == "win32":
    _dot_found = Utils.search_for("dot.exe")
    
    if Utils.search_for("gswin32c.exe") == 1:
        gs_cmd = "gswin32c.exe"
    elif Utils.search_for("gswin32.exe") == 1:
        gs_cmd = "gswin32.exe"
else:
    _dot_found = Utils.search_for("dot")
    
    if Utils.search_for("gs") == 1:
        gs_cmd = "gs"

if gs_cmd != "":
    _options.formats += (("pdf", "PDF", _("PDF"), "application/pdf"),)

#------------------------------------------------------------------------
#
# Report class
#
#------------------------------------------------------------------------
class GraphViz:

    def __init__(self,database,person,options_class):
        """
        Creates ComprehensiveAncestorsReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        filter     - Filter to be applied to the people of the database.
                     The option class carries its number, and the function
                     returning the list of filters.
        font       - Font to use.
        fontsize   - Size of the font in points
        latin      - Set if text needs to be converted to latin-1
        arrow      - Arrow styles for heads and tails.
        showfamily - Whether to show family nodes.
        incid      - Whether to include IDs.
        incdate    - Whether to include dates.
        justyears  - Use years only.
        placecause - Whether to replace missing dates with place or cause
        url        - Whether to include URLs.
        rankdir    - Graph direction, LR or RL
        ratio      - Output aspect ration, fill/compress/auto
        color      - Whether to use outline, colored outline or filled color in graph
        dashedl    - Whether to use dashed lines for non-birth relationships.
        margin     - Margins, in cm.
        pagesh     - Number of pages in horizontal direction.
        pagesv     - Number of pages in vertical direction.
        pagedir    - Paging direction
        note       - Note to add to the graph
        notesize   - Note font size (in points)
        noteloc    - Note location t/b
        """
        colored = {
            'male': 'dodgerblue4',
            'female': 'deeppink',
            'unknown': 'black',
            'family': 'darkgreen'
        }
        filled = {
            'male': 'lightblue',
            'female': 'lightpink',
            'unknown': 'lightgray',
            'family': 'lightyellow'
        }
        self.database = database
        self.start_person = person

        self.paper = options_class.handler.get_paper()
        self.orient = options_class.handler.get_orientation()
        self.width = self.paper.get_width_inches()
        self.height = self.paper.get_height_inches()

        options = options_class.handler.options_dict
        self.pagedir = options['pagedir']
        self.hpages = options['pagesh']
        self.vpages = options['pagesv']
        margin_cm = options['margin']
        self.margin = round(margin_cm/2.54,2)
        if margin_cm > 0.1:
            # GraphViz has rounding errors so have to make the real
            # margins slightly smaller than (page - content size)
            self.margin_small = round((margin_cm-0.1)/2.54,2)
        else:
            self.margin_small = 0
        self.includeid = options['incid']
        self.includedates = options['incdate']
        self.includeurl = options['url']
        self.adoptionsdashed = options['dashedl']
        self.show_families = options['showfamily']
        self.just_years = options['justyears']
        self.placecause = options['placecause']
        self.rankdir = options['rankdir']
        self.ratio = options['ratio']
        self.fontname = options['font']
        self.fontsize = options['fontsize']
        self.colorize = options['color']
        if self.colorize == 'colored':
            self.colors = colored
        elif self.colorize == 'filled':
            self.colors = filled
        arrow_str = options['arrow']
        if arrow_str.find('a') + 1:
            self.arrowheadstyle = 'normal'
        else:
            self.arrowheadstyle = 'none'
        if arrow_str.find('d') + 1:
            self.arrowtailstyle = 'normal'
        else:
            self.arrowtailstyle = 'none'

        self.latin = options['latin']
        self.noteloc = options['noteloc']
        self.notesize = options['notesize']
        self.note = options['note']

        filter_num = options_class.get_filter_number()
        filters = options_class.get_report_filters(person)
        self.filter = filters[filter_num]

        the_buffer = self.get_report()

        self.f = open(options_class.get_output(),'w')
        if self.latin:
            try:
                self.f.write(the_buffer.encode('iso-8859-1', 'strict'))
            except UnicodeEncodeError:
                self.f = open(options_class.get_output(),'w')
                self.f.write(the_buffer.encode('iso-8859-1', 'replace'))
                ErrorDialog(
                    _("Your data contains characters that cannot be "
                      "converted to latin-1. These characters were "
                      "replaced with the question marks in the output. "
                      "To get these characters properly displayed, "
                      "unselect latin-1 option and try again."))
        else:
            self.f.write(the_buffer)
        self.f.close()

    def get_report(self):
        "return string of the .dot file contents"
        self.person_handles = self.filter.apply(self.database,
                    self.database.get_person_handles(sort_handles=False))
        
        # graph size
        if self.orient == PAPER_LANDSCAPE:
            rotate = 90
            sizew = (self.height - self.margin*2) * self.hpages
            sizeh = (self.width - self.margin*2) * self.vpages
        else:
            rotate = 0
            sizew = (self.width - self.margin*2) * self.hpages
            sizeh = (self.height - self.margin*2) * self.vpages
        
        
        buffer = self.get_comment_header()
        buffer += """
digraph GRAMPS_relationship_graph {
/* whole graph attributes */
bgcolor=white;
center=1;
ratio=%s;
rankdir=%s;
mclimit=2.0;
margin="%3.2f";
pagedir="%s";
page="%3.2f,%3.2f";
size="%3.2f,%3.2f";
rotate=%d;
/* default node and edge attributes */
nodesep=0.25;
edge [style=solid, arrowhead=%s arrowtail=%s];
""" %   (
        self.ratio,
        self.rankdir,
        self.margin_small,
        self.pagedir,
        self.width, self.height,
        sizew, sizeh,
        rotate,
        self.arrowheadstyle,
        self.arrowtailstyle
        )

        if self.fontname:
            font = 'fontname="%s" ' % self.fontname
        else:
            font = ''
        font += 'fontsize="%d"' % self.fontsize
        if self.colorize == 'filled':
            buffer += 'node [style=filled %s];\n' % font
        else:
            buffer += 'node [%s];\n' % font
        if self.latin:
            # GraphViz default is UTF-8
            buffer += 'charset="iso-8859-1";\n'
        
        if len(self.person_handles) > 1:
            buffer += "/* persons and their families */\n"
            buffer += self.get_persons_and_families()
            buffer += "/* link children to families */\n"
            buffer += self.get_child_links_to_families()

        if self.note:
            buffer += 'labelloc="%s";\n' % self.noteloc
            buffer += 'label="%s";\n' % self.note.replace('\n', '\\n').replace('"', '\\\"')
            buffer += 'fontsize="%d";\n' % self.notesize # in points

        return buffer + "}\n"

    
    def get_comment_header(self):
        "return comment of Gramps options which are not Graphviz options"
        return """/*
GRAMPS - Relationship graph

Generated on %s.

Report content options:
  include URLs       : %s
          IDs        : %s
          dates      : %s
  just year          : %s
  place or cause     : %s
  colorize           : %s
  dotted adoptions   : %s
  show family nodes  : %s
  pages horizontal   : %s
        vertical     : %s

For other options, see graph settings below.

If you need to switch between iso-8859-1 and utf-8 text encodings,
e.g. because you're using different font or -T output format,
just use iconv:
        iconv -f iso-8859-1 -t utf-8 old.dot > new.dot
        iconv -t utf-8 -f iso-8859-1 old.dot > new.dot
*/
""" %   (
        asctime(),
        bool(self.includeurl),
        bool(self.includeid),
        bool(self.includedates),
        bool(self.just_years),
        bool(self.placecause),
        bool(self.colorize),
        bool(self.adoptionsdashed),
        bool(self.show_families),
        self.hpages, self.vpages
        )
        

    def get_child_links_to_families(self):
        "returns string of GraphViz edges linking parents to families or children"
        person_dict = {}
        # Hash people in a dictionary for faster inclusion checking
        for person_handle in self.person_handles:
            person_dict[person_handle] = 1
        the_buffer = ""
        for person_handle in self.person_handles:
            person = self.database.get_person_from_handle(person_handle)
            p_id = person.get_gramps_id()
            for fam_handle in person.get_parent_family_handle_list():
                family = self.database.get_family_from_handle(fam_handle)
                father_handle = family.get_father_handle()
                mother_handle = family.get_mother_handle()
                for child_ref in family.get_child_ref_list():
                    if child_ref.ref == person_handle:
                        frel = child_ref.frel
                        mrel = child_ref.mrel
                        break
                if (self.show_families and
                    ((father_handle and father_handle in person_dict) or
                     (mother_handle and mother_handle in person_dict))):
                    # Link to the family node if either parent is in graph
                    the_buffer += self.get_family_link(p_id,family,frel,mrel)
                else:
                    # Link to the parents' nodes directly, if they are in graph
                    if father_handle and father_handle in person_dict:
                        the_buffer += self.get_parent_link(p_id,father_handle,frel)
                    if mother_handle and mother_handle in person_dict:
                        the_buffer += self.get_parent_link(p_id,mother_handle,mrel)
        return the_buffer

    def get_family_link(self, p_id, family, frel, mrel):
        "returns string of GraphViz edge linking child to family"
        style = ''
        adopted = ((int(frel) != RelLib.ChildRefType.BIRTH) or
                   (int(mrel) != RelLib.ChildRefType.BIRTH))
        if adopted and self.adoptionsdashed:
            style = 'style=dotted'
        return '"p%s" -> "f%s" [%s];\n' % (p_id,
                family.get_gramps_id(), style)

    def get_parent_link(self, p_id, parent_handle, rel):
        "returns string of GraphViz edge linking child to parent"
        style = ''
        if (int(rel) != RelLib.ChildRefType.BIRTH) and self.adoptionsdashed:
            style = 'style=dotted'
        parent = self.database.get_person_from_handle(parent_handle)
        return '"p%s" -> "p%s" [%s];\n' % (p_id, parent.get_gramps_id(), style)
        
    def get_persons_and_families(self):
        "returns string of GraphViz nodes for persons and their families"
        # The list of families for which we have output the node,
        # so we don't do it twice
        buffer = ""
        families_done = {}
        for person_handle in self.person_handles:
            person = self.database.get_person_from_handle(person_handle)
            p_id = person.get_gramps_id()
            # Output the person's node
            label = self.get_person_label(person)
            style = self.get_gender_style(person)
            url = ""
            if self.includeurl:
                h = person_handle
                url = ', URL="ppl/%s/%s/%s.html", ' % (h[0],h[1],h)
            buffer += '"p%s" [label="%s", %s%s];\n' % (p_id, label, style, url)
  
            # Output families where person is a parent
            if self.show_families:
                family_list = person.get_family_handle_list()
                for fam_handle in family_list:
                    fam = self.database.get_family_from_handle(fam_handle)
                    fam_id = fam.get_gramps_id()
                    if fam_handle not in families_done:
                        families_done[fam_handle] = 1
                        label = ""
                        for event_ref in fam.get_event_ref_list():
                            event = self.database.get_event_from_handle(
                                event_ref.ref)
                            if int(event.get_type()) == RelLib.EventType.MARRIAGE:
                                label = self.get_event_string(event)
                                break
                        if self.includeid:
                            label = "%s (%s)" % (label, fam_id)
                        color = ""
                        if self.colorize == 'colored':
                            color = ', color="%s"' % self.colors['family']
                        elif self.colorize == 'filled':
                            color = ', fillcolor="%s"' % self.colors['family']
                        buffer += '"f%s" [shape=ellipse, label="%s"%s];\n' % (fam_id, label, color)
                    # Link this person to all his/her families.
                    buffer += '"f%s" -> "p%s";\n' % (fam_id, p_id)
        return buffer

    def get_gender_style(self, person):
        "return gender specific person style"
        gender = person.get_gender()
        if gender == person.MALE:
            shape = 'shape="box"'
        elif gender == person.FEMALE:
            shape = 'shape="box", style="rounded"'
        else:
            shape = 'shape="hexagon"'
        if self.colorize == 'outline':
            return shape
        else:
            if gender == person.MALE:
                color = self.colors['male']
            elif gender == person.FEMALE:
                color = self.colors['female']
            else:
                color = self.colors['unknown']
            if self.colorize == 'filled':
                # In current GraphViz boxes cannot be both rounded and filled
                return 'shape="box", fillcolor="%s"' % color
            else:
                return '%s, color="%s"' % (shape, color)

    def get_person_label(self, person):
        "return person label string"
        label = NameDisplay.displayer.display_name(person.get_primary_name())
        p_id = person.get_gramps_id()
        if self.includeid:
            label = label + " (%s)" % p_id
        if self.includedates:
            birth, death = self.get_date_strings(person)
            label = label + '\\n(%s - %s)' % (birth, death)
        return label.replace('"', '\\\"')
    
    def get_date_strings(self, person):
        "returns tuple of birth/christening and death/burying date strings"
        birth_ref = person.get_birth_ref()
        if birth_ref:
            birth_event = self.database.get_event_from_handle(birth_ref.ref)
            birth = self.get_event_string(birth_event)
        else:
            birth = ''
        death_ref = person.get_death_ref()
        if death_ref:
            death_event = self.database.get_event_from_handle(death_ref.ref)
            death = self.get_event_string(death_event)
        else:
            death = ''
        if birth and death:
            return (birth, death)
        # missing info, use (first) christening/burial instead
        for event_ref in person.get_primary_event_ref_list():
            event = self.database.get_event_from_handle(event_ref.ref)
            if int(event.get_type()) == RelLib.EventType.CHRISTEN:
                if not birth:
                    birth = self.get_event_string(event)
            elif int(event.get_type()) ==  RelLib.EventType.BURIAL:
                if not death:
                    death = self.get_event_string(event)
        return (birth, death)

    def get_event_string(self, event):
        """
        return string for for an event label.
        
        Based on the data availability and preferences, we select one
        of the following for a given event:
            year only
            complete date
            place name
            cause
            empty string
        """
        if event:
            if event.get_date_object().get_year_valid():
                if self.just_years:
                    return '%i' % event.get_date_object().get_year()
                else:
                    return DateHandler.get_date(event)
            elif self.placecause:
                place_handle = event.get_place_handle()
                place = self.database.get_place_from_handle(place_handle)
                if place and place.get_title():
                    return place.get_title()
                else:
                    return '' #event.get_cause()
        return ''


#------------------------------------------------------------------------
#
# Options class 
#
#------------------------------------------------------------------------
class GraphVizOptions(ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'font'       : "",
            'fontsize'   : 14,
            'latin'      : 1,
            'arrow'      : 'd',
            'showfamily' : 1,
            'incdate'    : 1,
            'incid'      : 0,
            'justyears'  : 0,
            'placecause' : 1,
            'url'        : 1,
            'ratio'      : "compress",
            'rankdir'    : "LR",
            'color'      : "filled",
            'dashedl'    : 1,
            'margin'     : 1.0,
            'pagedir'    : 'BL',
            'pagesh'     : 1,
            'pagesv'     : 1,
            'note'       : '',
            'noteloc'    : 'b',
            'notesize'   : 32,
            'gvof'       : 'ps',
        }

        self.options_help = {
            'font'      : ("=str","Font to use in the report.",
                            [ "%s\t%s" % (item[0],item[1]) for item in _options.fonts ],
                            False),
            'fontsize'  : ("=num","Font size (in points).",
                            "Integer values"),
            'latin'     : ("=0/1","Needs to be set if font doesn't support unicode.",
                            ["Supports unicode","Supports only Latin1"],
                            True),
            'arrow'     : ("=str","Arrow styles for heads and tails.",
                            [ "%s\t%s" % (item[0],item[1]) for item in _options.arrowstyles ],
                            False),
            'showfamily': ("=0/1","Whether to show family nodes.",
                            ["Do not show family nodes","Show family nodes"],
                            True),
            'incdate'   : ("=0/1","Whether to include dates.",
                            ["Do not include dates","Include dates"],
                            True),
            'incid'     : ("=0/1","Whether to include IDs.",
                            ["Do not include IDs","Include IDs"],
                            True),
            'justyears' : ("=0/1","Whether to use years only.",
                            ["Do not use years only","Use years only"],
                            True),
            'placecause': ("=0/1","Whether to replace missing dates with place/cause.",
                            ["Do not replace blank dates","Replace blank dates"],
                            True),
            'url'       : ("=0/1","Whether to include URLs.",
                            ["Do not include URLs","Include URLs"],
                            True),
            'ratio'     : ("=str","Graph aspect ratio.",
                            [ "%s\t%s" % (item[0],item[1]) for item in _options.ratio ],
                            False),
            'rankdir'   : ("=str","Graph direction.",
                            [ "%s\t%s" % (item[0],item[1]) for item in _options.rankdir ],
                            False),
            'color'     : ("=str","Whether and how to colorize graph.",
                            [ "%s\t%s" % (item[0],item[1]) for item in _options.colors ],
                            False),
            'dashedl'   : ("=0/1","Whether to use dotted lines for non-birth relationships.",
                            ["Do not use dotted lines","Use dotted lines"],
                            True),
            'margin'    : ("=num","Margin size.",
                            "Floating point value, in cm"),
            'pagedir'   : ("=str","Paging direction.",
                            [ "%s\t%s" % (item[0],item[1]) for item in _options.pagedir ],
                            False),
            'pagesh'    : ("=num","Number of pages in horizontal direction.",
                            "Integer values"),
            'pagesv'    : ("=num","Number of pages in vertical direction.",
                            "Integer values"),
            'note'      : ("=str","Note to add to the graph.",
                            "Text"),
            'notesize'  : ("=num","Note size (in points).",
                            "Integer values"),
            'noteloc'   : ("=str","Note location.",
                            [ "%s\t%s" % (item[0],item[1]) for item in _options.noteloc ],
                            False),
            'gvof'      : ("=str","Output format to convert dot file into.",
                            [ "%s\t%s" % (item[0],item[1]) for item in _options.formats ],
                            False),
        }

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'filter'    : 0,
        }

    def get_report_filters(self,person):
        """Set up the list of possible content filters."""
        if person:
            name = person.get_primary_name().get_name()
            gramps_id = person.get_gramps_id()
        else:
            name = 'PERSON'
            gramps_id = ''

        all = GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(Rules.Person.Everyone([]))

        des = GenericFilter()
        des.set_name(_("Descendants of %s") % name)
        des.add_rule(Rules.Person.IsDescendantOf([gramps_id,1]))

        ans = GenericFilter()
        ans.set_name(_("Ancestors of %s") % name)
        ans.add_rule(Rules.Person.IsAncestorOf([gramps_id,1]))

        com = GenericFilter()
        com.set_name(_("People with common ancestor with %s") % name)
        com.add_rule(Rules.Person.HasCommonAncestorWith([gramps_id]))

        the_filters = [all,des,ans,com]
        from Filters import CustomFilters
        the_filters.extend(CustomFilters.get_filters('Person'))
        return the_filters

    def make_doc_menu(self,dialog,active=None):
        pass

    def add_list(self, options, default):
        "returns compobox of given options and default value"
        box = gtk.ComboBox()
        store = gtk.ListStore(str)
        box.set_model(store)
        cell = gtk.CellRendererText()
        box.pack_start(cell,True)
        box.add_attribute(cell,'text',0)
        index = 0
        for item in options:
            store.append(row=[item[2]])
            if item[0] == default:
                box.set_active(index)
            index = index + 1
        return box
    
    def add_user_options(self,dialog):
        if self.handler.module_name == "rel_graph2":
            dialog.make_doc_menu = self.make_doc_menu
            dialog.format_menu = GraphicsFormatComboBox()
            dialog.format_menu.set(self.options_dict['gvof'])

        # Content options tab
        msg = _("Include Birth, Marriage and Death dates")
        self.includedates_cb = gtk.CheckButton(msg)
        self.includedates_cb.set_active(self.options_dict['incdate'])
        dialog.add_option(None,
                        self.includedates_cb,
                        _("Include the dates that the individual "
                          "was born, got married and/or died "
                          "in the graph labels."))

        self.just_years_cb = gtk.CheckButton(_("Limit dates to years only"))
        self.just_years_cb.set_active(self.options_dict['justyears'])
        dialog.add_option(None,
                        self.just_years_cb,
                        _("Prints just dates' year, neither "
                          "month or day nor date approximation "
                          "or interval are shown."))

        self.place_cause_cb = gtk.CheckButton(_("Place/cause when no date"))
        self.place_cause_cb.set_active(self.options_dict['placecause'])
        dialog.add_option(None,
                        self.place_cause_cb,
                        _("When no birth, marriage, or death date "
                          "is available, the correspondent place field "
                          "(or cause field when blank place) will be used."))

        # disable other date options if no dates
        self.includedates_cb.connect('toggled',self.toggle_date)
        self.toggle_date(self.includedates_cb)

        self.includeurl_cb = gtk.CheckButton(_("Include URLs"))
        self.includeurl_cb.set_active(self.options_dict['url'])
        dialog.add_option(None,
                        self.includeurl_cb,
                        _("Include a URL in each graph node so "
                          "that PDF and imagemap files can be "
                          "generated that contain active links "
                          "to the files generated by the 'Generate "
                          "Web Site' report."))

        self.includeid_cb = gtk.CheckButton(_("Include IDs"))
        self.includeid_cb.set_active(self.options_dict['incid'])
        dialog.add_option(None,
                        self.includeid_cb,
                        _("Include individual and family IDs."))

        # GraphViz output options tab
        self.color_box = self.add_list(_options.colors,
                                        self.options_dict['color'])
        dialog.add_frame_option(_("GraphViz Options"),
                              _("Graph coloring"),
                              self.color_box,
                              _("Males will be shown with blue, females "
                                "with red.  If the sex of an individual "
                                "is unknown it will be shown with gray."))

        self.arrowstyle_box = self.add_list(_options.arrowstyles,
                                        self.options_dict['arrow'])
        dialog.add_frame_option(_("GraphViz Options"),
                                _("Arrowhead direction"),
                                self.arrowstyle_box,
                                _("Choose the direction that the arrows point."))

        self.font_box = self.add_list(_options.fonts,
                                        self.options_dict['font'])
        dialog.add_frame_option(_("GraphViz Options"),
                              _("Font family"),
                              self.font_box,
                              _("Choose the font family. If international "
                                "characters don't show, use FreeSans font. "
                                "FreeSans is available from: "
                                "http://www.nongnu.org/freefont/"))
        
        fontsize_adj = gtk.Adjustment(value=self.options_dict['fontsize'],
                                      lower=8, upper=128, step_incr=1)
        self.fontsize_sb = gtk.SpinButton(adjustment=fontsize_adj, digits=0)
        dialog.add_frame_option(_("GraphViz Options"),
                                _("Font size (in points)"),
                                self.fontsize_sb,
                                _("The font size, in points."))

        self.latin_cb = gtk.CheckButton(_("Output format/font requires text as latin-1"))
        self.latin_cb.set_active(self.options_dict['latin'])
        dialog.add_frame_option(_("GraphViz Options"), '',
                              self.latin_cb,
                              _("If text doesn't show correctly in report, use this. "
                                "Required e.g. for default font with PS output."))

        self.adoptionsdashed_cb = gtk.CheckButton(_("Indicate non-birth relationships with dotted lines"))
        self.adoptionsdashed_cb.set_active(self.options_dict['dashedl'])
        dialog.add_frame_option(_("GraphViz Options"), '',
                              self.adoptionsdashed_cb,
                              _("Non-birth relationships will show up "
                                "as dotted lines in the graph."))

        self.show_families_cb = gtk.CheckButton(_("Show family nodes"))
        self.show_families_cb.set_active(self.options_dict['showfamily'])
        dialog.add_frame_option(_("GraphViz Options"), '',
                              self.show_families_cb,
                              _("Families will show up as ellipses, linked "
                                "to parents and children."))

        # Page/layout options tab
        self.rank_box = self.add_list(_options.rankdir,
                                        self.options_dict['rankdir'])
        dialog.add_frame_option(_("Layout Options"),
                              _("Graph direction"),
                              self.rank_box,
                              _("Whether generations go from top to bottom "
                                "or left to right."))

        self.ratio_box = self.add_list(_options.ratio,
                                        self.options_dict['ratio'])
        dialog.add_frame_option(_("Layout Options"),
                              _("Aspect ratio"),
                              self.ratio_box,
                              _("Affects greatly how the graph is layed out "
                                "on the page. Multiple pages overrides the "
                                "pages settings below."))

        margin_adj = gtk.Adjustment(value=self.options_dict['margin'],
                        lower=0.0, upper=10.0, step_incr=1.0)

        self.margin_sb = gtk.SpinButton(adjustment=margin_adj, digits=1)

        dialog.add_frame_option(_("Layout Options"),
                              _("Margin size"),
                              self.margin_sb)

        hpages_adj = gtk.Adjustment(value=self.options_dict['pagesh'],
                    lower=1, upper=25, step_incr=1)
        vpages_adj = gtk.Adjustment(value=self.options_dict['pagesv'],
                    lower=1, upper=25, step_incr=1)

        self.hpages_sb = gtk.SpinButton(adjustment=hpages_adj, digits=0)
        self.vpages_sb = gtk.SpinButton(adjustment=vpages_adj, digits=0)

        dialog.add_frame_option(_("Layout Options"),
                              _("Number of Horizontal Pages"),
                              self.hpages_sb,
                              _("GraphViz can create very large graphs by "
                                "spreading the graph across a rectangular "
                                "array of pages. This controls the number "
                                "pages in the array horizontally."))
        dialog.add_frame_option(_("Layout Options"),
                              _("Number of Vertical Pages"),
                              self.vpages_sb,
                              _("GraphViz can create very large graphs "
                                "by spreading the graph across a "
                                "rectangular array of pages. This "
                                "controls the number pages in the array "
                                "vertically."))
        self.pagedir_box = self.add_list(_options.pagedir,
                                        self.options_dict['pagedir'])
        dialog.add_frame_option(_("Layout Options"),
                              _("Paging direction"),
                              self.pagedir_box,
                              _("The order in which the graph pages are output."))

        # Notes tab
        self.textbox = gtk.TextView()
        self.textbox.get_buffer().set_text(self.options_dict['note'])
        self.textbox.set_editable(1)
        swin = gtk.ScrolledWindow()
        swin.set_shadow_type(gtk.SHADOW_IN)
        swin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        swin.add(self.textbox)
        dialog.add_frame_option(_("Notes"),
                              _("Note to add to the graph"),
                              swin,
                              _("This text will be added to the graph."))
        self.noteloc_box = self.add_list(_options.noteloc,
                                        self.options_dict['noteloc'])
        dialog.add_frame_option(_("Notes"),
                              _("Note location"),
                              self.noteloc_box,
                              _("Whether note will appear on top "
                                "or bottom of the page."))

	notesize_adj = gtk.Adjustment(value=self.options_dict['notesize'],
                    lower=8, upper=128, step_incr=1)
        self.notesize_sb = gtk.SpinButton(adjustment=notesize_adj, digits=0)
        dialog.add_frame_option(_("Notes"),
                              _("Note size (in points)"),
                              self.notesize_sb,
                              _("The size of note text, in points."))


    def toggle_date(self, obj):
        self.just_years_cb.set_sensitive(self.includedates_cb.get_active())
        self.place_cause_cb.set_sensitive(self.includedates_cb.get_active())

    def parse_user_options(self,dialog):
        self.options_dict['incdate'] = int(self.includedates_cb.get_active())
        self.options_dict['url'] = int(self.includeurl_cb.get_active())
        self.options_dict['margin'] = self.margin_sb.get_value()
        self.options_dict['dashedl'] = int(self.adoptionsdashed_cb.get_active())
        self.options_dict['pagesh'] = self.hpages_sb.get_value_as_int()
        self.options_dict['pagesv'] = self.vpages_sb.get_value_as_int()
        self.options_dict['showfamily'] = int(self.show_families_cb.get_active())
        self.options_dict['fontsize'] = self.fontsize_sb.get_value_as_int()
        self.options_dict['incid'] = int(self.includeid_cb.get_active())
        self.options_dict['justyears'] = int(self.just_years_cb.get_active())
        self.options_dict['placecause'] = int(self.place_cause_cb.get_active())
        self.options_dict['latin'] = int(self.latin_cb.get_active())
        self.options_dict['ratio'] = \
                _options.ratio[self.ratio_box.get_active()][0]
        self.options_dict['rankdir'] = \
                _options.rankdir[self.rank_box.get_active()][0]
        self.options_dict['color'] = \
                _options.colors[self.color_box.get_active()][0]
        self.options_dict['arrow'] = \
                _options.arrowstyles[self.arrowstyle_box.get_active()][0]
        self.options_dict['font'] = \
                _options.fonts[self.font_box.get_active()][0]
        self.options_dict['pagedir'] = \
                _options.pagedir[self.pagedir_box.get_active()][0]
        self.options_dict['noteloc'] = \
                _options.noteloc[self.noteloc_box.get_active()][0]
        self.options_dict['notesize'] = self.notesize_sb.get_value_as_int()
        b = self.textbox.get_buffer()
        self.options_dict['note'] = \
                b.get_text(b.get_start_iter(), b.get_end_iter(), False)

        if self.handler.module_name == "rel_graph2":
            self.options_dict['gvof'] = dialog.format_menu.get_format_str()

#------------------------------------------------------------------------
#
# Dialog class
#
#------------------------------------------------------------------------
class GraphVizDialog(ReportDialog):

    def __init__(self,dbstate,uistate,person):
        self.database = dbstate.db
        self.person = person
        name = "rel_graph"
        translated_name = _("Relationship Graph")
        self.options_class = GraphVizOptions(name)
        self.category = CATEGORY_CODE
        ReportDialog.__init__(self,dbstate,uistate,person,self.options_class,
                              name,translated_name)
        response = self.window.run()
        if response == gtk.RESPONSE_OK:
            try:
                self.make_report()
            except (IOError,OSError),msg:
                ErrorDialog(str(msg))
        elif response == gtk.RESPONSE_DELETE_EVENT:
            return
        self.close()

    def make_doc_menu(self,active=None):
        """Build a one item menu of document types that are
        appropriate for this report."""
        self.format_menu = FormatComboBox()
        self.format_menu.set()

    def make_document(self):
        """Do Nothing.  This document will be created in the
        make_report routine."""
        pass
    
    def setup_style_frame(self):
        """The style frame is not used in this dialog."""
        pass

    def parse_style_frame(self):
        """The style frame is not used in this dialog."""
        pass

    def make_report(self):
        """Create the object that will produce the GraphViz file."""
        GraphViz(self.database,self.person,self.options_class)

#------------------------------------------------------------------------
#
# Combo Box classes
#
#------------------------------------------------------------------------
class FormatComboBox(gtk.ComboBox):
    """
    Format combo box class.
    
    Trivial class supporting only one format.
    """

    def set(self,tables=0,callback=None,obj=None,active=None):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)
        self.store.append(row=["Graphviz (dot)"])
        self.set_active(0)

    def get_label(self):
        return "Graphviz (dot)"

    def get_reference(self):
        return None

    def get_paper(self):
        return 1

    def get_styles(self):
        return 0

    def get_ext(self):
        return '.dot'

    def get_printable(self):
        _apptype = _options.formats[self.get_active()][3]
        print_label = None
        try:
            mprog = Mime.get_application(_apptype)
    
            if Utils.search_for(mprog[0]):
                print_label = _("Open in %(program_name)s") % { 'program_name':
                                                        mprog[1]}
            else:
                print_label = None
        except:
            print_label = None

        return print_label

    def get_clname(self):
        return 'dot'

class GraphicsFormatComboBox(gtk.ComboBox):
    """
    Format combo box class for graphical (not codegen) report.
    """

    def set(self,active=None):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)
        active_index = 0
        index = 0
        for item in _options.formats:
            self.store.append(row=[item[2]])
            if active == item[0]:
                active_index = index
            index = index + 1
        self.set_active(active_index)

    def get_label(self):
        return _options.formats[self.get_active()][2]

    def get_reference(self):
        return EmptyDoc

    def get_paper(self):
        return 1

    def get_styles(self):
        return 0

    def get_ext(self):
        return '.%s' % _options.formats[self.get_active()][0]

    def get_format_str(self):
        return _options.formats[self.get_active()][0]

    def get_printable(self):
        _apptype = _options.formats[self.get_active()][3]
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
        return 'print'

#------------------------------------------------------------------------
#
# Empty class to keep the BaseDoc-targeted format happy
#
#------------------------------------------------------------------------
class EmptyDoc:
    def __init__(self,styles,type,template,source=None):
        self.print_req = 0

    def init(self):
        pass
    
    def print_requested(self):
        self.print_req = 1

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def cl_report(database,name,category,options_str_dict):

    clr = CommandLineReport(database,name,category,GraphVizOptions,
                                   options_str_dict)

    # Exit here if show option was given
    if clr.show:
        return

    GraphViz(database,clr.person,clr.option_class)

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class GraphVizGraphics(Report):
    def __init__(self,database,person,options_class):
        self.database = database
        self.start_person = person
        self.options_class = options_class
        self.doc = options_class.get_document()

        self.user_output = options_class.get_output()
        (handle,self.junk_output) = tempfile.mkstemp(".dot", "rel_graph" )
        os.close( handle )

        self.the_format = self.options_class.handler.options_dict['gvof']
        self.the_font = self.options_class.handler.options_dict['font']

    def begin_report(self):
        self.options_class.set_output(self.junk_output)

    def write_report(self):
        GraphViz(self.database,self.start_person,self.options_class)

    def end_report(self):
    	if self.the_format == "pdf":
            # Create a temporary Postscript file
            (handle,tmp_ps) = tempfile.mkstemp(".ps", "rel_graph" )
            os.close( handle )

            # Generate Postscript using dot
            command = 'dot -Tps -o"%s" "%s"' % ( tmp_ps, self.junk_output )
            os.system(command)

            paper = self.options_class.handler.get_paper()
            # Add .5 to remove rounding errors.
            width_pt = int( (paper.get_width_inches() * 72) + 0.5 )
            height_pt = int( (paper.get_height_inches() * 72) + 0.5 )
            
            # Convert to PDF using ghostscript
            command = '%s -q -sDEVICE=pdfwrite -dNOPAUSE -dDEVICEWIDTHPOINTS=%d -dDEVICEHEIGHTPOINTS=%d -sOutputFile="%s" "%s" -c quit' \
                      % ( gs_cmd, width_pt, height_pt, self.user_output, tmp_ps )
            os.system(command)

            os.remove(tmp_ps)
            
        else:
            os.system('dot -T%s -o"%s" "%s"' %
                       (self.the_format,self.user_output,self.junk_output) )
            
        os.remove(self.junk_output)

        if self.doc.print_req:
            _apptype = None
            for format in _options.formats:
                if format[0] == self.the_format:
                    _apptype = format[3]
                    break
            if _apptype:
                try:
                    app = Mime.get_application(_apptype)
                    Utils.launch(app[0],self.user_output)
                except:
                    pass

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
def get_description():
    return _("Generates relationship graphs, currently only in GraphViz "
             "format. GraphViz (dot) can transform the graph into "
             "postscript, jpeg, png, vrml, svg, and many other formats. "
             "For more information or to get a copy of GraphViz, "
             "goto http://www.graphviz.org")

def get_description_graphics():
    return _("Generates relationship graphs using GraphViz (dot) program. "
             "This report generates dot file behind the scene and then "
             "uses dot to convert it into a graph. If you want the dot"
             "file itself, please use the Code Generators category.")

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'rel_graph',
    category = CATEGORY_CODE,
    report_class = GraphVizDialog,
    options_class = cl_report,
    modes = MODE_GUI | MODE_CLI,
    translated_name = _("Relationship Graph"),
    status = _("Stable"),
    description= get_description(),
    author_name="Donald N. Allingham",
    author_email="don@gramps-project.org"
    )

if _dot_found:
    register_report(
        name = 'rel_graph2',
        category = CATEGORY_DRAW,
        report_class = GraphVizGraphics,
        options_class = GraphVizOptions,
        modes = MODE_GUI | MODE_CLI,
        translated_name = _("Relationship Graph"),
        status = _("Stable"),
        description= get_description_graphics(),
        author_name="Donald N. Allingham",
        author_email="don@gramps-project.org"
    )
