#
# Gramps - a GTK+/GNOME based genealogy program
#
# Adapted from Graphviz.py (now deprecated)
#    Copyright (C) 2000-2007  Donald N. Allingham
#    Copyright (C) 2005-2006  Eero Tamminen
#    Copyright (C) 2007-2008  Brian G. Matherly
#    Copyright (C) 2007       Johan Gonqvist <johan.gronqvist@gmail.com>
#    Contributions by Lorenzo Cappelletti <lorenzo.cappelletti@email.it>
#    Copyright (C) 2008       Stephane Charette <stephanecharette@gmail.com>
#    Copyright (C) 2009       Gary Burton
#    Contribution 2009 by     Bob Ham <rah@bash.sh>
#    Copyright (C) 2010       Jakim Friant
#    Copyright (C) 2013       Fedir Zinchuk <fedikw@gmail.com>
#    Copyright (C) 2013-2015  Paul Franklin
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

"""
Create a relationship graph using Graphviz
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from functools import partial

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.constfunc import conv_to_unicode
from gramps.gen.plug.menu import (BooleanOption, EnumeratedListOption,
                                  FilterOption, PersonOption, ColorOption)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils as ReportUtils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.lib import ChildRefType, EventRoleType, EventType
from gramps.gen.utils.file import media_path_full, find_file
from gramps.gui.thumbnails import get_thumbnail_path
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.utils.db import get_birth_or_fallback, get_death_or_fallback
from gramps.gen.display.place import displayer as place_displayer

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
# RelGraphReport class
#
#------------------------------------------------------------------------
class RelGraphReport(Report):

    def __init__(self, database, options, user):
        """
        Create RelGraphReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        This report needs the following parameters (class variables)
        that come in the options class.
        
        filter     - Filter to be applied to the people of the database.
                     The option class carries its number, and the function
                     returning the list of filters.
        arrow      - Arrow styles for heads and tails.
        showfamily - Whether to show family nodes.
        incid      - Whether to include IDs.
        url        - Whether to include URLs.
        inclimg    - Include images or not
        imgpos     - Image position, above/beside name
        color      - Whether to use outline, colored outline or filled color
                     in graph
        color_males    - Colour to apply to males
        color_females  - Colour to apply to females
        color_unknown  - Colour to apply to unknown genders
        color_families - Colour to apply to families
        dashed         - Whether to use dashed lines for non-birth relationships
        use_roundedcorners - Whether to use rounded corners for females
        name_format    - Preferred format to display names
        incl_private   - Whether to include private data
        event_choice   - Whether to include dates and/or places
        """
        Report.__init__(self, database, options, user)

        menu = options.menu
        get_option_by_name = options.menu.get_option_by_name
        get_value = lambda name: get_option_by_name(name).get_value()

        stdoptions.run_private_data_option(self, menu)

        self.includeid = get_value('incid')
        self.includeurl = get_value('url')
        self.includeimg = get_value('includeImages')
        self.imgpos     = get_value('imageOnTheSide')
        self.use_roundedcorners = get_value('useroundedcorners')
        self.adoptionsdashed = get_value('dashed')
        self.show_families = get_value('showfamily')
        self.use_subgraphs = get_value('usesubgraphs')
        self.event_choice = get_value('event_choice')

        self.colorize = get_value('color')
        color_males = get_value('colormales')
        color_females = get_value('colorfemales')
        color_unknown = get_value('colorunknown')
        color_families = get_value('colorfamilies')
        self.colors = {
            'male': color_males,
            'female': color_females,
            'unknown': color_unknown,
            'family': color_families
        }

        arrow_str = get_value('arrow')
        if 'd' in arrow_str:
            self.arrowheadstyle = 'normal'
        else:
            self.arrowheadstyle = 'none'
        if 'a' in arrow_str:
            self.arrowtailstyle = 'normal'
        else:
            self.arrowtailstyle = 'none'
        filter_option = get_option_by_name('filter')
        self._filter = filter_option.get_filter()

        lang = menu.get_option_by_name('trans').get_value()
        self._locale = self.set_locale(lang)

        stdoptions.run_name_format_option(self, menu)

        pid = get_value('pid')
        self.center_person = self.database.get_person_from_gramps_id(pid)

        self.increlname = get_value('increlname')
        if self.increlname :
            self.rel_calc = get_relationship_calculator(reinit=True,
                                                        clocale=self._locale)

        if __debug__:
            self.advrelinfo = get_value('advrelinfo')
        else:
            self.advrelinfo = False

    def write_report(self):
        self.person_handles = self._filter.apply(self.database,
                    self.database.iter_person_handles())
        
        if len(self.person_handles) > 1:
            self.add_persons_and_families()
            self.add_child_links_to_families()

    def add_child_links_to_families(self):
        """
        returns string of Graphviz edges linking parents to families or
        children
        """
        # Hash people in a dictionary for faster inclusion checking
        person_dict = dict([conv_to_unicode(handle, 'utf-8'), 1]
                                for handle in self.person_handles)
            
        for person_handle in self.person_handles:
            person = self.database.get_person_from_handle(person_handle)
            p_id = person.get_gramps_id()
            for fam_handle in person.get_parent_family_handle_list():
                family = self.database.get_family_from_handle(fam_handle)
                father_handle = family.get_father_handle()
                mother_handle = family.get_mother_handle()
                for child_ref in family.get_child_ref_list():
                    if child_ref.ref == conv_to_unicode(person_handle, 'utf-8'):
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
        adopted = ((int(frel) != ChildRefType.BIRTH) or
                   (int(mrel) != ChildRefType.BIRTH))
        # If birth relation to father is NONE, meaning there is no father and
        # if birth relation to mother is BIRTH then solid line
        if ((int(frel) == ChildRefType.NONE) and
           (int(mrel) == ChildRefType.BIRTH)):
            adopted = False
        if adopted and self.adoptionsdashed:
            style = 'dotted'
        self.doc.add_link( family.get_gramps_id(), p_id, style,  
                           self.arrowheadstyle, self.arrowtailstyle )
        
    def add_parent_link(self, p_id, parent_handle, rel):
        "Links the child to a parent"
        style = 'solid'
        if (int(rel) != ChildRefType.BIRTH) and self.adoptionsdashed:
            style = 'dotted'
        parent = self.database.get_person_from_handle(parent_handle)
        self.doc.add_link( parent.get_gramps_id(), p_id, style,
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
            if person is None:
                continue
            p_id = person.get_gramps_id()
            # Output the person's node
            label = self.get_person_label(person)
            (shape, style, color, fill) = self.get_gender_style(person)
            url = ""
            if self.includeurl:
                h = conv_to_unicode(person_handle, 'utf-8')
                dirpath = "ppl/%s/%s" % (h[-1], h[-2])
                dirpath = dirpath.lower()
                url = "%s/%s.html" % (dirpath, h)
                
            self.doc.add_node(p_id, label, shape, color, style, fill, url)
  
            # Output families where person is a parent
            if self.show_families:
                family_list = person.get_family_handle_list()
                for fam_handle in family_list:
                    family = self.database.get_family_from_handle(fam_handle)
                    if family is None:
                        continue
                    if fam_handle not in families_done:
                        families_done[fam_handle] = 1
                        self.__add_family(fam_handle)
                    # If subgraphs are not chosen then each parent is linked 
                    # separately to the family. This gives Graphviz greater
                    # control over the layout of the whole graph but
                    # may leave spouses not positioned together.
                    if not self.use_subgraphs:
                        self.doc.add_link(p_id, family.get_gramps_id(), "",
                                          self.arrowheadstyle,
                                          self.arrowtailstyle)
                        
    def __add_family(self, fam_handle):
        """Add a node for a family and optionally link the spouses to it"""
        fam = self.database.get_family_from_handle(fam_handle)
        if fam is None:
            return
        fam_id = fam.get_gramps_id()

        date_label = place_label = None
        for event_ref in fam.get_event_ref_list():
            event = self.database.get_event_from_handle(event_ref.ref)
            if event is None:
                continue
            if (event.type == EventType.MARRIAGE and
                (event_ref.get_role() == EventRoleType.FAMILY or 
                 event_ref.get_role() == EventRoleType.PRIMARY)
               ):
                date_label = self.get_date_string(event)
                if not (self.event_choice == 3 and date_label):
                    place_label = self.get_place_string(event)
                break
        if self.includeid == 0 and not date_label and not place_label:
            label = ""
        elif self.includeid == 0 and not date_label and place_label:
            label = "(%s)" % place_label
        elif self.includeid == 0 and date_label and not place_label:
            label = "(%s)" % date_label
        elif self.includeid == 0 and date_label and place_label:
            label = "(%s)\\n(%s)" % (date_label, place_label)
        elif self.includeid == 1 and not date_label and not place_label:
            label = "(%s)" % fam_id
        elif self.includeid == 1 and not date_label and place_label:
            label = "(%s) (%s)" % (fam_id, place_label) # id on same line
        elif self.includeid == 1 and date_label and not place_label:
            label = "(%s) (%s)" % (fam_id, date_label) # id on same line
        elif self.includeid == 1 and date_label and place_label:
            label = "(%s) (%s)\\n(%s)" % (fam_id, date_label, place_label)
        elif self.includeid == 2 and not date_label and not place_label:
            label = "(%s)" % fam_id
        elif self.includeid == 2 and not date_label and place_label:
            label = "(%s)\\n(%s)" % (fam_id, place_label) # id on own line
        elif self.includeid == 2 and date_label and not place_label:
            label = "(%s)\\n(%s)" % (fam_id, date_label) # id on own line
        elif self.includeid == 2 and date_label and place_label:
            label = "(%s)\\n(%s)\\n(%s)" % (fam_id, date_label, place_label)
        color = ""
        fill = ""
        style = "solid"
        if self.colorize == 'colored':
            color = self.colors['family']
        elif self.colorize == 'filled':
            fill = self.colors['family']
            style = "filled"
        self.doc.add_node(fam_id, label, "ellipse", color, style, fill)
        
        # If subgraphs are used then we add both spouses here and Graphviz
        # will attempt to position both spouses closely together.
        # TODO: A person who is a parent in more than one family may only be
        #       positioned next to one of their spouses. The code currently
        #       does not take into account multiple spouses.
        if self.use_subgraphs:
            self.doc.start_subgraph(fam_id)
            f_handle = fam.get_father_handle()
            m_handle = fam.get_mother_handle()
            if f_handle:
                father = self.database.get_person_from_handle(f_handle)
                self.doc.add_link(father.get_gramps_id(),
                                  fam_id, "", 
                                  self.arrowheadstyle,
                                  self.arrowtailstyle)
            if m_handle:
                mother = self.database.get_person_from_handle(m_handle)
                self.doc.add_link(mother.get_gramps_id(),
                                  fam_id, "", 
                                  self.arrowheadstyle,
                                  self.arrowtailstyle)
            self.doc.end_subgraph()

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

        if person == self.center_person and self.increlname:
            shape = "octagon"

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
                    imagePath = get_thumbnail_path(
                                    media_path_full(self.database, 
                                                    media.get_path()),
                                    rectangle=mediaList[0].get_rectangle())
                    # test if thumbnail actually exists in thumbs
                    # (import of data means media files might not be present
                    imagePath = find_file(imagePath)

        label = ""
        lineDelimiter = '\\n'

        # If we have an image, then start an HTML table; remember to close
        # the table afterwards!
        #
        # This isn't a free-form HTML format here...just a few keywords that
        # happen to be
        # similar to keywords commonly seen in HTML.  For additional
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
        nm = self._name_display.display(person)
        if self.bUseHtmlOutput :
            # avoid < and > in the name, as this is html text
            label += nm.replace('<', '&#60;').replace('>', '&#62;')
        else :
            label += nm
        p_id = person.get_gramps_id()
        if self.includeid == 1: # same line
            label += " (%s)" % p_id
        elif self.includeid == 2: # own line
            label += "%s(%s)" % (lineDelimiter, p_id)
        if self.event_choice != 0:
            b_date, d_date, b_place, d_place = self.get_event_strings(person)
            if self.event_choice in [1, 2, 3, 4, 5] and (b_date or d_date):
                label += '%s(' % lineDelimiter
                if b_date:
                    label += '%s' % b_date
                label += ' - '
                if d_date:
                    label += '%s' % d_date
                label += ')'
            if (self.event_choice in [2, 3, 5, 6] and
                (b_place or d_place) and
                not (self.event_choice == 3 and (b_date or d_date))
               ):
                label += '%s(' % lineDelimiter
                if b_place:
                    label += '%s' % b_place
                label += ' - '
                if d_place:
                    label += '%s' % d_place
                label += ')'

        if self.increlname and self.center_person != person:
            # display relationship info
            if self.advrelinfo:
                (relationship, Ga, Gb) = self.rel_calc.get_one_relationship(
                            self.database, self.center_person, person,
                            extra_info=True, olocale=self._locale)
                if relationship:
                    label += "%s(%s Ga=%d Gb=%d)" % (lineDelimiter,
                                                     relationship, Ga, Gb)
            else:
                relationship = self.rel_calc.get_one_relationship(
                            self.database, self.center_person, person,
                            olocale=self._locale)
                if relationship:
                    label += "%s(%s)" % (lineDelimiter, relationship)

        # see if we have a table that needs to be terminated
        if self.bUseHtmlOutput:
            label += '</TD></TR></TABLE>'
            return label
        else :
            # non html label is enclosed by "" so escape other "
            return label.replace('"', '\\\"')
    
    def get_event_strings(self, person):
        "returns tuple of birth/christening and death/burying date strings"

        birth_date = birth_place = death_date = death_place = ""

        birth_event = get_birth_or_fallback(self.database, person)
        if birth_event:
            birth_date = self.get_date_string(birth_event)
            birth_place = self.get_place_string(birth_event)

        death_event = get_death_or_fallback(self.database, person)
        if death_event:
            death_date = self.get_date_string(death_event)
            death_place = self.get_place_string(death_event)

        return (birth_date, death_date, birth_place, death_place)

    def get_date_string(self, event):
        """
        return date string for an event label.
        
        Based on the data availability and preferences, we select one
        of the following for a given event:
            year only
            complete date
            empty string
        """
        if event and event.get_date_object() is not None:
            event_date = event.get_date_object()
            if event_date.get_year_valid():
                if self.event_choice in [4, 5]:
                    return '%i' % event_date.get_year()
                elif self.event_choice in [1, 2, 3]:
                    return self._get_date(event_date)
        return ''

    def get_place_string(self, event):
        """
        return place string for an event label.
        
        Based on the data availability and preferences, we select one
        of the following for a given event:
            place name
            empty string
        """
        if event and self.event_choice in [2, 3, 5, 6]:
            return place_displayer.display_event(self.database, event)
        return ''

#------------------------------------------------------------------------
#
# RelGraphOptions class 
#
#------------------------------------------------------------------------
class RelGraphOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """
    def __init__(self, name, dbase):
        self.__pid = None
        self.__filter = None
        self.__show_relships = None
        self.__show_GaGb = None
        self.__include_images = None
        self.__image_on_side = None
        self.__db = dbase
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        ################################
        category_name = _("Report Options")
        add_option = partial(menu.add_option, category_name)
        ################################

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
                         _("Determines what people are included in the graph"))
        add_option("filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)
        
        self.__pid = PersonOption(_("Center Person"))
        self.__pid.set_help(_("The center person for the report"))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)

        self._nf = stdoptions.add_name_format_option(menu, category_name)
        self._nf.connect('value-changed', self.__update_filters)

        self.__update_filters()

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_localization_option(menu, category_name)

        ################################
        add_option = partial(menu.add_option, _("Include"))
        ################################

        self.event_choice = EnumeratedListOption(_('Dates and/or Places'), 0)
        self.event_choice.add_item(0, _('Do not include any dates or places'))
        self.event_choice.add_item(1, _('Include (birth, marriage, death) '
                                         'dates, but no places'))
        self.event_choice.add_item(2, _('Include (birth, marriage, death) '
                                         'dates, and places'))
        self.event_choice.add_item(3, _('Include (birth, marriage, death) '
                                         'dates, and places if no dates'))
        self.event_choice.add_item(4, _('Include (birth, marriage, death) '
                                         'years, but no places'))
        self.event_choice.add_item(5, _('Include (birth, marriage, death) '
                                         'years, and places'))
        self.event_choice.add_item(6, _('Include (birth, marriage, death) '
                                         'places, but no dates'))
        self.event_choice.set_help(_("Whether to include dates and/or places"))
        add_option("event_choice", self.event_choice)

        url = BooleanOption(_("Include URLs"), False)
        url.set_help(_("Include a URL in each graph node so "
                       "that PDF and imagemap files can be "
                       "generated that contain active links "
                       "to the files generated by the 'Narrated "
                       "Web Site' report."))
        add_option("url", url)
        
        include_id = EnumeratedListOption(_('Include Gramps ID'), 0)
        include_id.add_item(0, _('Do not include'))
        include_id.add_item(1, _('Share an existing line'))
        include_id.add_item(2, _('On a line of its own'))
        include_id.set_help(_("Whether (and where) to include Gramps IDs"))
        add_option("incid", include_id)
        
        self.__show_relships = BooleanOption(
                            _("Include relationship to center person"), False)
        self.__show_relships.set_help(_("Whether to show every "
                            "person's relationship to the center person"))
        add_option("increlname", self.__show_relships)
        self.__show_relships.connect('value-changed',
                                     self.__show_relships_changed)

        self.__include_images = BooleanOption(
                                 _('Include thumbnail images of people'), False)
        self.__include_images.set_help(
                                 _("Whether to include thumbnails of people."))
        add_option("includeImages", self.__include_images)
        self.__include_images.connect('value-changed', self.__image_changed)
        
        self.__image_on_side = EnumeratedListOption(_("Thumbnail Location"), 0)
        self.__image_on_side.add_item(0, _('Above the name'))
        self.__image_on_side.add_item(1, _('Beside the name'))
        self.__image_on_side.set_help(
                              _("Where the thumbnail image should appear "
                                "relative to the name"))
        add_option("imageOnTheSide", self.__image_on_side)
        
        if __debug__:
            self.__show_GaGb = BooleanOption(_("Include relationship "
                                               "debugging numbers also"),
                                             False)
            self.__show_GaGb.set_help(_("Whether to include 'Ga' and 'Gb' "
                            "also, to debug the relationship calculator"))
            add_option("advrelinfo", self.__show_GaGb)

        ################################
        add_option = partial(menu.add_option, _("Graph Style"))
        ################################

        color = EnumeratedListOption(_("Graph coloring"), 'filled')
        for i in range( 0, len(_COLORS) ):
            color.add_item(_COLORS[i]["value"], _COLORS[i]["name"])
        color.set_help(_("Males will be shown with blue, females "
                         "with red.  If the sex of an individual "
                         "is unknown it will be shown with gray."))
        add_option("color", color)

        color_males = ColorOption(_('Males'), '#e0e0ff')
        color_males.set_help(_('The color to use to display men.'))
        add_option('colormales', color_males)

        color_females = ColorOption(_('Females'), '#ffe0e0')
        color_females.set_help(_('The color to use to display women.'))
        add_option('colorfemales', color_females)

        color_unknown = ColorOption(_('Unknown'), '#e0e0e0')
        color_unknown.set_help(
            _('The color to use when the gender is unknown.')
            )
        add_option('colorunknown', color_unknown)

        color_family = ColorOption(_('Families'), '#ffffe0')
        color_family.set_help(_('The color to use to display families.'))
        add_option('colorfamilies', color_family)
        
        arrow = EnumeratedListOption(_("Arrowhead direction"), 'd')
        for i in range( 0, len(_ARROWS) ):
            arrow.add_item(_ARROWS[i]["value"], _ARROWS[i]["name"])
        arrow.set_help(_("Choose the direction that the arrows point."))
        add_option("arrow", arrow)

        roundedcorners = BooleanOption(     # see bug report #2180
                    _("Use rounded corners"), False)
        roundedcorners.set_help(
                    _("Use rounded corners to differentiate "
                      "between women and men."))
        add_option("useroundedcorners", roundedcorners)
        
        dashed = BooleanOption(
                  _("Indicate non-birth relationships with dotted lines"), True)
        dashed.set_help(_("Non-birth relationships will show up "
                          "as dotted lines in the graph."))
        add_option("dashed", dashed)
        
        showfamily = BooleanOption(_("Show family nodes"), True)
        showfamily.set_help(_("Families will show up as ellipses, linked "
                              "to parents and children."))
        add_option("showfamily", showfamily)
        
    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        nfv = self._nf.get_value()
        filter_list = ReportUtils.get_person_filters(person,
                                                     include_single=False,
                                                     name_format=nfv)
        self.__filter.set_filters(filter_list)
        
    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        filter_value = self.__filter.get_value()
        if filter_value in [1, 2, 3, 4]:
            # Filters 1, 2, 3 and 4 rely on the center person
            self.__pid.set_available(True)
        elif self.__show_relships and self.__show_relships.get_value():
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
        
    def __show_relships_changed(self):
        """
        Enable/disable menu items if relationships are required
        """
        if self.__show_GaGb:
            self.__show_GaGb.set_available(self.__show_relships.get_value())
        self.__filter_changed()
