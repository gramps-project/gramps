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
from TransUtils import sgettext as _
from time import asctime

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
from PluginUtils import Report, ReportOptions, register_report
import GenericFilter
import RelLib
import DateHandler
from BaseDoc import PAPER_LANDSCAPE
from QuestionDialog import ErrorDialog

#------------------------------------------------------------------------
#
# Constant options items
#
#------------------------------------------------------------------------

class _options:
    # internal ID, english option name (for cli), localized option name (for gui)
    formats = (
        ("ps", "Postscript", _("Postscript")),
        ("svg", "Structured Vector Graphics (SVG)", _("Structured Vector Graphics (SVG)")),
        ("svgz", "Compressed Structured Vector Graphics (SVG)", _("Compressed Structured Vector Graphics (SVG)")),
        ("png", "PNG image", _("PNG image")),
        ("jpg", "JPEG image", _("JPEG image")),
        ("gif", "GIF image", _("GIF image")),
    )
    fonts = (
        # Last items tells whether strings need to be converted to Latin1
        ("", "Default", _("Default"), 1),
        ("Helvetica", "Postscript / Helvetica", _("Postscript / Helvetica"), 1),
        ("FreeSans", "Truetype / FreeSans", _("Truetype / FreeSans"), 0),
    )
    colors = (
        ("outline", "B&W Outline", _("B&W outline")),
        ("colored", "Colored outline", _("Colored outline")),
        ("filled", "Color fill", _("Color fill")),
    )
    rankdir = (
        ("LR", "Horizontal", _("Horizontal")),
        ("RL", "Vertical", _("Vertical")),
    )
    arrowstyles = (
        ('d', "Descendants <- Ancestors",  _("Descendants <- Ancestors")),
        ('a', "Descendants -> Ancestors",  _("Descendants -> Ancestors")),
        ('da',"Descendants <-> Ancestors", _("Descendants <-> Ancestors")),
        ('',  "Descendants - Ancestors",    _("Descendants - Ancestors")),
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
        
        filter     - Filter to be applied to the people of the database.
                     The option class carries its number, and the function
                     returning the list of filters.
        font       - Font to use.
        latin      - Set if font supports only Latin1
        arrow      - Arrow styles for heads and tails.
        showfamily - Whether to show family nodes.
        incid      - Whether to include IDs.
        incdate    - Whether to include dates.
        justyears  - Use years only.
        placecause - Whether to replace missing dates with place or cause
        url        - Whether to include URLs.
        rankdir    - Graph direction
        color      - Whether to use outline, colored outline or filled color in graph
        dashedl    - Whether to use dashed lines for non-birth relationships.
        margin     - Margins, in cm.
        pagesh     - Number of pages in horizontal direction.
        pagesv     - Number of pages in vertical direction.
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
        self.hpages = options['pagesh']
        self.vpages = options['pagesv']
        margin_cm = options['margin']
        self.margin = round(margin_cm/2.54,2)
        if margin_cm > 0.1:
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
        self.fontname = options['font']
        self.latin = options['latin']
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
        self.f.write("rankdir=%s;\n" % self.rankdir)
        self.f.write("center=1;\n")
        self.f.write("margin=%3.2f;\n" % self.margin_small)
        self.f.write("ratio=fill;\n")
        if self.orient == PAPER_LANDSCAPE:
            self.f.write("size=\"%3.2f,%3.2f\";\n" % (
                (self.height-self.margin*2)*self.hpages,
                (self.width-self.margin*2)*self.vpages
                ))
        else:
            self.f.write("size=\"%3.2f,%3.2f\";\n" % (
                (self.width-self.margin*2)*self.hpages,
                (self.height-self.margin*2)*self.vpages
                ))
        self.f.write("page=\"%3.2f,%3.2f\";\n" % (self.width,self.height))

        if self.orient == PAPER_LANDSCAPE:
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
                fadopted  = frel != RelLib.Person.CHILD_REL_BIRTH
                madopted  = mrel != RelLib.Person.CHILD_REL_BIRTH
                famid = family.get_gramps_id().replace('-','_')
                if (self.show_families and
                    (father_handle and person_dict.has_key(father_handle) or
                     mother_handle and person_dict.has_key(mother_handle))):
                    # Link to the family node.
                    self.f.write('p%s -> f%s ['  % (pid, famid))
                    self.f.write('arrowhead=%s, arrowtail=%s, ' %
                           (self.arrowheadstyle, self.arrowtailstyle))
                    if self.adoptionsdashed and (fadopted or madopted):
                        self.f.write('style=dotted')
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
                            self.f.write('style=dotted')
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
                            self.f.write('style=dotted')
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
                h = person.get_handle()
                self.f.write('URL="ppl/%s/%s/%s.html", ' % (h[0],h[1],h))
            if self.colorize != 'outline':
                if self.colorize == 'filled':
                    style = 'style=filled, fillcolor'
                else:
                    style = 'color'
                gender = person.get_gender()
                if gender == person.MALE:
                    self.f.write('%s=%s, ' % (style, self.colors['male']))
                elif gender == person.FEMALE:
                    self.f.write('%s=%s, ' % (style, self.colors['female']))
                else:
                    self.f.write('%s=%s, ' % (style, self.colors['unknown']))
            if self.latin:
                label = label.encode('iso-8859-1')
            self.f.write('fontname="%s", label="%s"];\n' % (self.fontname,label))

            # Output families's nodes.
            if self.show_families:
                family_list = person.get_family_handle_list()
                for fam_handle in family_list:
                    fam = self.database.get_family_from_handle(fam_handle)
                    fid = fam.get_gramps_id().replace('-','_')
                    if fam_handle not in families_done:
                        families_done.append(fam_handle)
                        self.f.write('f%s [shape=ellipse, ' % fid)
                        if self.colorize == 'colored':
                            self.f.write('color=%s, ' % self.colors['family'])
                        elif self.colorize == 'filled':
                            self.f.write('style=filled fillcolor=%s, ' % self.colors['family'])

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
        self.f.write(" *   graph direction    : %s\n" % self.rankdir)
        self.f.write(" *   include URLs       : %s\n" % bool(self.includeurl))
        self.f.write(" *           IDs        : %s\n" % bool(self.includeid))
        self.f.write(" *           dates      : %s\n" % bool(self.includedates))
        self.f.write(" *   just year          : %s\n" % bool(self.just_years))
        self.f.write(" *   place or cause     : %s\n" % bool(self.placecause))
        self.f.write(" *   colorize           : %s\n" % bool(self.colorize))
        self.f.write(" *   dotted adoptions   : %s\n" % bool(self.adoptionsdashed))
        self.f.write(" *   show family nodes  : %s\n" % bool(self.show_families))
        self.f.write(" *   margin             : %3.2fin\n" % self.margin_small)
        self.f.write(" *   pages horizontal   : %s\n" % self.hpages)
        self.f.write(" *         vertical     : %s\n" % self.vpages)
        self.f.write(" *   page width         : %3.2fin\n" % self.width)
        self.f.write(" *        height        : %3.2fin\n" % self.height)
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
            'font'       : "",
            'latin'      : 1,
            'arrow'      : 'd',
            'showfamily' : 1,
            'incdate'    : 1,
            'incid'      : 0,
            'justyears'  : 0,
            'placecause' : 1,
            'url'        : 1,
            'rankdir'    : "LR",
            'color'      : "filled",
            'dashedl'    : 1,
            'margin'     : 1.0,
            'pagesh'     : 1,
            'pagesv'     : 1,
            'gvof'       : 'ps',
        }

        self.options_help = {
            'font'      : ("=str","Font to use in the report.",
                            [ "%s\t%s" % (item[0],item[1]) for item in _options.fonts ],
                            False),
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
            'rankdir'      : ("=str","Graph direction.",
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
            'pagesh'    : ("=num","Number of pages in horizontal direction.",
                            "Integer values"),
            'pagesv'    : ("=num","Number of pages in vertical direction.",
                            "Integer values"),
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

        all = GenericFilter.GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(GenericFilter.Everyone([]))

        des = GenericFilter.GenericFilter()
        des.set_name(_("Descendants of %s") % name)
        des.add_rule(GenericFilter.IsDescendantOf([gramps_id,1]))

        ans = GenericFilter.GenericFilter()
        ans.set_name(_("Ancestors of %s") % name)
        ans.add_rule(GenericFilter.IsAncestorOf([gramps_id,1]))

        com = GenericFilter.GenericFilter()
        com.set_name(_("People with common ancestor with %s") % name)
        com.add_rule(GenericFilter.HasCommonAncestorWith([gramps_id]))

        return [all,des,ans,com]

    def make_doc_menu(self,dialog,active=None):
        pass

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
        self.rank_box = gtk.ComboBox()
        store = gtk.ListStore(str)
        self.rank_box.set_model(store)
        cell = gtk.CellRendererText()
        self.rank_box.pack_start(cell,True)
        self.rank_box.add_attribute(cell,'text',0)
        index = 0
        for item in _options.rankdir:
            store.append(row=[item[2]])
            if item[0] == self.options_dict['rankdir']:
                self.rank_box.set_active(index)
            index = index + 1
        dialog.add_frame_option(_("GraphViz Options"),
                              _("Graph direction"),
                              self.rank_box,
                              _("Whether generations go from top to bottom "
                                "or left to right."))

        self.color_box = gtk.ComboBox()
        store = gtk.ListStore(str)
        self.color_box.set_model(store)
        cell = gtk.CellRendererText()
        self.color_box.pack_start(cell,True)
        self.color_box.add_attribute(cell,'text',0)
        index = 0
        for item in _options.colors:
            store.append(row=[item[2]])
            if item[0] == self.options_dict['color']:
                self.color_box.set_active(index)
            index = index + 1
        dialog.add_frame_option(_("GraphViz Options"),
                              _("Graph coloring"),
                              self.color_box,
                              _("Males will be shown with blue, females "
                                "with red.  If the sex of an individual "
                                "is unknown it will be shown with gray."))

        self.arrowstyle_box = gtk.ComboBox()
        store = gtk.ListStore(str)
        self.arrowstyle_box.set_model(store)
        cell = gtk.CellRendererText()
        self.arrowstyle_box.pack_start(cell,True)
        self.arrowstyle_box.add_attribute(cell,'text',0)
        index = 0
        for item in _options.arrowstyles:
            store.append(row=[item[2]])
            if item[0] == self.options_dict['arrow']:
                self.arrowstyle_box.set_active(index)
            index = index + 1
        dialog.add_frame_option(_("GraphViz Options"),
                                _("Arrowhead direction"),
                                self.arrowstyle_box,
                                _("Choose the direction that the arrows point."))

        self.font_box = gtk.ComboBox()
        store = gtk.ListStore(str)
        self.font_box.set_model(store)
        cell = gtk.CellRendererText()
        self.font_box.pack_start(cell,True)
        self.font_box.add_attribute(cell,'text',0)
        index = 0
        for item in _options.fonts:
            if item[3]:
                name = "%s (iso-latin1 font)" % item[2]
            else:
                name = item[2]
            store.append(row=[name])
            if item[0] == self.options_dict['font']:
                self.font_box.set_active(index)
            index = index + 1
        dialog.add_frame_option(_("GraphViz Options"),
                              _("Font family"),
                              self.font_box,
                              _("Choose the font family. If international "
                                "characters don't show, use FreeSans font. "
                                "FreeSans is available from: "
                                "http://www.nongnu.org/freefont/"))

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

        # Page options tab
        margin_adj = gtk.Adjustment(value=self.options_dict['margin'],
                        lower=0.0, upper=10.0, step_incr=1.0)

        self.margin_sb = gtk.SpinButton(adjustment=margin_adj, digits=1)

        dialog.add_frame_option(_("Page Options"),
                              _("Margin size"),
                              self.margin_sb)

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
        self.options_dict['incid'] = int(self.includeid_cb.get_active())
        self.options_dict['justyears'] = int(self.just_years_cb.get_active())
        self.options_dict['placecause'] = int(self.place_cause_cb.get_active())
        self.options_dict['rankdir'] = \
                _options.rankdir[self.rank_box.get_active()][0]
        self.options_dict['color'] = \
                _options.colors[self.color_box.get_active()][0]
        self.options_dict['arrow'] = \
                _options.arrowstyles[self.arrowstyle_box.get_active()][0]
        self.options_dict['font'] = \
                _options.fonts[self.font_box.get_active()][0]
        self.options_dict['latin'] = \
                _options.fonts[self.font_box.get_active()][3]
        if self.handler.module_name == "rel_graph2":
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
        self.category = Report.CATEGORY_CODE
        Report.ReportDialog.__init__(self,database,person,self.options_class,
                                    name,translated_name)

        response = self.window.run()
        if response == gtk.RESPONSE_OK:
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

    def init(self):
        pass

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def cl_report(database,name,category,options_str_dict):

    clr = Report.CommandLineReport(database,name,category,GraphVizOptions,
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
class GraphVizGraphics(Report.Report):
    def __init__(self,database,person,options_class):
        self.database = database
        self.start_person = person
        self.options_class = options_class
        self.doc = options_class.get_document()

        self.user_output = options_class.get_output()
        self.junk_output = os.path.join(const.home_dir,"junk")
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
register_report(
    name = 'rel_graph',
    category = Report.CATEGORY_CODE,
    report_class = GraphVizDialog,
    options_class = cl_report,
    modes = Report.MODE_GUI | Report.MODE_CLI,
    translated_name = _("Relationship Graph"),
    status = _("Stable"),
    description= get_description(),
    author_name="Donald N. Allingham",
    author_email="don@gramps-project.org"
    )

if dot_found:
    register_report(
        name = 'rel_graph2',
        category = Report.CATEGORY_DRAW,
        report_class = GraphVizGraphics,
        options_class = GraphVizOptions,
        modes = Report.MODE_GUI | Report.MODE_CLI,
        translated_name = _("Relationship Graph"),
        status = _("Stable"),
        description= get_description_graphics(),
        author_name="Donald N. Allingham",
        author_email="don@gramps-project.org"
    )
