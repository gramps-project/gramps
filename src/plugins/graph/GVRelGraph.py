#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Brian G. Matherly
#
# Adapted from GraphViz.py (now deprecated)
#    Copyright (C) 2000-2007  Donald N. Allingham
#    Copyright (C) 2005-2006  Eero Tamminen
#    Copyright (C) 2007       Johan Gonqvist <johan.gronqvist@gmail.com>
#    Contributions by Lorenzo Cappelletti <lorenzo.cappelletti@email.it>
#    Copyright (C) 2008       Stephane Charette <stephanecharette@gmail.com>
#    Copyright (C) 2009       Gary Burton
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

"""
Create a relationship graph using Graphviz
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.plug import PluginManager
from gen.plug.menu import BooleanOption, EnumeratedListOption, FilterOption, \
                          PersonOption
from ReportBase import Report, ReportUtils, MenuReportOptions, CATEGORY_GRAPHVIZ
from BasicUtils import name_displayer
import DateHandler
import gen.lib
import Utils
import ThumbNails

#------------------------------------------------------------------------
#
# Constant options items
#
#------------------------------------------------------------------------
_COLORS = [ { 'name' : _("B&W outline"),     'value' : 'outlined' },
            { 'name' : _("Colored outline"), 'value' : 'colored' },
            { 'name' : _("Color fill"),      'value' : 'filled' }]

_ARROWS = [ { 'name' : _("Descendants <- Ancestors"),  'value' : 'd' },
            { 'name' : _("Descendants -> Ancestors"),  'value' : 'a' },
            { 'name' : _("Descendants <-> Ancestors"), 'value' : 'da' },
            { 'name' : _("Descendants - Ancestors"),   'value' : '' }]

#------------------------------------------------------------------------
#
# Report class
#
#------------------------------------------------------------------------
class RelGraphReport(Report):

    def __init__(self, database, options_class):
        """
        Create ComprehensiveAncestorsReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        filter     - Filter to be applied to the people of the database.
                     The option class carries its number, and the function
                     returning the list of filters.
        arrow      - Arrow styles for heads and tails.
        showfamily - Whether to show family nodes.
        incid      - Whether to include IDs.
        incdate    - Whether to include dates.
        justyears  - Use years only.
        use_place  - Whether to replace missing dates with place
        url        - Whether to include URLs.
        inclimg    - Include images or not
        imgpos     - Image position, above/beside name
        color      - Whether to use outline, colored outline or filled color
                     in graph
        dashed     - Whether to use dashed lines for non-birth relationships.
        use_roundedcorners - Whether to use rounded corners for females
        """
        Report.__init__(self, database, options_class)
        
        # Would be nice to get rid of these 2 hard-coded arrays of colours
        # and instead allow the user to pick-and-choose whatever colour they
        # want.  When/if this is done, take a look at the colour-selection
        # widget and code used in the FamilyLines graph.
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

        menu = options_class.menu
        self.includeid = menu.get_option_by_name('incid').get_value()
        self.includedates = menu.get_option_by_name('incdate').get_value()
        self.includeurl = menu.get_option_by_name('url').get_value()
        self.includeimg = menu.get_option_by_name('includeImages').get_value()
        self.imgpos     = menu.get_option_by_name('imageOnTheSide').get_value()
        self.use_roundedcorners = \
           menu.get_option_by_name('useroundedcorners').get_value()
        self.adoptionsdashed = menu.get_option_by_name('dashed').get_value()
        self.show_families = menu.get_option_by_name('showfamily').get_value()
        self.just_years = menu.get_option_by_name('justyears').get_value()
        self.use_place = menu.get_option_by_name('use_place').get_value()
        self.colorize = menu.get_option_by_name('color').get_value()
        if self.colorize == 'colored':
            self.colors = colored
        elif self.colorize == 'filled':
            self.colors = filled
        arrow_str = menu.get_option_by_name('arrow').get_value()
        if arrow_str.find('a') + 1:
            self.arrowheadstyle = 'normal'
        else:
            self.arrowheadstyle = 'none'
        if arrow_str.find('d') + 1:
            self.arrowtailstyle = 'normal'
        else:
            self.arrowtailstyle = 'none'
        filter_option = options_class.menu.get_option_by_name('filter')
        self._filter = filter_option.get_filter()

    def write_report(self):
        self.person_handles = self._filter.apply(self.database,
                    self.database.get_person_handles(sort_handles=False))
        
        if len(self.person_handles) > 1:
            self.add_persons_and_families()
            self.add_child_links_to_families()

    def add_child_links_to_families(self):
        "returns string of GraphViz edges linking parents to families or \
         children"
        person_dict = {}
        # Hash people in a dictionary for faster inclusion checking
        for person_handle in self.person_handles:
            person_dict[person_handle] = 1
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
                    self.add_family_link(p_id, family, frel, mrel)
                else:
                    # Link to the parents' nodes directly, if they are in graph
                    if father_handle and father_handle in person_dict:
                        self.add_parent_link(p_id, father_handle, frel)
                    if mother_handle and mother_handle in person_dict:
                        self.add_parent_link(p_id, mother_handle, mrel)

    def add_family_link(self, p_id, family, frel, mrel):
        "Links the child to a family"
        style = 'solid'
        adopted = ((int(frel) != gen.lib.ChildRefType.BIRTH) or
                   (int(mrel) != gen.lib.ChildRefType.BIRTH))
        if adopted and self.adoptionsdashed:
            style = 'dotted'
        self.doc.add_link( p_id, family.get_gramps_id(), style, 
                           self.arrowheadstyle, self.arrowtailstyle )
        
    def add_parent_link(self, p_id, parent_handle, rel):
        "Links the child to a parent"
        style = 'solid'
        if (int(rel) != gen.lib.ChildRefType.BIRTH) and self.adoptionsdashed:
            style = 'dotted'
        parent = self.database.get_person_from_handle(parent_handle)
        self.doc.add_link( p_id, parent.get_gramps_id(), style, 
                           self.arrowheadstyle, self.arrowtailstyle )
        
    def add_persons_and_families(self):
        "adds nodes for persons and their families"
        # variable to communicate with get_person_label
        self.bUseHtmlOutput = False
            
        # The list of families for which we have output the node,
        # so we don't do it twice
        families_done = {}
        for person_handle in self.person_handles:
            # determine per person if we use HTML style label
            if self.includeimg:
                self.bUseHtmlOutput = True
            person = self.database.get_person_from_handle(person_handle)
            p_id = person.get_gramps_id()
            # Output the person's node
            label = self.get_person_label(person)
            (shape, style, color, fill) = self.get_gender_style(person)
            url = ""
            if self.includeurl:
                h = person_handle
                dirpath = "ppl/%s/%s" % (h[0], h[1])
                dirpath = dirpath.lower()
                url = "%s/%s.html" % (dirpath, h)
                
            self.doc.add_node(p_id, label, shape, color, style, fill, url)
  
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
                            if event.type == gen.lib.EventType.MARRIAGE:
                                label = self.get_event_string(event)
                                break
                        if self.includeid:
                            label = "%s (%s)" % (label, fam_id)
                        color = ""
                        fill = ""
                        style = "solid"
                        if self.colorize == 'colored':
                            color = self.colors['family']
                        elif self.colorize == 'filled':
                            fill = self.colors['family']
                            style = "filled"
                        self.doc.add_node(fam_id, label, "ellipse",
                                          color, style, fill)
                    # Link this person to all his/her families.
                    self.doc.add_link( fam_id, p_id, "", 
                                      self.arrowheadstyle, self.arrowtailstyle )

    def get_gender_style(self, person):
        "return gender specific person style"
        gender = person.get_gender()
        shape = "box"
        style = "solid"
        color = ""
        fill = ""

        if gender == person.FEMALE and self.use_roundedcorners:
            style = "rounded"
        elif gender == person.UNKNOWN:
            shape = "hexagon"

        if self.colorize == 'colored':
            if gender == person.MALE:
                color = self.colors['male']
            elif gender == person.FEMALE:
                color = self.colors['female']
            else:
                color = self.colors['unknown']
        elif self.colorize == 'filled':
            style += ",filled"
            if gender == person.MALE:
                fill = self.colors['male']
            elif gender == person.FEMALE:
                fill = self.colors['female']
            else:
                fill = self.colors['unknown']
        return(shape, style, color, fill)

    def get_person_label(self, person):
        "return person label string"
        # see if we have an image to use for this person
        imagePath = None
        if self.bUseHtmlOutput:
            mediaList = person.get_media_list()
            if len(mediaList) > 0:
                mediaHandle = mediaList[0].get_reference_handle()
                media = self.database.get_object_from_handle(mediaHandle)
                mediaMimeType = media.get_mime_type()
                if mediaMimeType[0:5] == "image":
                    imagePath = ThumbNails.get_thumbnail_path(
                                    Utils.media_path_full(self.database, 
                                                          media.get_path()))
                    # test if thumbnail actually exists in thumbs
                    # (import of data means media files might not be present
                    imagePath = Utils.find_file(imagePath)

        label = u""
        lineDelimiter = '\\n'

        # If we have an image, then start an HTML table; remember to close
        # the table afterwards!
        #
        # This isn't a free-form HTML format here...just a few keywords that
        # happen to be
        # simillar to keywords commonly seen in HTML.  For additional
        # information on what
        # is allowed, see:
        #
        #       http://www.graphviz.org/info/shapes.html#html
        #
        if self.bUseHtmlOutput and imagePath:
            lineDelimiter = '<BR/>'
            label += '<TABLE BORDER="0" CELLSPACING="2" CELLPADDING="0" CELLBORDER="0"><TR><TD></TD><TD><IMG SRC="%s"/></TD><TD></TD>'  % imagePath
            if self.imgpos == 0:
                #trick it into not stretching the image
                label += '</TR><TR><TD COLSPAN="3">'
            else :
                label += '<TD>'
        else :
            #no need for html label with this person
            self.bUseHtmlOutput = False

        # at the very least, the label must have the person's name
        nm =  name_displayer.display_name(person.get_primary_name())
        if self.bUseHtmlOutput :
            # avoid < and > in the name, as this is html text
            label += nm.replace('<', '&#60;').replace('>', '&#62;')
        else :
            label += nm
        p_id = person.get_gramps_id()
        if self.includeid:
            label += " (%s)" % p_id
        if self.includedates:
            birth, death = self.get_date_strings(person)
            label = label + '%s(%s - %s)' % (lineDelimiter, birth, death)
            
        # see if we have a table that needs to be terminated
        if self.bUseHtmlOutput:
            label += '</TD></TR></TABLE>'
            return label
        else :
            # non html label is enclosed by "" so excape other "
            return label.replace('"', '\\\"')
    
    def get_date_strings(self, person):
        "returns tuple of birth/christening and death/burying date strings"
        birth_event = ReportUtils.get_birth_or_fallback(self.database, person)
        if birth_event:
            birth = self.get_event_string(birth_event)
        else:
            birth = ""

        death_event = ReportUtils.get_death_or_fallback(self.database, person)
        if death_event:
            death = self.get_event_string(death_event)
        else:
            death = ""

        return (birth, death)

    def get_event_string(self, event):
        """
        return string for for an event label.
        
        Based on the data availability and preferences, we select one
        of the following for a given event:
            year only
            complete date
            place name
            empty string
        """
        if event:
            if event.get_date_object().get_year_valid():
                if self.just_years:
                    return '%i' % event.get_date_object().get_year()
                else:
                    return DateHandler.get_date(event)
            elif self.use_place:
                place_handle = event.get_place_handle()
                place = self.database.get_place_from_handle(place_handle)
                if place and place.get_title():
                    return place.get_title()
        return ''


#------------------------------------------------------------------------
#
# Options class 
#
#------------------------------------------------------------------------
class RelGraphOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """
    def __init__(self, name, dbase):
        self.__pid = None
        self.__filter = None
        self.__include_images = None
        self.__image_on_side = None
        self.__db = dbase
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        ################################
        category_name = _("Report Options")
        ################################

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
                         _("Determines what people are included in the graph"))
        menu.add_option(category_name, "filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)
        
        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter"))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)
        
        self.__update_filters()
        
        self.incdate = BooleanOption(
                            _("Include Birth, Marriage and Death dates"), True)
        self.incdate.set_help(_("Include the dates that the individual was "
                          "born, got married and/or died in the graph labels."))
        menu.add_option(category_name, "incdate", self.incdate)
        self.incdate.connect('value-changed', self.__include_dates_changed)
        
        self.justyears = BooleanOption(_("Limit dates to years only"), False)
        self.justyears.set_help(_("Prints just dates' year, neither "
                                  "month or day nor date approximation "
                                  "or interval are shown."))
        menu.add_option(category_name, "justyears", self.justyears)
        
        use_place = BooleanOption(_("Use place when no date"), True)
        use_place.set_help(_("When no birth, marriage, or death date is "
                              "available, the correspondent place field "
                              "will be used."))
        menu.add_option(category_name, "use_place", use_place)
        
        url = BooleanOption(_("Include URLs"), False)
        url.set_help(_("Include a URL in each graph node so "
                       "that PDF and imagemap files can be "
                       "generated that contain active links "
                       "to the files generated by the 'Narrated "
                       "Web Site' report."))
        menu.add_option(category_name, "url", url)
        
        incid = BooleanOption(_("Include IDs"), False)
        incid.set_help(_("Include individual and family IDs."))
        menu.add_option(category_name, "incid", incid)
        
        self.__include_images = BooleanOption(
                                 _('Include thumbnail images of people'), False)
        self.__include_images.set_help(
                                 _("Whether to include thumbnails of people."))
        menu.add_option(category_name, "includeImages", self.__include_images)
        self.__include_images.connect('value-changed', self.__image_changed)
        
        self.__image_on_side = EnumeratedListOption(_("Thumbnail Location"), 0)
        self.__image_on_side.add_item(0, _('Above the name'))
        self.__image_on_side.add_item(1, _('Beside the name'))
        self.__image_on_side.set_help(
                              _("Where the thumbnail image should appear "
                                "relative to the name"))
        menu.add_option(category_name, "imageOnTheSide", self.__image_on_side)
        
        ################################
        category_name = _("Graph Style")
        ################################

        color = EnumeratedListOption(_("Graph coloring"), 'filled')
        for i in range( 0, len(_COLORS) ):
            color.add_item(_COLORS[i]["value"], _COLORS[i]["name"])
        color.set_help(_("Males will be shown with blue, females "
                         "with red.  If the sex of an individual "
                         "is unknown it will be shown with gray."))
        menu.add_option(category_name, "color", color)
        
        arrow = EnumeratedListOption(_("Arrowhead direction"), 'd')
        for i in range( 0, len(_ARROWS) ):
            arrow.add_item(_ARROWS[i]["value"], _ARROWS[i]["name"])
        arrow.set_help(_("Choose the direction that the arrows point."))
        menu.add_option(category_name, "arrow", arrow)

        roundedcorners = BooleanOption(     # see bug report #2180
                    _("Use rounded corners"), False)
        roundedcorners.set_help(
                    _("Use rounded corners to differentiate "
                      "between women and men."))
        menu.add_option(category_name, "useroundedcorners", roundedcorners)
        
        dashed = BooleanOption(
                  _("Indicate non-birth relationships with dotted lines"), True)
        dashed.set_help(_("Non-birth relationships will show up "
                          "as dotted lines in the graph."))
        menu.add_option(category_name, "dashed", dashed)
        
        showfamily = BooleanOption(_("Show family nodes"), True)
        showfamily.set_help(_("Families will show up as ellipses, linked "
                              "to parents and children."))
        menu.add_option(category_name, "showfamily", showfamily)
        
    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        filter_list = ReportUtils.get_person_filters(person, False)
        self.__filter.set_filters(filter_list)
        
    def __include_dates_changed(self):
        """
        Enable/disable menu items if dates are required
        """
        if self.incdate.get_value():
            self.justyears.set_available(True)
        else:
            self.justyears.set_available(False)

    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        filter_value = self.__filter.get_value()
        if filter_value in [1, 2, 3, 4]:
            # Filters 1, 2, 3 and 4 rely on the center person
            self.__pid.set_available(True)
        else:
            # The rest don't
            self.__pid.set_available(False)

    def __image_changed(self):
        """
        Handle thumbnail change. If the image is not to be included, make the
        image location option unavailable.
        """
        self.__image_on_side.set_available(self.__include_images.get_value())

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_report(
    name            = 'rel_graph',
    category        = CATEGORY_GRAPHVIZ,
    report_class    = RelGraphReport,
    options_class   = RelGraphOptions,
    modes           = PluginManager.REPORT_MODE_GUI | \
                      PluginManager.REPORT_MODE_CLI,
    translated_name = _("Relationship Graph"),
    status          = _("Stable"),
    description     = _("Produces relationship graphs using Graphviz"),
    author_name     = "Brian G. Matherly",
    author_email    = "brian@gramps-project.org"
    )



