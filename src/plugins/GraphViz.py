#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
import Report
import ReportOptions
import GenericFilter
import const
from BaseDoc import PAPER_LANDSCAPE
from latin_utf8 import utf8_to_latin
from QuestionDialog import ErrorDialog

#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------
_PS_FONT = 'Helvetica'
_TT_FONT = 'FreeSans'

_formats = (
    ( _("Postscript"), "ps" ),
    ( _("Structured Vector Graphics (SVG)"), "svg" ),
    ( _("Compressed Structured Vector Graphics (SVG)"), "svgz" ),
    ( _("PNG image"), "png" ),
    ( _("JPEG image"), "jpg" ),
    ( _("GIF image"), "gif" ),
)

dot_found = os.system("dot -V 2>/dev/null") == 0

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
        
        filter  - Filter to be applied to the people of the database.
                  The option class carries its number, and the function
                  returning the list of filters.
        font    - Font to use.
        arrow   - Arrow styles for heads and tails.
        sfn     - Whether to show family nodes.
        incid   - Whether to include IDs.
        incda   - Whether to include dates.
        yearso  - Use years only.
        repb    -           THIS ONE IS NOT BACK FROM THE DEAD YET :-)
        url     - Whether to include URLs.
        color   - Whether to colorize the graph.
        dashedl - Whether to use dashed lines for non-birth relationships.
        margtb  - Top & bottom margins, in cm.
        marglr  - Left & right margins, in cm.
        pagesh  - Number of pages in horizontal direction.
        pagesv  - Number of pages in vertical direction.
        """
        self.database = database
        self.start_person = person
        self.options_class = options_class

        self.paper = self.options_class.handler.get_paper()
        self.orien = self.options_class.handler.get_orientation()

        self.width = self.paper.get_width_inches()
        self.height = self.paper.get_height_inches()
        self.hpages = self.options_class.handler.options_dict['pagesh']
        self.vpages = self.options_class.handler.options_dict['pagesv']
        self.lr_margin = self.options_class.handler.options_dict['marglr']
        self.tb_margin = self.options_class.handler.options_dict['margtb']
        self.includeid = self.options_class.handler.options_dict['incid']
        self.includedates = self.options_class.handler.options_dict['incda']
        self.includeurl = self.options_class.handler.options_dict['url']
        self.colorize = self.options_class.handler.options_dict['color']
        self.adoptionsdashed = self.options_class.handler.options_dict['dashedl']
        self.show_families = self.options_class.handler.options_dict['sfn']
        self.just_year = self.options_class.handler.options_dict['yearso']
        self.placecause = self.options_class.handler.options_dict['repb']
        self.font = self.options_class.handler.options_dict['font']
        if self.font == 'tt':
            self.fontname = _TT_FONT
        else:
            self.fontname = _PS_FONT
        arrow_str = self.options_class.handler.options_dict['arrow']
        if arrow_str.find('a') + 1:
        	self.arrowheadstyle = 'normal'
        else:
        	self.arrowheadstyle = 'none'
        if arrow_str.find('d') + 1:
        	self.arrowtailstyle = 'normal'
        else:
        	self.arrowtailstyle = 'none'

        filter_num = options_class.get_filter_number()
        filters = options_class.get_report_filters(person)
        filters.extend(GenericFilter.CustomFilters.get_filters())
        self.filter = filters[filter_num]

        self.f = open(options_class.get_output(),'w')
        self.write_report()
        self.f.close()

    def write_report(self):

        self.ind_list = self.filter.apply(self.database,
                    self.database.get_person_handles(sort_handles=False))
        
        self.write_header()
        self.f.write("digraph GRAMPS_relationship_graph {\n")
        self.f.write("bgcolor=white;\n")
        self.f.write("rankdir=LR;\n")
        self.f.write("center=1;\n")
        self.f.write("margin=0.5;\n")
        self.f.write("ratio=fill;\n")
        self.f.write("size=\"%3.1f,%3.1f\";\n" % (
                (self.width*self.hpages)-(self.lr_margin*2)
                        -((self.hpages-1)*1.0),
                (self.height*self.vpages)-(self.tb_margin*2)
                        -((self.vpages-1)*1.0))
        )
        self.f.write("page=\"%3.1f,%3.1f\";\n" % (self.width,self.height))

        if self.orien == PAPER_LANDSCAPE:
            self.f.write("rotate=90;\n")

        if len(self.ind_list) > 1:
            self.dump_index()
            self.dump_person()

        self.f.write("}\n")

    def dump_person(self):
        # Hash people in a dictionary for faster inclusion checking.
        person_dict = {}
    	for p_id in self.ind_list:
            person_dict[p_id] = 1

        for person_handle in self.ind_list:
            person = self.database.get_person_from_handle(person_handle)
            pid = person.get_gramps_id().replace('-','_')
            for family_handle, mrel, frel in person.get_parent_family_handle_list():
                family = self.database.get_family_from_handle(family_handle)
                father_handle = family.get_father_handle()
                mother_handle = family.get_mother_handle()
                fadopted  = frel != _("Birth")
                madopted  = mrel != _("Birth")
                famid = family.get_gramps_id().replace('-','_')
                if (self.show_families and
                    (father_handle and person_dict.has_key(father_handle) or
                     mother_handle and person_dict.has_key(mother_handle))):
                    # Link to the family node.
                    self.f.write('p%s -> f%s ['  % (pid, famid))
                    self.f.write('arrowhead=%s, arrowtail=%s, ' %
                           (self.arrowheadstyle, self.arrowtailstyle))
                    if self.adoptionsdashed and (fadopted or madopted):
                        self.f.write('style=dashed')
                    else:
                        self.f.write('style=solid')
                    self.f.write('];\n')
                else:
                    # Link to the parents' nodes directly.
                    if father_handle and person_dict.has_key(father_handle):
                        father = self.database.get_person_from_handle(father_handle)
                        fid = father.get_gramps_id().replace('-','_')
                        self.f.write('p%s -> p%s ['  % (pid, fid))
                        self.f.write('arrowhead=%s, arrowtail=%s, ' %
                                   (self.arrowheadstyle, self.arrowtailstyle))
                        if self.adoptionsdashed and fadopted:
                            self.f.write('style=dashed')
                        else:
                            self.f.write('style=solid')
                        self.f.write('];\n')
                    if mother_handle and person_dict.has_key(mother_handle):
                        mother = self.database.get_person_from_handle(mother_handle)
                        mid = mother.get_gramps_id().replace('-','_')
                        self.f.write('p%s -> p%s ['  % (pid, mid))
                        self.f.write('arrowhead=%s, arrowtail=%s, ' %
                                   (self.arrowheadstyle, self.arrowtailstyle))
                        if self.adoptionsdashed and madopted:
                            self.f.write('style=dashed')
                        else:
                            self.f.write('style=solid')
                        self.f.write('];\n')
    
    def dump_index(self):
        # The list of families for which we have output the node, so we
        # don't do it twice.
        families_done = []
        for person_handle in self.ind_list:
            person = self.database.get_person_from_handle(person_handle)
            # Output the person's node.
            label = person.get_primary_name().get_name()
            the_id = person.get_gramps_id().replace('-','_')
            if self.includeid:
                label = label + " (%s)" % the_id
            if self.includedates:
                birth_handle = person.get_birth_handle()
                if birth_handle:
                    birth_event = self.database.get_event_from_handle(birth_handle)
                    birth = self.dump_event(birth_event)
                else:
                    birth = ''
                death_handle = person.get_death_handle()
                if death_handle:
                    death_event = self.database.get_event_from_handle(death_handle)
                    death = self.dump_event(death_event)
                else:
                    death = ''
                label = label + '\\n(%s - %s)' % (birth, death)
            self.f.write('p%s [shape=box, ' % the_id)
            if self.includeurl:
                self.f.write('URL="%s.html", ' % the_id)
            if self.colorize:
                gender = person.get_gender()
                if gender == person.male:
                    self.f.write('color=dodgerblue4, ')
                elif gender == person.female:
                    self.f.write('color=deeppink, ')
                else:
                    self.f.write('color=black, ')
            if self.font == 'tt':
                self.f.write('fontname="%s", label="%s"];\n' % (self.fontname,label))
            else:
                self.f.write('fontname="%s", label="%s"];\n' % (self.fontname,utf8_to_latin(label)))
            # Output families's nodes.
            if self.show_families:
                family_list = person.get_family_handle_list()
                for fam_handle in family_list:
                    fam = self.database.get_family_from_handle(fam_handle)
                    fid = fam.get_gramps_id().replace('-','_')
                    if fam_handle not in families_done:
                        families_done.append(fam_handle)
                        self.f.write('f%s [shape=ellipse, ' % fid)
                        marriage = ""

                        for event_handle in fam.get_event_list():
                            if event_handle:
                                event = self.database.get_event_from_handle(event_handle)
                                if event.get_name() == "Marriage":
                                    m = event
                                    break
                        else:
                            m = None
    
                        if m:
                            marriage = self.dump_event(m)
                        if self.includeid:
                            marriage = marriage + " (%s)" % fid
                        self.f.write('fontname="%s", label="%s"];\n' 
                                    % (self.fontname,marriage))
                    # Link this person to all his/her families.
                    self.f.write('f%s -> p%s [' % (fid, the_id))
                    self.f.write('arrowhead=%s, arrowtail=%s, ' %
                               (self.arrowheadstyle, self.arrowtailstyle))
                    self.f.write('style=solid];\n')
    
    def dump_event(self,event):
        """
        Compile an event label.
        
        Based on the data availability and preferences, we select one
        of the following for a given event:
            year only
            complete date
            place name
            cause
            empty string
        """
        if event.get_date_object().get_year_valid():
            if self.just_year:
                return '%i' % event.get_date_object().get_year()
            else:
                return event.get_date()
        elif self.placecause:
            place_handle = event.get_place_handle()
            place = self.database.get_place_from_handle(place_handle)
            if place and place.get_title():
                return place.get_title()
            else:
                return event.get_cause()
        return ''

    def write_header(self):
        """
        Write header listing the options used.
        """
        self.f.write("/* GRAMPS - Relationship graph\n")
        self.f.write(" *\n")
        self.f.write(" * Report options:\n")
        self.f.write(" *   font style         : %s\n" % self.fontname)
        self.f.write(" *   style arrow head   : %s\n" % self.arrowheadstyle)
        self.f.write(" *               tail   : %s\n" % self.arrowtailstyle)
        self.f.write(" *   include URLs       : %s\n" % bool(self.includeurl))
        self.f.write(" *           IDs        : %s\n" % bool(self.includeid))
        self.f.write(" *           dates      : %s\n" % bool(self.includedates))
        self.f.write(" *   just year          : %s\n" % bool(self.just_year))
        self.f.write(" *   place or cause     : %s\n" % bool(self.placecause))
        self.f.write(" *   colorize           : %s\n" % bool(self.colorize))
        self.f.write(" *   dashed adoptions   : %s\n" % bool(self.adoptionsdashed))
        self.f.write(" *   show family nodes  : %s\n" % bool(self.show_families))
#        self.f.write(" *        as stack      : %s\n" % self.ShowAsStack)
        self.f.write(" *   margins top/bottm  : %s\n" % self.tb_margin)
        self.f.write(" *           left/right : %s\n" % self.lr_margin)
        self.f.write(" *   pages horizontal   : %s\n" % self.hpages)
        self.f.write(" *         vertical     : %s\n" % self.vpages)
        self.f.write(" *   page width         : %sin\n" % self.width)
        self.f.write(" *        height        : %sin\n" % self.height)
        self.f.write(" *\n")
        self.f.write(" * Generated on %s by GRAMPS\n" % asctime())
        self.f.write(" */\n\n")

#------------------------------------------------------------------------
#
# Options class 
#
#------------------------------------------------------------------------
class GraphVizOptions(ReportOptions.ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.ReportOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'font'      : 'tt',
            'arrow'     : 'd',
            'sfn'       : 0,
            'incid'     : 1,
            'incda'     : 1,
            'yearso'    : 0,
            'repb'      : 1,
            'url'       : 1,
            'color'     : 1,
            'dashedl'   : 1,
            'margtb'    : 0.5,
            'marglr'    : 0.5,
            'pagesh'    : 1,
            'pagesv'    : 1,
            'gvof'      : 'png',
        }

        self.options_help = {
            'font'      : ("=str","Font to use in the report.",
                            ["tt\tTrueType","ps\tPostscript"],
                            False),
            'arrow'     : ("=str","Arrow styles for heads and tails.",
                            [
                            'd \tDescendants <- Ancestors',
                            'a \tDescendants -> Ancestors',
                            'da\tDescendants <-> Ancestors',
                            '""\tDescendants - Ancestors'],
                            False),
            'sfn'       : ("=0/1","Whether to show family nodes.",
                            ["Do not show family nodes","Show family nodes"],
                            True),
            'incid'     : ("=0/1","Whether to include dates.",
                            ["Do not include dates","Include dates"],
                            True),
            'incda'     : ("=0/1","Whether to include IDs.",
                            ["Do not include IDs","Include IDs"],
                            True),
            'yearso'    : ("=0/1","Whether to use years only.",
                            ["Do not use years only","Use years only"],
                            True),
            'repb'      : ("=0/1","Whether to replace missing dates with place/cause.",
                            ["Do not replace blank dates","Replace blank dates"],
                            True),
            'url'       : ("=0/1","Whether to include URLs.",
                            ["Do not include URLs","Include URLs"],
                            True),
            'color'     : ("=0/1","Whether to colorize graph.",
                            ["Do not colorize graph","Colorize graph"],
                            True),
            'dashedl'   : ("=0/1","Whether to use dashed lines for non-birth relationships.",
                            ["Do not use dashed lines","Use dashed lines"],
                            True),
            'margtb'    : ("=num","Top & bottom margins.",
                            "Floating point values, in cm"),
            'marglr'    : ("=num","Left & right margins.",
                            "Floating point values, in cm"),
            'pagesh'    : ("=num","Number of pages in horizontal direction.",
                            "Integer values"),
            'pagesv'    : ("=num","Number of pages in vertical direction.",
                            "Integer values"),
            'gvof'      : ("=str","Output format to convert dot file into.",
                            [ "%s\t%s" % (item[1],item[0]) for item in _formats ],
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
            handle = person.get_handle()
        else:
            name = 'PERSON'
            handle = ''

        all = GenericFilter.GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(GenericFilter.Everyone([]))

        des = GenericFilter.GenericFilter()
        des.set_name(_("Descendants of %s") % name)
        des.add_rule(GenericFilter.IsDescendantOf([handle,1]))

        ans = GenericFilter.GenericFilter()
        ans.set_name(_("Ancestors of %s") % name)
        ans.add_rule(GenericFilter.IsAncestorOf([handle,1]))

        com = GenericFilter.GenericFilter()
        com.set_name(_("People with common ancestor with %s") % name)
        com.add_rule(GenericFilter.HasCommonAncestorWith([handle]))

        return [all,des,ans,com]

    def make_doc_menu(self,dialog,active=None): pass

    def add_user_options(self,dialog):
        if self.handler.report_name == "rel_graph2":
            dialog.make_doc_menu = self.make_doc_menu
            dialog.format_menu = GraphicsFormatComboBox()
            dialog.format_menu.set(self.options_dict['gvof'])

        self.arrowstyles = (
            (_("Descendants <- Ancestors"),     'd'),
            (_("Descendants -> Ancestors"),     'a'),
            (_("Descendants <-> Ancestors"),    'da'),
            (_("Descendants - Ancestors"),      ''),
        )
        self.arrowstyle_box = gtk.ComboBox()
        store = gtk.ListStore(str)
        self.arrowstyle_box.set_model(store)
        cell = gtk.CellRendererText()
        self.arrowstyle_box.pack_start(cell,True)
        self.arrowstyle_box.add_attribute(cell,'text',0)
        index = 0
        active_index = 0
        for item in self.arrowstyles:
            store.append(row=[item[0]])
            if item[1] == self.options_dict['arrow']:
                active_index = index
            index = index + 1
        self.arrowstyle_box.set_active(active_index)

        dialog.add_frame_option(_("GraphViz Options"),
                              _("Arrowhead Options"),
                              self.arrowstyle_box,
                              _("Choose the direction that the arrows point."))
        

        self.font_options = (
            (_("TrueType"),'tt'),
            (_("PostScript"),'ps'),
        )
        self.font_box = gtk.ComboBox()
        store = gtk.ListStore(str)
        self.font_box.set_model(store)
        cell = gtk.CellRendererText()
        self.font_box.pack_start(cell,True)
        self.font_box.add_attribute(cell,'text',0)
        index = 0
        active_index = 0
        for item in self.font_options:
            store.append(row=[item[0]])
            if item[1] == self.options_dict['font']:
                active_index = index
            index = index + 1
        self.font_box.set_active(active_index)

        dialog.add_frame_option(_("GraphViz Options"),
                              _("Font Options"),
                              self.font_box,
                              _("Choose the font family."))

        msg = _("Include Birth, Marriage and Death Dates")
        self.includedates_cb = gtk.CheckButton(msg)
        self.includedates_cb.set_active(self.options_dict['incda'])
        dialog.add_frame_option(_("GraphViz Options"), '',
                              self.includedates_cb,
                              _("Include the dates that the individual "
                                "was born, got married and/or died "
                                "in the graph labels."))

        self.just_year_cb = gtk.CheckButton(_("Limit dates to years only"))
        self.just_year_cb.set_active(self.options_dict['yearso'])
        dialog.add_frame_option(_("GraphViz Options"), '',
                              self.just_year_cb,
                              _("Prints just dates' year, neither "
                                "month or day nor date approximation "
                                "or interval are shown."))

        self.includedates_cb.connect('toggled',self.toggle_date)

        self.place_cause_cb = gtk.CheckButton(_("Place/cause when no date"))
        self.place_cause_cb.set_active(self.options_dict['repb'])
        dialog.add_frame_option(_("GraphViz Options"), '',
                              self.place_cause_cb,
                              _("When no birth, marriage, or death date "
                                "is available, the correspondent place field "
                                "(or cause field when blank place) will be used."))

        self.includeurl_cb = gtk.CheckButton(_("Include URLs"))
        self.includeurl_cb.set_active(self.options_dict['url'])
        dialog.add_frame_option(_("GraphViz Options"), '',
                              self.includeurl_cb,
                              _("Include a URL in each graph node so "
                                "that PDF and imagemap files can be "
                                "generated that contain active links "
                                "to the files generated by the 'Generate "
                                "Web Site' report."))

        self.colorize_cb = gtk.CheckButton(_("Colorize Graph"))
        self.colorize_cb.set_active(self.options_dict['color'])
        dialog.add_frame_option(_("GraphViz Options"), '',
                              self.colorize_cb,
                              _("Males will be outlined in blue, females "
                                "will be outlined in pink.  If the sex of "
                                "an individual is unknown it will be "
                                "outlined in black."))

        self.adoptionsdashed_cb = gtk.CheckButton(_("Indicate non-birth relationships with dashed lines"))
        self.adoptionsdashed_cb.set_active(self.options_dict['dashedl'])
        dialog.add_frame_option(_("GraphViz Options"), '',
                              self.adoptionsdashed_cb,
                              _("Non-birth relationships will show up "
                                "as dashed lines in the graph."))

        self.show_families_cb = gtk.CheckButton(_("Show family nodes"))
        self.show_families_cb.set_active(self.options_dict['sfn'])
        dialog.add_frame_option(_("GraphViz Options"), '',
                              self.show_families_cb,
                              _("Families will show up as ellipses, linked "
                                "to parents and children."))

        self.includeid_cb = gtk.CheckButton(_("Include IDs"))
        self.includeid_cb.set_active(self.options_dict['incid'])
        dialog.add_frame_option(_("GraphViz Options"), '',
                              self.includeid_cb,
                              _("Include individual and family IDs."))

        tb_margin_adj = gtk.Adjustment(value=self.options_dict['margtb'],
                        lower=0.25, upper=100.0, step_incr=0.25)
        lr_margin_adj = gtk.Adjustment(value=self.options_dict['marglr'],
                        lower=0.25, upper=100.0, step_incr=0.25)

        self.tb_margin_sb = gtk.SpinButton(adjustment=tb_margin_adj, digits=2)
        self.lr_margin_sb = gtk.SpinButton(adjustment=lr_margin_adj, digits=2)

        dialog.add_frame_option(_("Page Options"),
                              _("Top & Bottom Margins"),
                              self.tb_margin_sb)
        dialog.add_frame_option(_("Page Options"),
                              _("Left & Right Margins"),
                              self.lr_margin_sb)

        hpages_adj = gtk.Adjustment(value=self.options_dict['pagesh'],
                    lower=1, upper=25, step_incr=1)
        vpages_adj = gtk.Adjustment(value=self.options_dict['pagesv'],
                    lower=1, upper=25, step_incr=1)

        self.hpages_sb = gtk.SpinButton(adjustment=hpages_adj, digits=0)
        self.vpages_sb = gtk.SpinButton(adjustment=vpages_adj, digits=0)

        dialog.add_frame_option(_("Page Options"),
                              _("Number of Horizontal Pages"),
                              self.hpages_sb,
                              _("GraphViz can create very large graphs by "
                                "spreading the graph across a rectangular "
                                "array of pages. This controls the number "
                                "pages in the array horizontally."))
        dialog.add_frame_option(_("Page Options"),
                              _("Number of Vertical Pages"),
                              self.vpages_sb,
                              _("GraphViz can create very large graphs "
                                "by spreading the graph across a "
                                "rectangular array of pages. This "
                                "controls the number pages in the array "
                                "vertically."))

    def toggle_date(self,obj):
        self.just_year_cb.set_sensitive(self.includedates_cb.get_active())
        self.place_cause_cb.set_sensitive(self.includedates_cb.get_active())

    def parse_user_options(self,dialog):
        self.options_dict['arrow'] = \
                self.arrowstyles[self.arrowstyle_box.get_active()][1]
        self.options_dict['incda'] = int(self.includedates_cb.get_active())
        self.options_dict['url'] = int(self.includeurl_cb.get_active())
        self.options_dict['margtb'] = self.tb_margin_sb.get_value()
        self.options_dict['marglr'] = self.lr_margin_sb.get_value()
        self.options_dict['color'] = int(self.colorize_cb.get_active())
        self.options_dict['dashedl'] = int(self.adoptionsdashed_cb.get_active())
        self.options_dict['pagesh'] = self.hpages_sb.get_value_as_int()
        self.options_dict['pagesv'] = self.hpages_sb.get_value_as_int()
        self.options_dict['sfn'] = int(self.show_families_cb.get_active())
        self.options_dict['incid'] = int(self.includeid_cb.get_active())
        self.options_dict['repb'] = int(self.place_cause_cb.get_active())
        self.options_dict['font'] = \
                self.font_options[self.font_box.get_active()][1]
        if self.handler.report_name == "rel_graph2":
            self.options_dict['gvof'] = dialog.format_menu.get_format_str()

#------------------------------------------------------------------------
#
# Dialog class
#
#------------------------------------------------------------------------
class GraphVizDialog(Report.ReportDialog):

    def __init__(self,database,person):
        self.database = database 
        self.person = person
        name = "rel_graph"
        translated_name = _("Relationship Graph")
        self.options_class = GraphVizOptions(name)
        self.category = const.CATEGORY_CODE
        Report.ReportDialog.__init__(self,database,person,self.options_class,
                                    name,translated_name)

        response = self.window.run()
        if response == True:
            try:
                self.make_report()
            except (IOError,OSError),msg:
                ErrorDialog(str(msg))
        self.window.destroy()

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
        return None

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
        for item in _formats:
            self.store.append(row=[item[0]])
            if active == item[1]:
                active_index = index
            index = index + 1
        self.set_active(active_index)

    def get_label(self):
        return _formats[self.get_active()][0]

    def get_reference(self):
        return EmptyDoc

    def get_paper(self):
        return 1

    def get_styles(self):
        return 0

    def get_ext(self):
        return '.%s' % _formats[self.get_active()][1]

    def get_format_str(self):
        return _formats[self.get_active()][1]

    def get_printable(self):
        return None

    def get_clname(self):
        return 'print'

#------------------------------------------------------------------------
#
# Empty class to keep the BaseDoc-targeted format happy
#
#------------------------------------------------------------------------
class EmptyDoc:
    def __init__(self,styles,type,template,orientation,source=None):
        pass

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def cl_report(database,name,category,options_str_dict):

    clr = Report.CommandLineReport(database,name,category,GraphVizOptions,options_str_dict)

    # Exit here if show option was given
    if clr.show:
        return

    try:
        GraphViz(database,clr.person,clr.option_class)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class GraphVizGraphics(Report.Report):
    def __init__(self,database,person,options_class):
        self.database = database
        self.start_person = person
        self.options_class = options_class

        self.user_output = options_class.get_output()
        self.junk_output = os.path.expanduser("~/.gramps/junk")
        self.the_format = self.options_class.handler.options_dict['gvof']
        self.the_font = self.options_class.handler.options_dict['font']

    def begin_report(self):
        self.options_class.set_output(self.junk_output)

    def write_report(self):
        GraphViz(self.database,self.start_person,self.options_class)

    def end_report(self):
        os.system('dot -T%s -o%s %s ; rm %s' %
                    (self.the_format,self.user_output,
                    self.junk_output,self.junk_output))

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
from PluginMgr import register_report
register_report(
    name = 'rel_graph',
    category = const.CATEGORY_CODE,
    report_class = GraphVizDialog,
    options_class = cl_report,
    modes = Report.MODE_GUI | Report.MODE_CLI,
    translated_name = _("Relationship Graph"),
    status = _("Beta"),
    description= get_description(),
    author_name="Donald N. Allingham",
    author_email="dallingham@users.sourceforge.net"
    )

if dot_found:
    register_report(
        name = 'rel_graph2',
        category = const.CATEGORY_DRAW,
        report_class = GraphVizGraphics,
        options_class = GraphVizOptions,
        modes = Report.MODE_GUI | Report.MODE_CLI,
        translated_name = _("Relationship Graph"),
        status = _("Beta"),
        description= get_description_graphics(),
        author_name="Donald N. Allingham",
        author_email="dallingham@users.sourceforge.net"
    )
