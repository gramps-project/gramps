#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
# Contributions by Lorenzo Cappelletti <lorenzo.cappelletti@email.it>
# Modified by Alex Roitman: convert to database interface, change coding style.
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
import string

from sets import Set
from time import asctime

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
import Utils
import Report
import BaseDoc
import GenericFilter
import Errors

from gettext import gettext as _
from latin_utf8 import utf8_to_latin

#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------
_scaled = 0
_single = 1
_multiple = 2

_pagecount_map = {
    _("Single (scaled)") : _scaled,
    _("Single") : _single,
    _("Multiple") : _multiple,
    }

_PS_FONT = 'Helvetica'
_TT_FONT = 'FreeSans'

#------------------------------------------------------------------------
#
# RelGraphDialog
#
#------------------------------------------------------------------------
class RelGraphDialog(Report.ReportDialog):

    # Default graph options
    File            = None
    IndividualSet   = Set()
    ShowAsStack     = 0
    ShowFamilies    = 0
    IncludeDates    = 1
    JustYear        = 0
    PlaceCause      = 1
    IncludeUrl      = 1
    IncludeId       = 0
    Colorize        = 1
    FontStyle       = _TT_FONT
    ArrowHeadStyle  = 'none'
    ArrowTailStyle  = 'normal'
    AdoptionsDashed = 1
    Width           = 0
    Height          = 0
    HPages          = 1
    VPages          = 1
    TBMargin        = 0
    LRMargin        = 0

    report_options = {}

    def __init__(self,database,person):
        Report.ReportDialog.__init__(self,database,person,self.report_options)

    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("Relationship Graph"),
                                     _("Graphical Reports"))

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Graphviz File")

    def get_print_pagecount_map(self):
        """Set up the list of possible page counts."""
        return (_pagecount_map, _("Single (scaled)"))

    def get_report_generations(self):
        """Default to 10 generations, no page breaks."""
        return (10, 0)

    def get_report_filters(self):
        """Set up the list of possible content filters."""

        name = self.person.get_primary_name().get_name()

        all = GenericFilter.GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(GenericFilter.Everyone([]))

        des = GenericFilter.GenericFilter()
        des.set_name(_("Descendants of %s") % name)
        des.add_rule(GenericFilter.IsDescendantOf([self.person.get_id()]))

        fam = GenericFilter.GenericFilter()
        fam.set_name(_("Descendant family members of %s") % name)
        fam.add_rule(GenericFilter.IsDescendantFamilyOf([self.person.get_id()]))

        ans = GenericFilter.GenericFilter()
        ans.set_name(_("Ancestors of %s") % name)
        ans.add_rule(GenericFilter.IsAncestorOf([self.person.get_id()]))

        com = GenericFilter.GenericFilter()
        com.set_name(_("People with common ancestor with %s") % name)
        com.add_rule(GenericFilter.HasCommonAncestorWith([self.person.get_id()]))

        return [all, des, fam, ans, com]

    def add_user_options(self):
        self.arrowstyle_optionmenu = gtk.OptionMenu()
        menu = gtk.Menu()

        menuitem = gtk.MenuItem(_("Descendants <- Ancestors"))
        menuitem.set_data('t', ('none', 'normal'))
        menuitem.show()
        menu.append(menuitem)

        menuitem = gtk.MenuItem(_("Descendants -> Ancestors"))
        menuitem.set_data('t', ('normal', 'none'))
        menuitem.show()
        menu.append(menuitem)

        menuitem = gtk.MenuItem(_("Descendants <-> Ancestors"))
        menuitem.set_data('t', ('normal', 'normal'))
        menuitem.show()
        menu.append(menuitem)

        menuitem = gtk.MenuItem(_("Descendants - Ancestors"))
        menuitem.set_data('t', ('none', 'none'))
        menuitem.show()
        menu.append(menuitem)

        menu.set_active(0)

        self.arrowstyle_optionmenu.set_menu(menu)

        self.font_optionmenu = gtk.OptionMenu()
        menu = gtk.Menu()

        menuitem = gtk.MenuItem(_("TrueType"))
        menuitem.set_data('t', _TT_FONT)
        menuitem.show()
        menu.append(menuitem)

        menuitem = gtk.MenuItem(_("PostScript"))
        menuitem.set_data('t', _PS_FONT)
        menuitem.show()
        menu.append(menuitem)

        self.font_optionmenu.set_menu(menu)

        self.add_frame_option(_("GraphViz Options"),
                              _("Font Options"),
                              self.font_optionmenu,
                              _("Choose the font family."))

        self.add_frame_option(_("GraphViz Options"),
                              _("Arrowhead Options"),
                              self.arrowstyle_optionmenu,
                              _("Choose the direction that the arrows point."))


        self.show_as_stack_cb = gtk.CheckButton(_("Show family as a stack"))
        self.show_as_stack_cb.set_active(self.ShowAsStack)
        self.show_as_stack_cb.connect('toggled', self._grey_out_cb)
        self.add_frame_option(_("GraphViz Options"), '',
                              self.show_as_stack_cb,
                              _("The main individual is shown along with "
                                "their spouses in a stack."))

        self.show_families_cb = gtk.CheckButton(_("Show family nodes"))
        self.show_families_cb.set_active(self.ShowFamilies)
        self.show_families_cb.connect('toggled', self._grey_out_cb)
        self.add_frame_option(_("GraphViz Options"), '',
                              self.show_families_cb,
                              _("Families will show up as ellipses, linked "
                                "to parents and children."))
        msg = _("Include IDs")
        self.includeid_cb = gtk.CheckButton(msg)
        self.includeid_cb.set_active(self.IncludeId)
        self.add_frame_option(_("GraphViz Options"), '',
                              self.includeid_cb,
                              _("Include individual and family IDs."))

        msg = _("Include Birth, Marriage and Death Dates")
        self.includedates_cb = gtk.CheckButton(msg)
        self.includedates_cb.set_active(self.IncludeDates)
        self.add_frame_option(_("GraphViz Options"), '',
                              self.includedates_cb,
                              _("Include the dates that the individual "
                                "was born, got married and/or died "
                                "in the graph labels."))

        self.just_year_cb = gtk.CheckButton(_("Limit dates to years only"))
        self.just_year_cb.set_active(self.JustYear)
        self.add_frame_option(_("GraphViz Options"), '',
                              self.just_year_cb,
                              _("Prints just dates' year, neither "
                                "month or day nor date approximation "
                                "or interval are shown."))

        self.place_cause_cb = gtk.CheckButton(_("Place/cause when no date"))
        self.place_cause_cb.set_active(self.PlaceCause)
        self.includedates_cb.connect('toggled', self._grey_out_cb)
        self.add_frame_option(_("GraphViz Options"), '',
                              self.place_cause_cb,
                              _("When no birth, marriage, or death date "
                                "is available, the correspondent place field "
                                "(or cause field when blank) will be used."))

        self.includeurl_cb = gtk.CheckButton(_("Include URLs"))
        self.includeurl_cb.set_active(self.IncludeUrl)
        self.add_frame_option(_("GraphViz Options"), '',
                              self.includeurl_cb,
                              _("Include a URL in each graph node so "
                                "that PDF and imagemap files can be "
                                "generated that contain active links "
                                "to the files generated by the 'Generate "
                                "Web Site' report."))

        self.colorize_cb = gtk.CheckButton(_("Colorize Graph"))
        self.colorize_cb.set_active(self.Colorize)
        self.add_frame_option(_("GraphViz Options"),
                              '',
                              self.colorize_cb,
                              _("Males will be outlined in blue, females "
                                "will be outlined in pink.  If the sex of "
                                "an individual is unknown it will be "
                                "outlined in black."))

        self.adoptionsdashed_cb = gtk.CheckButton(_("Indicate non-birth relationships with dashed lines"))
        self.adoptionsdashed_cb.set_active(self.AdoptionsDashed)
        self.add_frame_option(_("GraphViz Options"),
                              '',
                              self.adoptionsdashed_cb,
                              _("Non-birth relationships will show up "
                                "as dashed lines in the graph."))

        tb_margin_adj = gtk.Adjustment(value=0.5, lower=0.25,
                                      upper=100.0, step_incr=0.25)
        lr_margin_adj = gtk.Adjustment(value=0.5, lower=0.25,
                                      upper=100.0, step_incr=0.25)

        self.tb_margin_sb = gtk.SpinButton(adjustment=tb_margin_adj, digits=2)
        self.lr_margin_sb = gtk.SpinButton(adjustment=lr_margin_adj, digits=2)

        self.add_frame_option(_("Page Options"),
                              _("Top & Bottom Margins"),
                              self.tb_margin_sb)
        self.add_frame_option(_("Page Options"),
                              _("Left & Right Margins"),
                              self.lr_margin_sb)

        hpages_adj = gtk.Adjustment(value=1, lower=1, upper=25, step_incr=1)
        vpages_adj = gtk.Adjustment(value=1, lower=1, upper=25, step_incr=1)

        self.hpages_sb = gtk.SpinButton(adjustment=hpages_adj, digits=0)
        self.vpages_sb = gtk.SpinButton(adjustment=vpages_adj, digits=0)

        self.add_frame_option(_("Page Options"),
                              _("Number of Horizontal Pages"),
                              self.hpages_sb,
                              _("GraphViz can create very large graphs by "
                                "spreading the graph across a rectangular "
                                "array of pages. This controls the number "
                                "pages in the array horizontally."))
        self.add_frame_option(_("Page Options"),
                              _("Number of Vertical Pages"),
                              self.vpages_sb,
                              _("GraphViz can create very large graphs "
                                "by spreading the graph across a "
                                "rectangular array of pages. This "
                                "controls the number pages in the array "
                                "vertically."))

    def _grey_out_cb (self, button):
        if button == self.includedates_cb:
            if button.get_active():
                self.just_year_cb.set_sensitive(1)
                self.place_cause_cb.set_sensitive(1)
            else:
                self.just_year_cb.set_sensitive(0)
                self.place_cause_cb.set_sensitive(0)
        elif button == self.show_families_cb:
            if button.get_active():
                self.show_as_stack_cb.set_sensitive(0)
            else:
                self.show_as_stack_cb.set_sensitive(1)
        elif button == self.show_as_stack_cb:
            if button.get_active():
                self.show_families_cb.set_sensitive(0)
            else:
                self.show_families_cb.set_sensitive(1)

    def make_doc_menu(self):
        """Build a one item menu of document types that are
        appropriate for this report."""
        name = "Graphviz (dot)"
        menuitem = gtk.MenuItem (name)
        menuitem.set_data ("d", name)
        menuitem.set_data("paper",1)
        if os.system ("dot </dev/null 2>/dev/null") == 0:
            menuitem.set_data ("printable", _("Generate print output"))
        menuitem.show ()
        myMenu = gtk.Menu ()
        myMenu.append (menuitem)
        self.format_menu.set_menu(myMenu)

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

    def parse_other_frames(self):
        self.ShowAsStack = self.show_as_stack_cb.get_active()
        self.ShowFamilies = self.show_families_cb.get_active()
        self.IncludeDates = self.includedates_cb.get_active()
        self.JustYear = self.just_year_cb.get_active()
        self.PlaceCause = self.place_cause_cb.get_active()
        self.IncludeId = self.includeid_cb.get_active()
        self.IncludeUrl = self.includeurl_cb.get_active()
        self.Colorize = self.colorize_cb.get_active()
        self.FontStyle =\
            self.font_optionmenu.get_menu().get_active().get_data('t')
        self.ArrowHeadStyle, \
        self.ArrowTailStyle =\
            self.arrowstyle_optionmenu.get_menu().get_active().get_data('t')
        self.AdoptionsDashed = self.adoptionsdashed_cb.get_active()
        self.HPages = self.hpages_sb.get_value_as_int()
        self.VPages = self.vpages_sb.get_value_as_int()
        self.TBMargin = self.tb_margin_sb.get_value()
        self.LRMargin = self.lr_margin_sb.get_value()

    def make_report(self):
        """Create the object that will produce the GraphViz file."""
        self.Width = self.paper.get_width_inches()
        self.Height = self.paper.get_height_inches()

        self.File = open(self.target_path,"w")

        try:
            self.individual_set =\
                Set(self.filter.apply(self.db, self.db.get_person_keys()))
            self.individual_set.add(self.person.get_id())
        except Errors.FilterError, msg:
            from QuestionDialog import ErrorDialog
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)

        _writeDot(self)

        if self.print_report.get_active ():
            os.environ["DOT"] = self.target_path
            os.system ('dot -Tps "$DOT" | %s &' % Report.get_print_dialog_app ())

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
def report(database,person):
    RelGraphDialog(database,person)

