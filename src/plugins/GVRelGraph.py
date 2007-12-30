#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Brian G. Matherly
#
# Adapted from GraphViz.py (now deprecated)
#    Copyright (C) 2000-2007  Donald N. Allingham
#    Copyright (C) 2007       Johan Gonqvist <johan.gronqvist@gmail.com>
#    Contributions by Lorenzo Cappelletti <lorenzo.cappelletti@email.it>
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

# $Id:  $

"""
Create a relationship graph using Graphviz
"""

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from PluginUtils import register_report, FilterListOption, \
                        EnumeratedListOption, BooleanOption
from ReportBase import Report, MenuReportOptions, \
    MODE_GUI, MODE_CLI, CATEGORY_GRAPHVIZ
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
_COLORS = [ { 'name' : _("B&W outline"),     'value' : "outline" },
            { 'name' : _("Colored outline"), 'value' : "colored" },
            { 'name' : _("Color fill"),      'value' : "filled"  }]

_ARROWS = [ { 'name' : _("Descendants <- Ancestors"),  'value' : 'd'  },
            { 'name' : _("Descendants -> Ancestors"),  'value' : 'a'  },
            { 'name' : _("Descendants <-> Ancestors"), 'value' : 'da' },
            { 'name' : _("Descendants - Ancestors"),   'value' : ''   }]

