#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
# GraphVizDialog
#
#------------------------------------------------------------------------
class GraphVizDialog(Report.ReportDialog):

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
        des.add_rule(GenericFilter.IsDescendantOf([self.person.get_id(),1]))

        ans = GenericFilter.GenericFilter()
        ans.set_name(_("Ancestors of %s") % name)
        ans.add_rule(GenericFilter.IsAncestorOf([self.person.get_id(),1]))

        com = GenericFilter.GenericFilter()
        com.set_name(_("People with common ancestor with %s") % name)
        com.add_rule(GenericFilter.HasCommonAncestorWith([self.person.get_id()]))

        return [all,des,ans,com]

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
        
        msg = _("Include Birth, Marriage and Death Dates")
        self.includedates_cb = gtk.CheckButton(msg)
        self.includedates_cb.set_active(1)
        self.add_frame_option(_("GraphViz Options"), '',
                              self.includedates_cb,
                              _("Include the dates that the individual "
                                "was born, got married and/or died "
                                "in the graph labels."))

        self.just_year_cb = gtk.CheckButton(_("Limit dates to years only"))
        self.just_year_cb.set_active(0)
        self.add_frame_option(_("GraphViz Options"), '',
                              self.just_year_cb,
                              _("Prints just dates' year, neither "
                                "month or day nor date approximation "
                                "or interval are shown."))

        self.includedates_cb.connect('toggled',self.toggle_date)

        self.includeurl_cb = gtk.CheckButton(_("Include URLs"))
        self.includeurl_cb.set_active(1)
        self.add_frame_option(_("GraphViz Options"), '',
                              self.includeurl_cb,
                              _("Include a URL in each graph node so "
                                "that PDF and imagemap files can be "
                                "generated that contain active links "
                                "to the files generated by the 'Generate "
                                "Web Site' report."))

        self.colorize_cb = gtk.CheckButton(_("Colorize Graph"))
        self.colorize_cb.set_active(1)
        self.add_frame_option(_("GraphViz Options"),
                              '',
                              self.colorize_cb,
                              _("Males will be outlined in blue, females "
                                "will be outlined in pink.  If the sex of "
                                "an individual is unknown it will be "
                                "outlined in black."))

        self.adoptionsdashed_cb = gtk.CheckButton(_("Indicate non-birth relationships with dashed lines"))
        self.adoptionsdashed_cb.set_active(1)
        self.add_frame_option(_("GraphViz Options"),
                              '',
                              self.adoptionsdashed_cb,
                              _("Non-birth relationships will show up "
                                "as dashed lines in the graph."))

        self.show_families_cb = gtk.CheckButton(_("Show family nodes"))
        self.show_families_cb.set_active(0)
        self.add_frame_option(_("GraphViz Options"),
                              '',
                              self.show_families_cb,
                              _("Families will show up as ellipses, linked "
                                "to parents and children."))

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

    def toggle_date(self,obj):
        if self.includedates_cb.get_active():
            self.just_year_cb.set_sensitive(1)
        else:
            self.just_year_cb.set_sensitive(0)

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
        menu = self.arrowstyle_optionmenu.get_menu()
        self.arrowheadstyle, self.arrowtailstyle = menu.get_active().get_data('t')
        self.includedates = self.includedates_cb.get_active()
        self.includeurl = self.includeurl_cb.get_active()
        self.tb_margin = self.tb_margin_sb.get_value()
        self.lr_margin = self.lr_margin_sb.get_value()
        self.colorize = self.colorize_cb.get_active()
        self.adoptionsdashed = self.adoptionsdashed_cb.get_active()
        self.hpages = self.hpages_sb.get_value_as_int()
        self.vpages = self.vpages_sb.get_value_as_int()
        self.show_families = self.show_families_cb.get_active()
        self.just_year = self.just_year_cb.get_active()

        menu = self.font_optionmenu.get_menu()
        self.fontstyle = menu.get_active().get_data('t')

    def make_report(self):
        """Create the object that will produce the GraphViz file."""
        width = self.paper.get_width_inches()
        height = self.paper.get_height_inches()

        file = open(self.target_path,"w")

        try:
            ind_list = self.filter.apply(self.db, self.db.get_person_keys())
        except Errors.FilterError, msg:
            from QuestionDialog import ErrorDialog
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)

        write_dot(self.db, file, ind_list, self.orien, width, height,
                  self.tb_margin, self.lr_margin, self.hpages,
                  self.vpages, self.includedates, self.includeurl,
                  self.colorize, self.adoptionsdashed, self.arrowheadstyle,
                  self.arrowtailstyle, self.show_families, self.just_year,
                  self.fontstyle)

        if self.print_report.get_active ():
            os.environ["DOT"] = self.target_path
            os.system ('dot -Tps "$DOT" | %s &' %
                       Report.get_print_dialog_app ())

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
def report(database,person):
    GraphVizDialog(database,person)

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
def write_dot(database, file, ind_list, orien, width, height, tb_margin,
              lr_margin, hpages, vpages, includedates, includeurl,
              colorize, adoptionsdashed, arrowheadstyle, arrowtailstyle,
              show_families, just_year, fontstyle):
    file.write("digraph g {\n")
    file.write("bgcolor=white;\n")
    file.write("rankdir=LR;\n")
    file.write("center=1;\n")
    file.write("margin=0.5;\n")
    file.write("ratio=fill;\n")
    file.write("size=\"%3.1f,%3.1f\";\n" % ((width*hpages)-(lr_margin*2)-((hpages-1)*1.0),
                                            (height*vpages)-(tb_margin*2)-((vpages-1)*1.0)))
    file.write("page=\"%3.1f,%3.1f\";\n" % (width,height))

    if orien == BaseDoc.PAPER_LANDSCAPE:
        file.write("rotate=90;\n")

    if len(ind_list) > 1:
        dump_index(database,ind_list,file,includedates,includeurl,colorize,
                   arrowheadstyle,arrowtailstyle,show_families,just_year,fontstyle)
        dump_person(database,ind_list,file,adoptionsdashed,arrowheadstyle,
                    arrowtailstyle,show_families)

    file.write("}\n")
    file.close()

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
def dump_person(database,person_list,file,adoptionsdashed,arrowheadstyle,
                arrowtailstyle,show_families):
    # Hash people in a dictionary for faster inclusion checking.
    person_dict = {}
    for p_id in person_list:
        person_dict[p_id] = 1

    for person_id in person_list:
        pid = string.replace(person_id,'-','_')
        person = database.try_to_find_person_from_id(person_id)
        for family_id, mrel, frel in person.get_parent_family_id_list():
            family = database.find_family_from_id(family_id)
            father_id = family.get_father_id()
            mother_id = family.get_mother_id()
            fadopted  = frel != _("Birth")
            madopted  = mrel != _("Birth")
            if (show_families and
                (father_id and person_dict.has_key(father_id) or
                 mother_id and person_dict.has_key(mother_id))):
                # Link to the family node.
                famid = string.replace(family_id,'-','_')
                file.write('p%s -> f%s ['  % (pid, famid))
                file.write('arrowhead=%s, arrowtail=%s, ' %
                           (arrowheadstyle, arrowtailstyle))
                if adoptionsdashed and (fadopted or madopted):
                    file.write('style=dashed')
                else:
                    file.write('style=solid')
                file.write('];\n')
            else:
                # Link to the parents' nodes directly.
                if father_id and person_dict.has_key(father_id):
                    fid = string.replace(father_id,'-','_')
                    file.write('p%s -> p%s ['  % (pid, fid))
                    file.write('arrowhead=%s, arrowtail=%s, ' %
                               (arrowheadstyle, arrowtailstyle))
                    if adoptionsdashed and fadopted:
                        file.write('style=dashed')
                    else:
                        file.write('style=solid')
                    file.write('];\n')
                if mother_id and person_dict.has_key(mother_id):
                    mid = string.replace(mother_id,'-','_')
                    file.write('p%s -> p%s ['  % (pid, mid))
                    file.write('arrowhead=%s, arrowtail=%s, ' %
                               (arrowheadstyle, arrowtailstyle))
                    if adoptionsdashed and madopted:
                        file.write('style=dashed')
                    else:
                        file.write('style=solid')
                    file.write('];\n')

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
def dump_index(database,person_list,file,includedates,includeurl,colorize,
               arrowheadstyle,arrowtailstyle,show_families,just_year,font):
    # The list of families for which we have output the node, so we
    # don't do it twice.
    families_done = []
    for person_id in person_list:
        person = database.try_to_find_person_from_id(person_id)
        # Output the person's node.
        label = person.get_primary_name().get_name()
        id = string.replace(person_id,'-','_')
        if includedates:
            birth_id = person.get_birth_id()
            if birth_id:
                birth_event = database.find_event_from_id(birth_id)
                if birth_event.get_date_object().get_year_valid():
                    if just_year:
                        birth = '%i' % birth_event.get_date_object().get_year()
                    else:
                        birth = birth_event.get_date()
            else:
                birth = ''
            death_id = person.get_death_id()
            if death_id:
                death_event = database.find_event_from_id(death_id)
                if death_event.get_date_object().get_year_valid():
                    if just_year:
                        death = '%i' % death_event.get_date_object().get_year()
                    else:
                        death = death_event.get_date()
            else:
                death = ''
            label = label + '\\n(%s - %s)' % (birth, death)
        file.write('p%s [shape=box, ' % id)
        if includeurl:
            file.write('URL="%s.html", ' % id)
        if colorize:
            gender = person.get_gender()
            if gender == person.male:
                file.write('color=dodgerblue4, ')
            elif gender == person.female:
                file.write('color=deeppink, ')
            else:
                file.write('color=black, ')
        if font == _TT_FONT:
            file.write('fontname="%s", label="%s"];\n' % (font,label))
        else:
            file.write('fontname="%s", label="%s"];\n' % (font,utf8_to_latin(label)))
        # Output families's nodes.
        if show_families:
            family_list = person.get_family_id_list()
            for fam_id in family_list:
                fid = string.replace(fam_id,'-','_')
                if fam_id not in families_done:
                    families_done.append(fam_id)
                    file.write('f%s [shape=ellipse, ' % fid)
                    marriage = ""
                    fam = database.find_family_from_id(fam_id)

                    for event_id in fam.get_event_list():
                        if event_id:
                            event = database.find_event_from_id(event_id)
                            if event.get_name() == "Marriage":
                                m = event
                                break
                    else:
                        m = None

                    if m:
                        do = m.get_date_object()
                        if do:
                            if do.get_year_valid():
                                if just_year:
                                    marriage = '%i' % do.get_year()
                                else:
                                    marriage = m.get_date()
                    file.write('fontname="%s", label="%s"];\n' % (font,marriage))
                # Link this person to all his/her families.
                file.write('f%s -> p%s [' % (fid, id))
                file.write('arrowhead=%s, arrowtail=%s, ' %
                           (arrowheadstyle, arrowtailstyle))
                file.write('style=solid];\n')

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
import sys

ver = sys.version_info
if ver[0] == 2 and ver[1] == 2:
    register_report(
        report,
        _("Relationship Graph"),
        status=(_("Beta")),
        category=_("Graphical Reports"),
        description=get_description(),
        author_name="Donald N. Allingham",
        author_email="dallingham@users.sourceforge.net"
        )