#------------------------------------------------------------------------
#
# _writeDot
#
#------------------------------------------------------------------------
def _writeDot(self):
    """Write out to a file a relationship graph in dot format"""
    self.File.write("/* GRAMPS - Relationship graph\n")
    self.File.write(" *\n")
    self.File.write(" * Report options:\n")
    self.File.write(" *   font style         : %s\n" % self.FontStyle)
    self.File.write(" *   style arrow head   : %s\n" % self.ArrowHeadStyle)
    self.File.write(" *               tail   : %s\n" % self.ArrowTailStyle)
    self.File.write(" *   include URLs       : %s\n" % self.IncludeUrl)
    self.File.write(" *           IDs        : %s\n" % self.IncludeId)
    self.File.write(" *           dates      : %s\n" % self.IncludeDates)
    self.File.write(" *   just year          : %s\n" % self.JustYear)
    self.File.write(" *   place or cause     : %s\n" % self.PlaceCause)
    self.File.write(" *   colorize           : %s\n" % self.Colorize)
    self.File.write(" *   dashed adoptions   : %s\n" % self.AdoptionsDashed)
    self.File.write(" *   show families      : %s\n" % self.ShowFamilies)
    self.File.write(" *        as stack      : %s\n" % self.ShowAsStack)
    self.File.write(" *   margins top/bottm  : %s\n" % self.TBMargin)
    self.File.write(" *           left/right : %s\n" % self.LRMargin)
    self.File.write(" *   pages horizontal   : %s\n" % self.HPages)
    self.File.write(" *         vertical     : %s\n" % self.VPages)
    self.File.write(" *   page width         : %sin\n" % self.Width)
    self.File.write(" *        height        : %sin\n" % self.Height)
    self.File.write(" *\n")
    self.File.write(" * Generated on %s by GRAMPS\n" % asctime())
    self.File.write(" */\n\n")
    self.File.write("digraph GRAMPS_relationship_graph {\n")
    self.File.write("bgcolor=white;\n")
    self.File.write("rankdir=LR;\n")
    self.File.write("center=1;\n")
    self.File.write("margin=0.5;\n")
    self.File.write("ratio=fill;\n")
    self.File.write("size=\"%3.1f,%3.1f\";\n"
                    % ((self.Width*self.HPages) - (self.LRMargin*2) -
                       ((self.HPages - 1)*1.0),
                       (self.Height*self.VPages) - (self.TBMargin*2) -
                       ((self.VPages - 1)*1.0)))
    self.File.write("page=\"%3.1f,%3.1f\";\n" % (self.Width, self.Height))

    if len(self.individual_set) > 1:
        if self.ShowAsStack:
            _write_graph_record(self)
        else:
            _write_graph_box(self)

    self.File.write("}\n// File end")
    self.File.close()