#------------------------------------------------------------------------
#
# Report class
#
#------------------------------------------------------------------------
class RelGraphReport(Report):

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
        arrow      - Arrow styles for heads and tails.
        showfamily - Whether to show family nodes.
        incid      - Whether to include IDs.
        incdate    - Whether to include dates.
        justyears  - Use years only.
        placecause - Whether to replace missing dates with place or cause
        url        - Whether to include URLs.
        inclimg    - Include images or not
        imgpos     - Image position, above/beside name
        color      - Whether to use outline, colored outline or filled color in graph
        dashed     - Whether to use dashed lines for non-birth relationships.
        """
        Report.__init__(self,database,person,options_class)
        
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

        options = options_class.handler.options_dict
        self.includeid = options['incid']
        self.includedates = options['incdate']
        self.includeurl = options['url']
        self.includeimg = options['includeImages']
        self.imgpos     = options['imageOnTheSide']
        self.adoptionsdashed = options['dashed']
        self.show_families = options['showfamily']
        self.just_years = options['justyears']
        self.placecause = options['placecause']
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

        filter_option = options_class.menu.get_option_by_name('filter')
        filter_index = int(filter_option.get_value())
        filters = filter_option.get_filters()
        self.filter = filters[filter_index]

    def write_report(self):
        self.person_handles = self.filter.apply(self.database,
                    self.database.get_person_handles(sort_handles=False))
        
        if len(self.person_handles) > 1:
            self.add_persons_and_families()
            self.add_child_links_to_families()

    def add_child_links_to_families(self):
        "returns string of GraphViz edges linking parents to families or children"
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
                    self.add_family_link(p_id,family,frel,mrel)
                else:
                    # Link to the parents' nodes directly, if they are in graph
                    if father_handle and father_handle in person_dict:
                        self.add_parent_link(p_id,father_handle,frel)
                    if mother_handle and mother_handle in person_dict:
                        self.add_parent_link(p_id,mother_handle,mrel)

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
            (shape,style,color,fill) = self.get_gender_style(person)
            url = ""
            if self.includeurl:
                h = person_handle
                dirpath = "ppl/%s/%s" % (h[0], h[1])
                dirpath = dirpath.lower()
                url = "%s/%s.html" % (dirpath,h)
                
            self.doc.add_node(p_id,label,shape,color,style,fill)
  
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
                            if int(event.get_type()) == gen.lib.EventType.MARRIAGE:
                                label = self.get_event_string(event)
                                break
                        if self.includeid:
                            label = "%s (%s)" % (label, fam_id)
                        color = ""
                        fill = ""
                        style = ""
                        if self.colorize == 'colored':
                            color = self.colors['family']
                        elif self.colorize == 'filled':
                            fill = self.colors['family']
                            style = "filled"
                        self.doc.add_node(fam_id,label,"ellipse",color,style,fill)
                    # Link this person to all his/her families.
                    self.doc.add_link( fam_id, p_id, "", 
                                      self.arrowheadstyle, self.arrowtailstyle )

    def get_gender_style(self, person):
        "return gender specific person style"
        gender = person.get_gender()
        shape = "box"
        style = ""
        color = ""
        fill = ""
        if gender == person.MALE:
            shape="box"
        elif gender == person.FEMALE:
            shape="box"
            style="rounded"
        else:
            shape="hexagon"
        if self.colorize == 'colored':
            if gender == person.MALE:
                color = self.colors['male']
            elif gender == person.FEMALE:
                color = self.colors['female']
            else:
                color = self.colors['unknown']
        elif self.colorize == 'filled':
            if style != "":
                 style += ",filled"
            else:
                 style = "filled"
            if gender == person.MALE:
                fill = self.colors['male']
            elif gender == person.FEMALE:
                fill = self.colors['female']
            else:
                fill = self.colors['unknown']
        return(shape,style,color,fill)

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
                    imagePath = ThumbNails.get_thumbnail_path(media.get_path())
                    #test if thumbnail actually exists in thumbs (import of data means media files might not be present
                    imagePath = Utils.find_file(imagePath)

        label = u""
        lineDelimiter = '\\n'

        # If we have an image, then start an HTML table; remember to close the table afterwards!
        #
        # This isn't a free-form HTML format here...just a few keywords that happen to be
        # simillar to keywords commonly seen in HTML.  For additional information on what
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
            label += nm.replace('<','&#60;').replace('>','&#62;')
        else :
            label += nm
        p_id = person.get_gramps_id()
        if self.includeid:
            label += " (%s)" % p_id
        if self.includedates:
            birth, death = self.get_date_strings(person)
            label = label + '%s(%s - %s)' % (lineDelimiter,birth, death)
            
        # see if we have a table that needs to be terminated
        if self.bUseHtmlOutput:
            label += '</TD></TR></TABLE>'
            return label
        else :
            # non html label is enclosed by "" so excape other "
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
            if int(event.get_type()) == gen.lib.EventType.CHRISTEN:
                if not birth:
                    birth = self.get_event_string(event)
            elif int(event.get_type()) ==  gen.lib.EventType.BURIAL:
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
class RelGraphOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """
    def __init__(self,name,dbstate=None):
        MenuReportOptions.__init__(self,name,dbstate)
        
    def add_menu_options(self,menu,dbstate):
        ################################
        category_name = _("Report Options")
        ################################
        
        filter = FilterListOption(_("Filter"))
        filter.add_item("person")
        filter.set_help(_("Select the filter to be applied to the report"))
        menu.add_option(category_name,"filter", filter)
        
        incdate = BooleanOption(
                            _("Include Birth, Marriage and Death dates"), True)
        incdate.set_help(_("Include the dates that the individual was born, "
                           "got married and/or died in the graph labels."))
        menu.add_option(category_name,"incdate", incdate)
        
        justyears = BooleanOption(_("Limit dates to years only"), False)
        justyears.set_help(_("Prints just dates' year, neither "
                             "month or day nor date approximation "
                             "or interval are shown."))
        menu.add_option(category_name,"justyears", justyears)
        
        placecause = BooleanOption(_("Place/cause when no date"), True)
        placecause.set_help(_("When no birth, marriage, or death date is "
                              "available, the correspondent place field (or "
                              "cause field when blank place) will be used."))
        menu.add_option(category_name,"placecause", placecause)
        
        url = BooleanOption(_("Include URLs"), False)
        url.set_help(_("Include a URL in each graph node so "
                       "that PDF and imagemap files can be "
                       "generated that contain active links "
                       "to the files generated by the 'Narrated "
                       "Web Site' report."))
        menu.add_option(category_name,"url", url)
        
        incid = BooleanOption(_("Include IDs"), False)
        incid.set_help(_("Include individual and family IDs."))
        menu.add_option(category_name,"incid", incid)
        
        includeImages = BooleanOption(
                                 _('Include thumbnail images of people'), False)
        includeImages.set_help(_("Whether to include thumbnails of people."))
        menu.add_option(category_name,"includeImages", includeImages)
        
        imageOnTheSide = EnumeratedListOption(_("Thumbnail Location"), 0)
        imageOnTheSide.add_item(0, _('Above the name'))
        imageOnTheSide.add_item(1, _('Beside the name'))
        imageOnTheSide.set_help(_("Where the thumbnail image should appear "
                                  "relative to the name"))
        menu.add_option(category_name,"imageOnTheSide",imageOnTheSide)
        
        ################################
        category_name = _("Graph Style")
        ################################

        color = EnumeratedListOption(_("Graph coloring"), "filled")
        for i in range( 0, len(_COLORS) ):
            color.add_item(_COLORS[i]["value"], _COLORS[i]["name"])
        color.set_help(_("Males will be shown with blue, females "
                         "with red.  If the sex of an individual "
                         "is unknown it will be shown with gray."))
        menu.add_option(category_name,"color",color)
        
        arrow = EnumeratedListOption(_("Arrowhead direction"), 'd')
        for i in range( 0, len(_ARROWS) ):
            arrow.add_item(_ARROWS[i]["value"], _ARROWS[i]["name"])
        arrow.set_help(_("Choose the direction that the arrows point."))
        menu.add_option(category_name,"arrow",arrow)
        
        dashed = BooleanOption(
                  _("Indicate non-birth relationships with dotted lines"), True)
        dashed.set_help(_("Non-birth relationships will show up "
                          "as dotted lines in the graph."))
        menu.add_option(category_name,"dashed", dashed)
        
        showfamily = BooleanOption(_("Show family nodes"), True)
        showfamily.set_help(_("Families will show up as ellipses, linked "
                              "to parents and children."))
        menu.add_option(category_name,"showfamily", showfamily)
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'rel_graph',
    category = CATEGORY_GRAPHVIZ,
    report_class = RelGraphReport,
    options_class = RelGraphOptions,
    modes = MODE_GUI | MODE_CLI,
    translated_name = _("Relationship Graph"),
    status = _("Stable"),
    description = _("Generates a relationship graphs using Graphviz."),
    author_name ="Brian G. Matherly",
    author_email ="brian@gramps-project.org"
    )