#------------------------------------------------------------------------
#
# _write_graph_box
#
#------------------------------------------------------------------------
def _write_graph_box (self):
    """Write out a graph body where all individuals are separated boxes"""
    individual_nodes = Set()  # list of individual graph nodes
    family_nodes = Set()      # list of family graph nodes
    # Writes out a not for each individual
    self.File.write('\n// Individual nodes (box graph)\n')
    _write_node(self.File, shape='box', color='black', fontname=self.FontStyle)
    for individual_id in self.individual_set:
        individual_nodes.add(individual_id)
        (color, url) = _get_individual_data(self, individual_id)
        label = _get_individual_label(self, individual_id)
        _write_node(self.File, individual_id, label, color, url, 
                fontname=self.FontStyle)
    # Writes out a node for each family
    if self.ShowFamilies:
        self.File.write('\n// Family nodes (box graph)\n')
        _write_node(self.File, shape='ellipse', color='black',
                   fontname=self.FontStyle)
        for individual_id in individual_nodes:
            individual = self.db.find_person_from_id(individual_id)
            for family_id in individual.get_family_id_list():
                if family_id not in family_nodes:
                    family_nodes.add(family_id)
                    label = _get_family_id_label(self, family_id)
                    _write_node(self.File, family_id, label, 
                            fontname=self.FontStyle)
    # Links each individual to their parents/family
    self.File.write('\n// Individual edges\n')
    _write_edge(self.File, style="solid", 
                    arrowHead=self.ArrowHeadStyle,arrowTail=self.ArrowTailStyle)
    for individual_id in individual_nodes:
        individual = self.db.find_person_from_id(individual_id)
        for family_id, mother_rel_ship, father_rel_ship\
                in individual.get_parent_family_id_list():
            family =  self.db.find_family_from_id(family_id)
            father_id = family.get_father_id()
            mother_id = family.get_mother_id()
            if self.ShowFamilies and family_id in family_nodes:
                # edge from an individual to their family
                style = _get_edge_style(self, father_rel_ship, mother_rel_ship)
                _write_edge(self.File, individual_id, family_id, style)
            else:
                # edge from an individual to their parents
                if father_id and father_id in individual_nodes:
                    _write_edge(self.File, individual_id, father_id,
                               _get_edge_style(self, father_rel_ship))
                if mother_id and mother_id in individual_nodes:
                    _write_edge(self.File, individual_id, mother_id,
                               _get_edge_style(self, mother_rel_ship))
    # Links each family to its components
    if self.ShowFamilies:
        self.File.write('\n// Family edges (box graph)\n')
        _write_edge(self.File, style="solid", 
                    arrowHead=self.ArrowHeadStyle,arrowTail=self.ArrowTailStyle)
        for family_id in family_nodes:
            family = self.db.find_family_from_id(family_id)
            father_id = family.get_father_id()
            if father_id and father_id in individual_nodes:
                _write_edge(self.File, family_id, father_id)
            mother_id = family.get_mother_id()
            if mother_id and mother_id in individual_nodes:
                _write_edge(self.File, family_id, mother_id)
    # Statistics
    males = 0
    females = 0
    unknowns = 0
    for individual_id in individual_nodes:
        individual = self.db.find_person_from_id(individual_id)
        if individual.get_gender() == individual.male:
            males = males + 1
        elif individual.get_gender() == individual.female:
            females = females + 1
        else:
            unknowns = unknowns + 1
    _write_stats(self.File, males, females, unknowns, len(family_nodes))

#------------------------------------------------------------------------
#
# _writeGraphRecord
#
#------------------------------------------------------------------------
def _write_graph_record (self):
    """Write out a graph body where families are rendered as records"""
    # Builds a dictionary of family records.
    # Each record is made of an individual married with zero or
    # more individuals.
    family_nodes = {}
    if isinstance(self.filter.get_rules()[0],
                  GenericFilter.IsDescendantFamilyOf):
        # With the IsDescendantFamilyOf filter, the IndividualSet
        # includes people which are not direct descendants of the
        # active person (practically, spouses of direct
        # discendants). Because we want the graph to highlight the
        # consanguinity, IndividualSet is split in two subsets:
        # naturalRelatives (direct descendants) and its complementary
        # subset (in-law relatives).
        filter = GenericFilter.GenericFilter()
        filter.add_rule(GenericFilter.IsDescendantOf([self.person.get_id()]))
        natural_relatives =\
            Set(filter.apply(self.db, self.db.get_person_keys()))
        natural_relatives.add(self.person.get_id())
    else:
        natural_relatives = self.individual_set
    self.File.write('\n// Family nodes (record graph)\n')
    _write_node(self.File, shape='record', color='black',
               fontname=self.FontStyle)
    for individual_id in natural_relatives:
        # If both husband and wife are members of the IndividualSet,
        # only one record, with the husband first, is displayed.
        individual = self.db.find_person_from_id(individual_id)
        if individual.get_gender() == individual.female:
            # There are exactly three cases where a female node is added:
            family_id = None        # no family
            husbands = []           # filtered-in husbands (naturalRelatives)
            unknown_husbands = 0    # filtered-out/unknown husbands
            for family_id in individual.get_family_id_list():
                family = self.db.find_family_from_id(family_id)
                husband_id = family.get_father_id()
                if husband_id and husband_id in self.individual_set:
                    if husband_id not in natural_relatives:
                        husbands.append(husband_id)
                else:
                    unknown_husbands = 1
            if not family_id or len(husbands) or unknown_husbands:
                family_nodes[individual_id] = [individual_id] + husbands
        else:
            family_nodes[individual_id] = [individual_id]
            for family_id in individual.get_family_id_list():
                family = self.db.find_family_from_id(family_id)
                wife_id = family.get_mother_id()
                if wife_id in self.individual_set:
                    family_nodes[individual_id].append(wife_id)
    # Writes out all family records
    for individual_id, family_id in family_nodes.items():
        (color, url) = _get_individual_data(self, family_nodes[individual_id][0])
        label = _get_family_id_record_label(self, family_nodes[individual_id])
        _write_node(self.File, individual_id, label, color, url, 
                fontname=self.FontStyle)
    # Links individual's record to their parents' record
    # The arrow goes from the individual port of a family record
    # to the parent port of the parent's family record.
    self.File.write('\n// Individual edges\n')
    _write_edge(self.File, style="solid", 
                arrowHead=self.ArrowHeadStyle,arrowTail=self.ArrowTailStyle)
    for family_from_id, family_from_id2 in family_nodes.items():
        for individual_from_id in family_from_id2:
            individual_from = self.db.find_person_from_id(individual_from_id)
            for family_id, mother_rel_ship, father_rel_ship\
                    in individual_from.get_parent_family_id_list():
                family = self.db.find_family_from_id(family_id)
                father_id = family.get_father_id()
                mother_id = family.get_mother_id()
                # Things are complicated here because a parent may or
                # or may not exist.
                if not father_id:
                    father_id = ""
                if not mother_id:
                    mother_id = ""
                if family_nodes.has_key(father_id):
                    if mother_id in family_nodes[father_id]:
                        _write_edge(self.File, family_from_id, father_id,
                                   _get_edge_style(self, mother_rel_ship),
                                   portFrom=individual_from_id, portTo=mother_id)
                    else:
                        _write_edge(self.File, family_from_id, father_id,
                                   _get_edge_style(self, mother_rel_ship),
                                   portFrom=individual_from_id)
                if family_nodes.has_key(mother_id):
                    if father_id in family_nodes[mother_id]:
                        _write_edge(self.File, family_from_id, mother_id,
                                   _get_edge_style(self, father_rel_ship),
                                   portFrom=individual_from_id, portTo=father_id)
                    else:
                        _write_edge(self.File, family_from_id, mother_id,
                                   _get_edge_style(self, mother_rel_ship),
                                   portFrom=individual_from_id)
    # Stats (unique individuals)
    males = Set()
    females = Set()
    unknowns = Set()
    marriages = 0
    for family_id, family_id2 in family_nodes.items():
        marriages = marriages + (len(family_id2) - 1)
        for individual_id in family_id2:
            individual = self.db.find_person_from_id(individual_id)
            if individual.get_gender() == individual.male\
                   and individual_id not in males:
                males.add(individual_id)
            elif individual.get_gender() == individual.female\
                     and individual_id not in females:
                females.add(individual_id)
            elif individual.get_gender() == individual.unknown\
                     and individual_id not in unknowns:
                unknowns.add(individual_id)
    _write_stats(self.File, len(males), len(females), len(unknowns), marriages)

#------------------------------------------------------------------------
#
# _get_individual_data
#
#------------------------------------------------------------------------
def _get_individual_data (self, individual_id):
    """Returns a tuple of individual data"""
    # color
    color = ''
    individual = self.db.find_person_from_id(individual_id)
    if self.Colorize:
        gender = individual.get_gender()
        if gender == individual.male:
            color = 'dodgerblue4'
        elif gender == individual.female:
            color  = 'deeppink'
    # url
    url = ''
    if self.IncludeUrl:
        url = "%s.html" % individual_id

    return (color, url)

#------------------------------------------------------------------------
#
# _get_event_label
#
#------------------------------------------------------------------------
def _get_event_label (self, event_id):
    """Returns a formatted string of event data suitable for a label"""
    if self.IncludeDates and event_id:
        event = self.db.find_event_from_id(event_id)
        date_obj = event.get_date_object()
        if date_obj.get_year_valid():
            if self.JustYear:
                return "%i" % date_obj.get_year_valid()
            else:
                return date_obj.get_date()
        elif self.PlaceCause:
            place_id = event.get_place_id()
            if place_id:
                place = self.db.find_place_from_id(place_id)
                return place.get_title()
            else:
                return event.get_cause()
    return ''

#------------------------------------------------------------------------
#
# _get_individual_label
#
#------------------------------------------------------------------------
def _get_individual_label (self, individual_id, marriage_event_id=None, family_id=None):
    """Returns a formatted string of individual data suitable for a label

    Returned string always includes individual's name and optionally
    individual's birth and death dates, individual's marriage date,
    individual's and family's IDs.
    """
    # Get data ready
    individual = self.db.find_person_from_id(individual_id)
    name = individual.get_primary_name().get_name()
    if self.IncludeDates:
        birth = _get_event_label(self, individual.get_birth_id())
        death = _get_event_label(self, individual.get_death_id())
        if marriage_event_id:
            marriage = _get_event_label(self, marriage_event_id)
    # Id
    if self.IncludeId:
        if marriage_event_id:
            label = "%s (%s)\\n" % (family_id, individual_id)
        else:
            label = "%s\\n" % individual_id
    else:
        label = ""
    # Marriage date
    if self.IncludeDates and (marriage_event_id and marriage):
        label = label + "%s\\n" % marriage
    # Individual's name
    label = label + name
    # Birth and death
    if self.IncludeDates and (birth or death):
        label = label + "\\n%s - %s" % (birth, death)
    return label

#------------------------------------------------------------------------
#
# _get_edge_style
#
#------------------------------------------------------------------------
def _get_edge_style (self, father_rel_ship, mother_rel_ship="Birth"):
    """Returns a edge style that depends on the relationships with parents"""
    if self.AdoptionsDashed and \
           (father_rel_ship != "Birth" or mother_rel_ship != "Birth"):
        return "dashed"


#------------------------------------------------------------------------
#
# _get_family_id_label
#
#------------------------------------------------------------------------
def _get_family_id_label (self, family_id):
    """Returns a formatted string of family data suitable for a label"""

    fam = self.db.find_family_from_id(family_id)
    for event_id in fam.get_event_list():
        if event_id:
            event = self.db.find_event_from_id(event_id)
            if event.get_name() == "Marriage":
                marriage_event_id = event_id
                break
    else:
        marriage_event_id = None

    marriage = _get_event_label(self, marriage_event_id)
    if self.IncludeId:
        return "%s\\n%s" % (family_id, marriage)
    else:
        return marriage

#------------------------------------------------------------------------
#
# _get_family_id_record_label
#
#------------------------------------------------------------------------
def _get_family_id_record_label (self, record):
    """Returns a formatted string of a family record suitable for a label"""
    labels = []
    spouse_id = record[0]
    spouse = self.db.find_person_from_id(spouse_id)
    for individual_id in record:
        individual = self.db.find_person_from_id(individual_id)
        if spouse_id == individual_id:
            label = _get_individual_label(self, individual_id)
        else:
            marriage_event_id = None
            for individual_family_id in individual.get_family_id_list():
                if individual_family_id in spouse.get_family_id_list():
                    individual_family = self.db.find_family_from_id(individual_family_id)
                    for event_id in individual_family.get_event_list():
                        if event_id:
                            event = self.db.find_event_from_id(event_id)
                            if event.get_name() == "Marriage":
                                marriage_event_id = event_id
                                break

            label = _get_individual_label(self, individual_id, 
                        marriage_event_id,individual_family_id)
        label = string.replace(label, "|", r"\|")
        label = string.replace(label, "<", r"\<")
        label = string.replace(label, ">", r"\>")
        labels.append("<%s>%s" % (individual_id, label))
    return string.join(labels, "|")

#------------------------------------------------------------------------
#
# _write_node
#
#------------------------------------------------------------------------
def _write_node (file, node="node", label="", color="", url="", shape="",
               fontname=""):
    """Writes out an individual node"""
    file.write('%s [' % node)
    if label:
        if fontname == _TT_FONT:
            file.write('label="%s" ' % label.replace('"', r'\"'))
        else:
            file.write('label="%s" ' %
                   utf8_to_latin(label.replace('"', r'\"')))

    if color:
        file.write('color=%s ' % color)
    if url:
        file.write('URL="%s" ' % string.replace(url, '"', r'\"'))
    if shape:
        file.write('shape=%s ' % shape)
    if fontname:
        file.write('fontname="%s" ' % fontname)
    file.write('];\n')

#------------------------------------------------------------------------
#
# _write_edge
#
#------------------------------------------------------------------------
def _write_edge (file, nodeFrom="", nodeTo="", style="",
               arrowHead="", arrowTail="", portFrom="", portTo=""):
    """Writes out an edge"""
    if nodeFrom and nodeTo:
        if portFrom:
            frm = nodeFrom + ":" + portFrom
        else:
            frm = nodeFrom
        if portTo:
            to = nodeTo + ":" + portTo
        else:
            to = nodeTo
        file.write('%s -> %s [' % (frm, to))
    else:
        file.write('edge [')  # default edge
    if style:
        file.write('style=%s ' % style)
    if arrowHead:
        file.write('arrowhead=%s ' % arrowHead)
    if arrowTail:
        file.write('arrowtail=%s ' % arrowTail)
    file.write('];\n')

#------------------------------------------------------------------------
#
# _writeStats
#
#------------------------------------------------------------------------
def _write_stats (file, males, females, unknowns, marriages):
    file.write('\n/* Statistics\n')
    file.write(' *   individuals male    : % 4d\n' % males)
    file.write(' *               female  : % 4d\n' % females)
    file.write(' *               unknown : % 4d\n' % unknowns)
    file.write(' *               total   : % 4d\n' % (males+females+unknowns))
    file.write(' *   marriages           : % 4d\n' % marriages)
    file.write(' */\n')

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

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
from Plugins import register_report

register_report(
    report,
    _("Relationship Graph"),
    status=(_("Beta")),
    category=_("Graphical Reports"),
    description=get_description(),
    author_name="Donald N. Allingham",
    author_email="dallingham@users.sourceforge.net"
    )
