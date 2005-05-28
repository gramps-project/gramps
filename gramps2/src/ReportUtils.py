#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
#
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
# GRAMPS modules
#
#------------------------------------------------------------------------
import Date
import DateHandler
import RelLib
from NameDisplay import displayer as _nd
import time
from gettext import gettext as _

#-------------------------------------------------------------------------
#
#  Convert points to cm and back
#
#-------------------------------------------------------------------------
def pt2cm(pt):
    """
    Converts points to centimeters. Fonts are typically specified in points,
    but the BaseDoc classes use centimeters.

    @param pt: points
    @type pt: float or int
    @returns: equivalent units in centimeters
    @rtype: float
    """
    return pt/28.3465

def cm2pt(cm):
    """
    Converts centimeters to points. Fonts are typically specified in points,
    but the BaseDoc classes use centimeters.

    @param cm: centimeters
    @type cm: float or int
    @returns: equivalent units in points
    @rtype: float
    """
    return cm*182.88

def rgb_color(color):
    """
    Converts color value from 0-255 integer range into 0-1 float range.

    @param color: list or tuple of integer values for red, green, and blue
    @type color: int
    @returns: (r,g,b) tuple of floating point color values
    @rtype: 3-tuple
    """
    r = float(color[0])/255.0
    g = float(color[1])/255.0
    b = float(color[2])/255.0
    return (r,g,b)
        
def draw_pie_chart(doc, center_x, center_y, radius, data, start=0):
    """
    Draws a pie chart in the specified document. The data passed is plotted as
    a pie chart. The data should consist of the actual data. Percentages of
    each slice are determined by the routine.

    @param doc: Document to which the pie chart should be added
    @type doc: BaseDoc derived class
    @param center_x: x coordinate in centimeters where the center of the pie
       chart should be. 0 is the left hand edge of the document.
    @type center_x: float
    @param center_y: y coordinate in centimeters where the center of the pie
       chart should be. 0 is the top edge of the document
    @type center_y: float
    @param radius: radius of the pie chart. The pie charts width and height
       will be twice this value.
    @type radius: float
    @param data: List of tuples containing the data to be plotted. The values
       are (graphics_format, value), where graphics_format is a BaseDoc
       GraphicsStyle, and value is a floating point number. Any other items in
       the tuple are ignored. This allows you to share the same data list with
       the L{draw_legend} function.
    @type data: list
    @param start: starting point in degrees, where the default of 0 indicates
       a start point extending from the center to right in a horizontal line.
    @type start: float
    """

    total = 0.0
    for item in data:
        total += item[1]

    for item in data:
        incr = 360.0*(item[1]/total)
        doc.draw_wedge(item[0], center_x, center_y, radius, start, start + incr)
        start += incr

def draw_legend(doc, start_x, start_y, data):
    """
    Draws a legend for a graph in the specified document. The data passed is
    used to define the legend.

    @param doc: Document to which the legend chart should be added
    @type doc: BaseDoc derived class
    @param start_x: x coordinate in centimeters where the left hand corner
        of the legend is placed. 0 is the left hand edge of the document.
    @type start_x: float
    @param start_y: y coordinate in centimeters where the top of the legend
        should be. 0 is the top edge of the document
    @type start_y: float
    @param data: List of tuples containing the data to be used to create the
       legend. In order to be compatible with the graph plots, the first and
       third values of the tuple used. The format is (graphics_format, value,
       legend_description).
    @type data: list
    """
    for (format, size, legend) in data:
        gstyle = doc.get_draw_style(format)
        pstyle = gstyle.get_paragraph_style()
        size = pt2cm(doc.get_style(pstyle).get_font().get_size())
        
        doc.draw_bar(format, start_x, start_y, start_x + (2*size), start_y + size)
        doc.write_at(pstyle, legend, start_x + (3*size), start_y - (size*0.25))
        start_y += size * 1.3
        
def draw_vertical_bar_graph(doc, format, start_x, start_y, height, width, data):
    """
    Draws a vertical bar chart in the specified document. The data passed 
    should consist of the actual data. The bars are scaled appropriately by
    the routine.

    @param doc: Document to which the bar chart should be added
    @type doc: BaseDoc derived class
    @param start_x: x coordinate in centimeters where the left hand side of the
       chart should be. 0 is the left hand edge of the document.
    @type start_x: float
    @param start_y: y coordinate in centimeters where the top of the chart
    should be. 0 is the top edge of the document
    @type start_y: float
    @param height: height of the graph in centimeters
    @type height: float
    @param width: width of the graph in centimeters
    @type width: float
    @param data: List of tuples containing the data to be plotted. The values
       are (graphics_format, value), where graphics_format is a BaseDoc
       GraphicsStyle, and value is a floating point number. Any other items in
       the tuple are ignored. This allows you to share the same data list with
       the L{draw_legend} function.
    @type data: list
    """
    doc.draw_line(format,start_x,start_y+height,start_x,start_y)
    doc.draw_line(format,start_x,start_y+height,start_x+width,start_y+height)

    largest = 0.0
    for item in data:
        largest = max(item[1],largest)

    scale = float(height)/float(largest)
    units = len(data)
    box_width = (float(width) / (units*3.0+1.0))*2

    bottom = float(start_y)+float(height)

    start = 0.5*box_width + start_x
    for index in range(units):
        size = float(data[index][1]) * scale
        doc.draw_bar(data[index][0],start,bottom-size,start+box_width,bottom)
        start += box_width * 1.5


_t = time.localtime(time.time())
_TODAY = DateHandler.parser.parse("%04d-%02d-%02d" % (_t[0],_t[1],_t[2]))

def estimate_age(db, person, end_handle=None, start_handle=None):
    """
    Estimates the age of a person based off the birth and death
    dates of the person. A tuple containing the estimated upper
    and lower bounds of the person's age is returned. If either
    the birth or death date is missing, a (-1,-1) is returned.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param person: Person object to calculate the age of
    @type person: Person
    @param end_handle: Determines the event handle that determines
       the upper limit of the age. If None, the death event is used
    @type end_handle: str
    @param start_handle: Determines the event handle that determines
       the lower limit of the event. If None, the birth event is
       used
    @type start_handle: str
    @returns: tuple containing the lower and upper bounds of the
       person's age, or (-1,-1) if it could not be determined.
    @rtype: tuple
    """

    if start_handle:
        bhandle = start_handle
    else:
        bhandle = person.get_birth_handle()

    if end_handle:
        dhandle = end_handle
    else:
        dhandle = person.get_death_handle()

    # if either of the events is not defined, return an error message
    if not bhandle:
        return (-1,-1)

    bdata = db.get_event_from_handle(bhandle).get_date_object()
    if dhandle:
        ddata = db.get_event_from_handle(dhandle).get_date_object()
    else:
        ddata = _TODAY

    # if the date is not valid, return an error message
    if not bdata.get_valid() or not ddata.get_valid():
        return (-1,-1)

    # if a year is not valid, return an error message
    if not bdata.get_year_valid() or not ddata.get_year_valid():
        return (-1,-1)

    bstart = bdata.get_start_date()
    bstop  = bdata.get_stop_date()

    dstart = ddata.get_start_date()
    dstop  = ddata.get_stop_date()

    def _calc_diff(low,high):
        if (low[1],low[0]) > (high[1],high[0]):
            return high[2] - low[2] - 1
        else:
            return high[2] - low[2]

    if bstop == Date.EMPTY and dstop == Date.EMPTY:
        lower = _calc_diff(bstart,dstart)
        age = (lower, lower)
    elif bstop == Date.EMPTY:
        lower = _calc_diff(bstart,dstart)
        upper = _calc_diff(bstart,dstop)
        age = (lower,upper)
    elif dstop == Date.EMPTY:
        lower = _calc_diff(bstop,dstart)
        upper = _calc_diff(bstart,dstart)
        age = (lower,upper)
    else:
        lower = _calc_diff(bstop,dstart)
        upper = _calc_diff(bstart,dstop)
        age = (lower,upper)
    return age

def sanitize_person(db,person):
    """
    Creates a new Person instance based off the passed Person
    instance. The returned instance has all private records
    removed from it.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param person: source Person object that will be copied with
    privacy records removed
    @type person: Person
    @returns: 'cleansed' Person object
    @rtype: Person
    """
    new_person = RelLib.Person()

    # copy gender
    new_person.set_gender(person.get_gender())
    new_person.set_gramps_id(person.get_gramps_id())
    new_person.set_handle(person.get_handle())
    
    # copy names if not private
    name = person.get_primary_name()
    if name.get_privacy() or person.get_privacy():
        name = RelLib.Name()
        name.set_first_name(_('Private'))
        name.set_surname(_('Private'))
    else:
        new_person.set_nick_name(person.get_nick_name())

    new_person.set_primary_name(name)
    # copy Family reference list
    for handle in person.get_family_handle_list():
        new_person.add_family_handle(handle)

    # copy Family reference list
    for item in person.get_parent_family_handle_list():
        new_person.add_parent_family_handle(item[0],item[1],item[2])


    if person.get_privacy():
        return new_person

    for name in person.get_alternate_names():
        if not name.get_privacy():
            new_person.add_alternate_name(name)

    # set complete flag
    new_person.set_complete_flag(person.get_complete_flag())

    # copy birth event
    event_handle = person.get_birth_handle()
    event = db.get_event_from_handle(event_handle)
    if event and not event.get_privacy():
        new_person.set_birth_handle(event_handle)

    # copy death event
    event_handle = person.get_death_handle()
    event = db.get_event_from_handle(event_handle)
    if event and not event.get_privacy():
        new_person.set_death_handle(event_handle)

    # copy event list
    for event_handle in person.get_event_list():
        event = db.get_event_from_handle(event_handle)
        if event and not event.get_privacy():
            new_person.add_event_handle(event_handle)

    # copy address list
    for address in person.get_address_list():
        if not address.get_privacy():
            new_person.add_address(RelLib.Address(address))

    # copy attribute list
    for attribute in person.get_attribute_list():
        if not attribute.get_privacy():
            new_person.add_attribute(RelLib.Attribute(attribute))

    # copy URL list
    for url in person.get_url_list():
        if not url.get_privacy():
            new_person.add_url(url)

    # copy Media reference list
    for obj in person.get_media_list():
        new_person.add_media_reference(RelLib.MediaRef(obj))

    # LDS ordinances
    ordinance = person.get_lds_baptism()
    if ordinance:
        new_person.set_lds_baptism(ordinance)

    ordinance = person.get_lds_endowment()
    if ordinance:
        new_person.set_lds_endowment(ordinance)

    ordinance = person.get_lds_sealing()
    if ordinance:
        new_person.set_lds_sealing(ordinance)
    
    return new_person

#-------------------------------------------------------------------------
#
#  Roman numbers
#
#-------------------------------------------------------------------------
def roman(num):
    """ Integer to Roman numeral converter for 0 < num < 4000 """
    if type(num) != int:
        return "?"
    if not 0 < num < 4000:
        return "?"
    vals = (1000, 900, 500, 400, 100,  90,  50,  40,  10,   9,   5,   4,   1)
    nums = ( 'M','CM', 'D','CD', 'C','XC', 'L','XL', 'X','IX', 'V','IV', 'I')
    retval = ""
    for i in range(len(vals)):
        amount  = int(num / vals[i])
        retval += nums[i] * amount
        num    -= vals[i] * amount
    return retval

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def place_name(db,place_handle):
    if place_handle:
        place = db.get_place_from_handle(place_handle).get_title()
    else:
        place = ""
    
#-------------------------------------------------------------------------
#
# Functions commonly used in reports
#
#-------------------------------------------------------------------------
def insert_images(database, doc, person, w_cm=4.0, h_cm=4.0):
    """
    Insert pictures of a person into the document.
    """

    photos = person.get_media_list()
    for photo in photos :
        object_handle = photo.get_reference_handle()
        media_object = database.get_object_from_handle(object_handle)
        mime_type = media_object.get_mime_type()
        if mime_type and mime_type.startswith("image"):
            filename = media_object.get_path()
            doc.add_media_object(filename,"row",w_cm,h_cm)

#-------------------------------------------------------------------------
#
# Strings commonly used in reports
#
#-------------------------------------------------------------------------
def empty_notes(whatever):
    # Empty stab function for when endnotes are not needed
    return ""

def get_birth_death_strings(database,person,empty_date="",empty_place=""):
    """
    Returns strings for dates and places of birth and death.
    """

    bplace = dplace = empty_place
    bdate = ddate = empty_date
    bdate_full = ddate_full = False

    birth_handle = person.get_birth_handle()
    if birth_handle:
        birth = database.get_event_from_handle(birth_handle)
        bdate = birth.get_date()
        bplace_handle = birth.get_place_handle()
        if bplace_handle:
            bplace = database.get_place_from_handle(bplace_handle).get_title()
        bdate_obj = birth.get_date_object()
        bdate_full = bdate_obj and bdate_obj.get_day_valid()

    death_handle = person.get_death_handle()
    if death_handle:
        death = database.get_event_from_handle(death_handle)
        ddate = death.get_date()
        dplace_handle = death.get_place_handle()
        if dplace_handle:
            dplace = database.get_place_from_handle(dplace_handle).get_title()
        ddate_obj = death.get_date_object()
        ddate_full = ddate_obj and ddate_obj.get_day_valid()

    return (bdate,bplace,bdate_full,ddate,dplace,ddate_full)

def born_died_str(database,person,endnotes=None,name_object=None,person_name=None):
    """
    Composes a string describing birth and death of a person.
    
    The string is composed in the following form:
        "Such-and-such was born on-a-date in a-place, 
        and died on-a-date in a-place"
    Missing information will be omitted without loss of readability.
    Optional references may be added to birth and death events.
    Optional Name object may be used to override a person's Name instance.
    Optional string may be used to override the string representation of a name.
    
    @param database GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param person: Person instance for which the string has to be composed
    @type person: Person
    @param endnotes: Function to use for reference composition. If None
    then references will not be added
    @type endnotes: function
    @param name_object: Name instance for which the phrase is composed. If None
    then the regular primary name of the person will be used
    @type name_object: Name
    @param person_name: String to override the person's name. If None then the
    regular primary name string will be used
    @type person_name: unicode
    @returns: A composed string
    @rtype: unicode
    """

    if not endnotes:
        endnotes = empty_notes

    if not name_object:
        name_object = person.get_primary_name()

    if person_name == None:
        person_name = _nd.display_name(name_object)
    elif person_name == 0:
        if person.get_gender() == const.MALE:
            person_name = _('He')
        else:
            person_name = _('She')

    bdate,bplace,bdate_full,ddate,dplace,ddate_full = \
                            get_birth_death_strings(database,person)

    birth = database.get_event_from_handle(person.get_birth_handle())
    death = database.get_event_from_handle(person.get_death_handle())

    if person.get_gender() == const.MALE:
        if bdate:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace,
                        'death_date' : ddate,'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace, 'death_date' : ddate,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace, 'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace,
                        'birth_endnotes' : endnotes(birth) }
            else:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 
                        'death_date' : ddate,'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'death_date' : ddate,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_endnotes' : endnotes(birth) }
        else:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace,
                        'death_date' : ddate,'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace, 'death_date' : ddate,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace, 'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace,
                        'birth_endnotes' : endnotes(birth) }
            else:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'death_date' : ddate, 'death_place' : dplace,
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "died %(death_date)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'death_date' : ddate,
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "died in %(death_place)s%(death_endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object),
                        'death_place' : dplace,
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(male_name)s%(endnotes)s.") % {
                        'male_name' : person_name, 'endnotes' : endnotes(name_object) }
    else:
        if bdate:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace,
                        'death_date' : ddate,'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace, 'death_date' : ddate,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace, 'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_place' : bplace,
                        'birth_endnotes' : endnotes(birth) }
            else:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 
                        'death_date' : ddate,'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'death_date' : ddate,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_date' : bdate, 'birth_endnotes' : endnotes(birth) }
        else:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace,
                        'death_date' : ddate,'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace, 'death_date' : ddate,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace, 'death_place' : dplace,
                        'birth_endnotes' : endnotes(birth), 
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'birth_place' : bplace,
                        'birth_endnotes' : endnotes(birth) }
            else:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'death_date' : ddate, 'death_place' : dplace,
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "died %(death_date)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'death_date' : ddate,
                        'death_endnotes' : endnotes(death) }
                else:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "died in %(death_place)s%(death_endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object),
                        'death_place' : dplace,
                        'death_endnotes' : endnotes(death) }
                    else:
                        text = _("%(female_name)s%(endnotes)s.") % {
                        'female_name' : person_name, 'endnotes' : endnotes(name_object) }
    if text:
        text = text + " "
    return text

def married_str(database,person,spouse,event,endnotes=None,
                                empty_date="",empty_place="",is_first=True):
    """
    Composes a string describing marriage of a person.
    
    The string is composed in the following form:
        "He/She married such-and-such on-a-date" or 
        "He/She married such-and-such in a-place", 
    Missing information will be omitted without loss of readability.
    Optional references may be added to birth and death events.
    
    @param database GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param person: Person instance whose marriage is discussed
    @type person: Person
    @param spouse: Person instance to use as a spouse
    @type spouse: Person
    @param event: Event instance of marriage 
    @type event: Event
    @param endnotes: Function to use for reference composition. If None
    then references will not be added
    @type endnotes: function
    @returns: A composed string
    @rtype: unicode
    """

    # not all families have a spouse.
    if not spouse:
        return u""

    if not endnotes:
        endnotes = empty_notes

    date = empty_date
    place = empty_place
    spouse_name = _nd.display(spouse)

    mdate = event.get_date()
    if mdate:
        date = mdate
    place_handle = event.get_place_handle()
    if place_handle:
        place = database.get_place_from_handle(place_handle).get_title()

    text = ""
    if is_first:
        if date and place:
            if person.get_gender() == const.MALE:
                    text = _('He married %(spouse)s %(date)s in %(place)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'endnotes' : endnotes(event),
                        'date' : date,
                        'place' : place}
            else:
                    text = _('She married %(spouse)s %(date)s in %(place)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'date' : date,
                        'endnotes' : endnotes(event),
                        'place' : place}
        elif date:
            if person.get_gender() == const.MALE:
                    text = _('He married %(spouse)s %(date)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'endnotes' : endnotes(event),
                        'date' : date,}
            else:
                    text = _('She married %(spouse)s in %(place)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'endnotes' : endnotes(event),
                        'place' : place,}
        elif place:
            if person.get_gender() == const.MALE:
                    text = _('He married %(spouse)s in %(place)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'endnotes' : endnotes(event),
                        'place' : place}
            else:
                    text = _('She married %(spouse)s in %(place)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'endnotes' : endnotes(event),
                        'place' : place}
        else:
            if person.get_gender() == const.MALE:
                    text = _('He married %(spouse)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'endnotes' : endnotes(event) }
            else:
                    text = _('She married %(spouse)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'endnotes' : endnotes(event)}
    else:
        if date and place:
            if person.get_gender() == const.MALE:
                    text = _('He also married %(spouse)s %(date)s in %(place)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'endnotes' : endnotes(event),
                        'date' : date,
                        'place' : place}
            else:
                    text = _('She also married %(spouse)s %(date)s in %(place)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'date' : date,
                        'endnotes' : endnotes(event),
                        'place' : place}
        elif date:
            if person.get_gender() == const.MALE:
                    text = _('He also married %(spouse)s %(date)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'endnotes' : endnotes(event),
                        'date' : date,}
            else:
                    text = _('She also married %(spouse)s in %(place)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'endnotes' : endnotes(event),
                        'place' : place,}
        elif place:
            if person.get_gender() == const.MALE:
                    text = _('He also married %(spouse)s in %(place)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'endnotes' : endnotes(event),
                        'place' : place}
            else:
                    text = _('She also married %(spouse)s in %(place)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'endnotes' : endnotes(event),
                        'place' : place}
        else:
            if person.get_gender() == const.MALE:
                    text = _('He also married %(spouse)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'endnotes' : endnotes(event) }
            else:
                    text = _('She also married %(spouse)s%(endnotes)s.') % {
                        'spouse' : spouse_name,
                        'endnotes' : endnotes(event)}

    if text:
        text = text + " "
    return text

def married_rel_str(database,person,family,is_first=True):
    spouse_handle = find_spouse(person,family)
    spouse = database.get_person_from_handle(spouse_handle)

    # not all families have a spouse.
    if not spouse_handle or not spouse:
        return u""

    spouse_name = _nd.display(spouse)

    if is_first:
        if family.get_relationship() == const.FAMILY_MARRIED:
            if person.get_gender() == const.MALE:
                text = _('He married %(spouse)s.') % { 'spouse' : spouse_name }
            else:
                text = _('She married %(spouse)s.') % { 'spouse' : spouse_name }
        else:
            if person.get_gender() == const.MALE:
                text = _('He had relationship with %(spouse)s.') % { 
                            'spouse' : spouse_name }
            else:
                text = _('She had relationship with %(spouse)s.') % { 
                            'spouse' : spouse_name }
    else:
        if family.get_relationship() == const.FAMILY_MARRIED:
            if person.get_gender() == const.MALE:
                text = _('He also married %(spouse)s.') % { 'spouse' : spouse_name }
            else:
                text = _('She also married %(spouse)s.') % { 'spouse' : spouse_name }
        else:
            if person.get_gender() == const.MALE:
                text = _('He also had relationship with %(spouse)s.') % { 
                            'spouse' : spouse_name }
            else:
                text = _('She also had relationship with %(spouse)s.') % { 
                            'spouse' : spouse_name }
    if text:
        text = text + " "
    return text

def child_str(person,father_name="",mother_name="",dead=0):
    """
    Composes a string describing person being a child.
    
    The string is composed in the following form:
        "He/She is/was the son/daughter of father_name and mother_name"
    Missing information will be omitted without loss of readability.
    
    @param person_gender: Person.MALE, Person.FEMALE, or Person.UNKNOWN
    @type person: Person.MALE, Person.FEMALE, or Person.UNKNOWN~
    @param father_name: String to use for father's name
    @type father_name: unicode
    @param mother_name: String to use for mother's name
    @type mother_name: unicode
    @param dead: Whether the person discussed is dead or not
    @type dead: bool
    @returns: A composed string
    @rtype: unicode
    """
    
    text = ""

    if person.get_gender() == const.MALE:
        if mother_name and father_name:
            if dead:
                text = _("He was the son of %(father)s and %(mother)s.") % {
                    'father' : father_name,
                    'mother' : mother_name, }
            else:
                text = _("He is the son of %(father)s and %(mother)s.") % {
                    'father' : father_name,
                    'mother' : mother_name, }
        elif mother_name:
            if dead:
                text = _("He was the son of %(mother)s.") % {
                    'mother' : mother_name, }
            else:
                text = _("He is the son of %(mother)s.") % {
                    'mother' : mother_name, }
        elif father_name:
            if dead:
                text = _("He was the son of %(father)s.") % {
                    'father' : father_name, }
            else:
                text = _("He is the son of %(father)s.") % {
                    'father' : father_name, }
    else:
        if mother_name and father_name:
            if dead:
                text = _("She was the daughter of %(father)s and %(mother)s.") % {
                    'father' : father_name,
                    'mother' : mother_name, }
            else:
                text = _("She is the daughter of %(father)s and %(mother)s.") % {
                    'father' : father_name,
                    'mother' : mother_name, }
        elif mother_name:
            if dead:
                text = _("She was the daughter of %(mother)s.") % {
                    'mother' : mother_name, }
            else:
                text = _("She is the daughter of %(mother)s.") % {
                    'mother' : mother_name, }
        elif father_name:
            if dead:
                text = _("She was the daughter of %(father)s.") % {
                    'father' : father_name, }
            else:
                text = _("She is the daughter of %(father)s.") % {
                    'father' : father_name, }
    if text:
        text = text + " "
    return text

def find_spouse(person,family):
    if person.get_handle() == family.get_father_handle():
        spouse_handle = family.get_mother_handle()
    else:
        spouse_handle = family.get_father_handle()
    return spouse_handle

def find_marriage(database,family):    
    for event_handle in family.get_event_list():
        event = database.get_event_from_handle(event_handle)
        if event and event.get_name() == "Marriage":
            return event
    return None

def born_str(database,person,person_name=None,empty_date="",empty_place=""):
    """ 
    Check birth record.
    Statement formats name precedes this
        was born on Date.
        was born on Date in Place.
        was born in Month_Year.
        was born in Month_Year in Place.
        was born in Place.
        ''
    """

    if person_name == None:
        person_name = _nd.display_name(person.get_primary_name())
    elif person_name == 0:
        if person.get_gender() == const.MALE:
            person_name = _('He')
        else:
            person_name = _('She')

    text = ""
    
    bdate,bplace,bdate_full,ddate,dplace,ddate_full = \
                get_birth_death_strings(database,person,empty_date,empty_place)

    if person.get_gender() == const.MALE:
        if bdate and bdate_full:
            if bplace: #male, date, place
                text = _("%(male_name)s "
                        "was born on %(birth_date)s in %(birth_place)s.") % {
                    'male_name' : person_name, 
                    'birth_date' : bdate, 'birth_place' : bplace }
            else: #male, date, no place
                text = _("%(male_name)s was born on %(birth_date)s.") % {
                    'male_name' : person_name, 'birth_date' : bdate }
        elif bdate:
            if bplace: #male, month_year, place
                text = _("%(male_name)s "
                        "was born in %(month_year)s in %(birth_place)s.") % {
                    'male_name' : person_name, 
                    'month_year' : bdate, 'birth_place' : bplace }
            else: #male, month_year, no place
                text = _("%(male_name)s was born in %(month_year)s.") % {
                    'male_name' : person_name, 'month_year' : bdate }
        else:
            if bplace: #male, no date, place
                text = _("%(male_name)s was born in %(birth_place)s.") % {
                    'male_name' : person_name, 'birth_place' : bplace }
            else: #male, no date, no place
                text = person_name
    else:
        if bdate and bdate_full:
            if bplace: #female, date, place
                text = _("%(female_name)s "
                        "was born on %(birth_date)s in %(birth_place)s.") % {
                    'female_name' : person_name, 
                    'birth_date' : bdate, 'birth_place' : bplace }
            else: #female, date, no place
                text = _("%(female_name)s was born on %(birth_date)s.") % {
                    'female_name' : person_name, 'birth_date' : bdate }
        elif bdate:
            if bplace: #female, month_year, place
                text = _("%(female_name)s "
                        "was born in %(month_year)s in %(birth_place)s.") % {
                    'female_name' : person_name, 
                    'month_year' : bdate, 'birth_place' : bplace }
            else: #female, month_year, no place
                text = _("%(female_name)s was born in %(month_year)s.") % {
                    'female_name' : person_name, 'month_year' : bdate }
        else:
            if bplace: #female, no date, place
                text = _("%(female_name)s was born in %(birth_place)s.") % {
                    'female_name' : person_name, 'birth_place' : bplace }
            else: #female, no date, no place
                text = person_name

    if text:
        text = text + " "
    return text

def died_str(database,person,person_name=None,empty_date="",empty_place="",
                            age=None,age_units=0):
    """
    Write obit sentence.
        FIRSTNAME died on Date
        FIRSTNAME died on Date at the age of N Years
        FIRSTNAME died on Date at the age of N Months
        FIRSTNAME died on Date at the age of N Days
        FIRSTNAME died on Date in Place
        FIRSTNAME died on Date in Place at the age of N Years
        FIRSTNAME died on Date in Place at the age of N Months
        FIRSTNAME died on Date in Place at the age of N Days
        FIRSTNAME died in Month_Year
        FIRSTNAME died in Month_Year at the age of N Years
        FIRSTNAME died in Month_Year at the age of N Months
        FIRSTNAME died in Month_Year at the age of N Days
        FIRSTNAME died in Month_Year in Place
        FIRSTNAME died in Month_Year in Place at the age of N Years
        FIRSTNAME died in Month_Year in Place at the age of N Months
        FIRSTNAME died in Month_Year in Place at the age of N Days
        FIRSTNAME died in Place
        FIRSTNAME died in Place at the age of N Years
        FIRSTNAME died in Place at the age of N Months
        FIRSTNAME died in Place at the age of N Days
        FIRSTNAME died
        FIRSTNAME died at the age of N Years
        FIRSTNAME died at the age of N Months
        FIRSTNAME died at the age of N Days
    """

    if person_name == None:
        person_name = _nd.display_name(person.get_primary_name())
    elif person_name == 0:
        if person.get_gender() == const.MALE:
            person_name = _('He')
        else:
            person_name = _('She')

    text = ""

    bdate,bplace,bdate_full,ddate,dplace,ddate_full = \
                get_birth_death_strings(database,person,empty_date,empty_place)

    if person.get_gender() == const.MALE:
        if ddate and ddate_full:
            if dplace: 
                if not age_units: #male, date, place, no age
                    text = _("%(male_name)s "
                            "died on %(death_date)s in %(death_place)s.") % {
                    'male_name' : person_name, 
                    'death_date' : ddate, 'death_place' : dplace }
                elif age_units == 1: #male, date, place, years
                    text = _("%(male_name)s "
                            "died on %(death_date)s in %(death_place)s "
                            "at the age of %(age)d years.") % {
                    'male_name' : person_name, 
                    'death_date' : ddate, 'death_place' : dplace,
                    'age' : age }
                elif age_units == 2: #male, date, place, months
                    text = _("%(male_name)s "
                            "died on %(death_date)s in %(death_place)s "
                            "at the age of %(age)d months.") % {
                    'male_name' : person_name, 
                    'death_date' : ddate, 'death_place' : dplace,
                    'age' : age }
                elif age_units == 3: #male, date, place, days
                    text = _("%(male_name)s "
                            "died on %(death_date)s in %(death_place)s "
                            "at the age of %(age)d days.") % {
                    'male_name' : person_name, 
                    'death_date' : ddate, 'death_place' : dplace,
                    'age' : age }
            else:
                if not age_units: #male, date, no place, no age
                    text = _("%(male_name)s died on %(death_date)s.") % {
                    'male_name' : person_name, 'death_date' : ddate }
                elif age_units == 1: #male, date, no place, years
                    text = _("%(male_name)s died on %(death_date)s "
                            "at the age of %(age)d years.") % {
                    'male_name' : person_name, 
                    'death_date' : ddate, 'age' : age }
                elif age_units == 2: #male, date, no place, months
                    text = _("%(male_name)s died on %(death_date)s "
                            "at the age of %(age)d months.") % {
                    'male_name' : person_name, 
                    'death_date' : ddate, 'age' : age }
                elif age_units == 3: #male, date, no place, days
                    text = _("%(male_name)s died on %(death_date)s "
                            "at the age of %(age)d days.") % {
                    'male_name' : person_name, 
                    'death_date' : ddate, 'age' : age }
        elif ddate:
            if dplace: 
                if not age_units: #male, month_year, place, no age
                    text = _("%(male_name)s "
                            "died in %(month_year)s in %(death_place)s.") % {
                    'male_name' : person_name, 
                    'month_year' : ddate, 'death_place' : dplace }
                elif age_units == 1: #male, month_year, place, years
                    text = _("%(male_name)s "
                            "died in %(month_year)s in %(death_place)s "
                            "at the age of %(age)d years.") % {
                    'male_name' : person_name, 
                    'month_year' : ddate, 'death_place' : dplace,
                    'age' : age }
                elif age_units == 2: #male, month_year, place, months
                    text = _("%(male_name)s "
                            "died in %(month_year)s in %(death_place)s "
                            "at the age of %(age)d months.") % {
                    'male_name' : person_name, 
                    'month_year' : ddate, 'death_place' : dplace,
                    'age' : age }
                elif age_units == 3: #male, month_year, place, days
                    text = _("%(male_name)s "
                            "died in %(month_year)s in %(death_place)s "
                            "at the age of %(age)d days.") % {
                    'male_name' : person_name, 
                    'month_year' : ddate, 'death_place' : dplace,
                    'age' : age }
            else:
                if not age_units: #male, month_year, no place, no age
                    text = _("%(male_name)s died in %(month_year)s.") % {
                    'male_name' : person_name, 'month_year' : ddate }
                elif age_units == 1: #male, month_year, no place, years
                    text = _("%(male_name)s died in %(month_year)s "
                            "at the age of %(age)d years.") % {
                    'male_name' : person_name, 
                    'month_year' : ddate, 'age' : age }
                elif age_units == 2: #male, month_year, no place, months
                    text = _("%(male_name)s died in %(month_year)s "
                            "at the age of %(age)d months.") % {
                    'male_name' : person_name, 
                    'month_year' : ddate, 'age' : age }
                elif age_units == 3: #male, month_year, no place, days
                    text = _("%(male_name)s died in %(month_year)s "
                            "at the age of %(age)d days.") % {
                    'male_name' : person_name, 
                    'month_year' : ddate, 'age' : age }
        else:
            if dplace: 
                if not age_units: #male, no date, place, no age
                    text = _("%(male_name)s died in %(death_place)s.") % {
                    'male_name' : person_name, 'death_place' : dplace }
                elif age_units == 1: #male, no date, place, years
                    text = _("%(male_name)s died in %(death_place)s "
                            "at the age of %(age)d years.") % {
                    'male_name' : person_name, 'death_place' : dplace,
                    'age' : age }
                elif age_units == 2: #male, no date, place, months
                    text = _("%(male_name)s died in %(death_place)s "
                            "at the age of %(age)d months.") % {
                    'male_name' : person_name, 'death_place' : dplace,
                    'age' : age }
                elif age_units == 3: #male, no date, place, days
                    text = _("%(male_name)s died in %(death_place)s "
                            "at the age of %(age)d days.") % {
                    'male_name' : person_name, 'death_place' : dplace,
                    'age' : age }
            else:
                if not age_units: #male, no date, no place, no age
                    pass    #text = _("%(male_name)s died.") % {
                            #'male_name' : person_name }
                elif age_units == 1: #male, no date, no place, years
                    text = _("%(male_name)s died "
                            "at the age of %(age)d years.") % {
                    'male_name' : person_name, 'age' : age }
                elif age_units == 2: #male, no date, no place, months
                    passtext = _("%(male_name)s died "
                            "at the age of %(age)d months.") % {
                    'male_name' : person_name, 'age' : age }
                elif age_units == 3: #male, no date, no place, days
                    text = _("%(male_name)s died "
                            "at the age of %(age)d days.") % {
                    'male_name' : person_name, 'age' : age }
    else:
        if ddate and ddate_full:
            if dplace: 
                if not age_units: #female, date, place, no age
                    text = _("%(female_name)s "
                            "died on %(death_date)s in %(death_place)s.") % {
                    'female_name' : person_name, 
                    'death_date' : ddate, 'death_place' : dplace }
                elif age_units == 1: #female, date, place, years
                    text = _("%(female_name)s "
                            "died on %(death_date)s in %(death_place)s "
                            "at the age of %(age)d years.") % {
                    'female_name' : person_name, 
                    'death_date' : ddate, 'death_place' : dplace,
                    'age' : age }
                elif age_units == 2: #female, date, place, months
                    text = _("%(female_name)s "
                            "died on %(death_date)s in %(death_place)s "
                            "at the age of %(age)d months.") % {
                    'female_name' : person_name, 
                    'death_date' : ddate, 'death_place' : dplace,
                    'age' : age }
                elif age_units == 3: #female, date, place, days
                    text = _("%(female_name)s "
                            "died on %(death_date)s in %(death_place)s "
                            "at the age of %(age)d days.") % {
                    'female_name' : person_name, 
                    'death_date' : ddate, 'death_place' : dplace,
                    'age' : age }
            else:
                if not age_units: #female, date, no place, no age
                    text = _("%(female_name)s died on %(death_date)s.") % {
                    'female_name' : person_name, 'death_date' : ddate }
                elif age_units == 1: #female, date, no place, years
                    text = _("%(female_name)s died on %(death_date)s "
                            "at the age of %(age)d years.") % {
                    'female_name' : person_name, 
                    'death_date' : ddate, 'age' : age }
                elif age_units == 2: #female, date, no place, months
                    text = _("%(female_name)s died on %(death_date)s "
                            "at the age of %(age)d months.") % {
                    'female_name' : person_name, 
                    'death_date' : ddate, 'age' : age }
                elif age_units == 3: #female, date, no place, days
                    text = _("%(female_name)s died on %(death_date)s "
                            "at the age of %(age)d days.") % {
                    'female_name' : person_name, 
                    'death_date' : ddate, 'age' : age }
        elif ddate:
            if dplace: 
                if not age_units: #female, month_year, place, no age
                    text = _("%(female_name)s "
                            "died in %(month_year)s in %(death_place)s.") % {
                    'female_name' : person_name, 
                    'month_year' : ddate, 'death_place' : dplace }
                elif age_units == 1: #female, month_year, place, years
                    text = _("%(female_name)s "
                            "died in %(month_year)s in %(death_place)s "
                            "at the age of %(age)d years.") % {
                    'female_name' : person_name, 
                    'month_year' : ddate, 'death_place' : dplace,
                    'age' : age }
                elif age_units == 2: #female, month_year, place, months
                    text = _("%(female_name)s "
                            "died in %(month_year)s in %(death_place)s "
                            "at the age of %(age)d months.") % {
                    'female_name' : person_name, 
                    'month_year' : ddate, 'death_place' : dplace,
                    'age' : age }
                elif age_units == 3: #female, month_year, place, days
                    text = _("%(female_name)s "
                            "died in %(month_year)s in %(death_place)s "
                            "at the age of %(age)d days.") % {
                    'female_name' : person_name, 
                    'month_year' : ddate, 'death_place' : dplace,
                    'age' : age }
            else:
                if not age_units: #female, month_year, no place, no age
                    text = _("%(female_name)s died in %(month_year)s.") % {
                    'female_name' : person_name, 'month_year' : ddate }
                elif age_units == 1: #female, month_year, no place, years
                    text = _("%(female_name)s died in %(month_year)s "
                            "at the age of %(age)d years.") % {
                    'female_name' : person_name, 
                    'month_year' : ddate, 'age' : age }
                elif age_units == 2: #female, month_year, no place, months
                    text = _("%(female_name)s died in %(month_year)s "
                            "at the age of %(age)d months.") % {
                    'female_name' : person_name, 
                    'month_year' : ddate, 'age' : age }
                elif age_units == 3: #female, month_year, no place, days
                    text = _("%(female_name)s died in %(month_year)s "
                            "at the age of %(age)d days.") % {
                    'female_name' : person_name, 
                    'month_year' : ddate, 'age' : age }
        else:
            if dplace: 
                if not age_units: #female, no date, place, no age
                    text = _("%(female_name)s died in %(death_place)s.") % {
                    'female_name' : person_name, 'death_place' : dplace }
                elif age_units == 1: #female, no date, place, years
                    text = _("%(female_name)s died in %(death_place)s "
                            "at the age of %(age)d years.") % {
                    'female_name' : person_name, 'death_place' : dplace,
                    'age' : age }
                elif age_units == 2: #female, no date, place, months
                    text = _("%(female_name)s died in %(death_place)s "
                            "at the age of %(age)d months.") % {
                    'female_name' : person_name, 'death_place' : dplace,
                    'age' : age }
                elif age_units == 3: #female, no date, place, days
                    text = _("%(female_name)s died in %(death_place)s "
                            "at the age of %(age)d days.") % {
                    'female_name' : person_name, 'death_place' : dplace,
                    'age' : age }
            else:
                if not age_units: #female, no date, no place, no age
                    pass    #text = _("%(female_name)s died.") % {
                            #'female_name' : person_name }
                elif age_units == 1: #female, no date, no place, years
                    text = _("%(female_name)s died "
                            "at the age of %(age)d years.") % {
                    'female_name' : person_name, 'age' : age }
                elif age_units == 2: #female, no date, no place, months
                    text = _("%(female_name)s died "
                            "at the age of %(age)d months.") % {
                    'female_name' : person_name, 'age' : age }
                elif age_units == 3: #female, no date, no place, days
                    text = _("%(female_name)s died "
                            "at the age of %(age)d days.") % {
                    'female_name' : person_name, 'age' : age }
    if text:
        text = text + " "
    return text

def buried_str(database,person,person_name=None,empty_date="",empty_place=""):
    """ 
    Check burial record.
    Statement formats name precedes this
        was buried on Date.
        was buried on Date in Place.
        was buried in Month_Year.
        was buried in Month_Year in Place.
        was buried in Place.
        ''
    """

    if person_name == None:
        person_name = _nd.display_name(person.get_primary_name())
    elif person_name == 0:
        if person.get_gender() == const.MALE:
            person_name = _('He')
        else:
            person_name = _('She')

    text = ""
    
    bplace = dplace = empty_place
    bdate = ddate = empty_date
    bdate_full = False

    burial = None
    for event_handle in person.get_event_list():
        event = database.get_event_from_handle(event_handle)
        if event and event.get_name() == "Burial":
            burial = event
            break

    if burial:
        bdate = burial.get_date()
        bplace_handle = burial.get_place_handle()
        if bplace_handle:
            bplace = database.get_place_from_handle(bplace_handle).get_title()
        bdate_obj = burial.get_date_object()
        bdate_full = bdate_obj and bdate_obj.get_day_valid()
    else:
        return text

    if person.get_gender() == const.MALE:
        if bdate and bdate_full:
            if bplace: #male, date, place
                text = _("%(male_name)s "
                        "was buried on %(burial_date)s in %(burial_place)s.") % {
                    'male_name' : person_name, 
                    'burial_date' : bdate, 'burial_place' : bplace }
            else: #male, date, no place
                text = _("%(male_name)s was buried on %(burial_date)s.") % {
                    'male_name' : person_name, 'burial_date' : bdate }
        elif bdate:
            if bplace: #male, month_year, place
                text = _("%(male_name)s "
                        "was buried in %(month_year)s in %(burial_place)s.") % {
                    'male_name' : person_name, 
                    'month_year' : bdate, 'burial_place' : bplace }
            else: #male, month_year, no place
                text = _("%(male_name)s was buried in %(month_year)s.") % {
                    'male_name' : person_name, 'month_year' : bdate }
        else:
            if bplace: #male, no date, place
                text = _("%(male_name)s was buried in %(burial_place)s.") % {
                    'male_name' : person_name, 'burial_place' : bplace }
            else: #male, no date, no place
                text = _("%(male_name)s was buried.") % {
                    'male_name' : person_name }
    else:
        if bdate and bdate_full:
            if bplace: #female, date, place
                text = _("%(female_name)s "
                        "was buried on %(burial_date)s in %(burial_place)s.") % {
                    'female_name' : person_name, 
                    'burial_date' : bdate, 'burial_place' : bplace }
            else: #female, date, no place
                text = _("%(female_name)s was buried on %(burial_date)s.") % {
                    'female_name' : person_name, 'burial_date' : bdate }
        elif bdate:
            if bplace: #female, month_year, place
                text = _("%(female_name)s "
                        "was buried in %(month_year)s in %(burial_place)s.") % {
                    'female_name' : person_name, 
                    'month_year' : bdate, 'burial_place' : bplace }
            else: #female, month_year, no place
                text = _("%(female_name)s was buried in %(month_year)s.") % {
                    'female_name' : person_name, 'month_year' : bdate }
        else:
            if bplace: #female, no date, place
                text = _("%(female_name)s was buried in %(burial_place)s.") % {
                    'female_name' : person_name, 'burial_place' : bplace }
            else: #female, no date, no place
                text = _("%(female_name)s was buried.") % {
                    'female_name' : person_name }

    if text:
        text = text + " "
    return text

def list_person_str(database,person,person_name=None,empty_date="",empty_place=""):
    """ 
    Briefly list person and birth/death events.
    """

    if person_name == None:
        person_name = _nd.display_name(person.get_primary_name())
    elif person_name == 0:
        if person.get_gender() == const.MALE:
            person_name = _('He')
        else:
            person_name = _('She')

    bdate,bplace,bdate_full,ddate,dplace,ddate_full = \
                        get_birth_death_strings(database,person)

    text = ""
    
    if person.get_gender() == const.MALE:
        if bdate:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s "
                            "Born: %(birth_date)s %(birth_place)s "
                            "Died: %(death_date)s %(death_place)s.") % {
                        'male_name' : person_name, 
                        'birth_date' : bdate, 'birth_place' : bplace,
                        'death_date' : ddate,'death_place' : dplace }
                    else:
                        text = _("%(male_name)s "
                            "Born: %(birth_date)s %(birth_place)s "
                            "Died: %(death_date)s.") % {
                        'male_name' : person_name, 
                        'birth_date' : bdate, 'birth_place' : bplace,
                        'death_date' : ddate }
                else:
                    if dplace:
                        text = _("%(male_name)s "
                            "Born: %(birth_date)s %(birth_place)s "
                            "Died: %(death_place)s.") % {
                        'male_name' : person_name, 
                        'birth_date' : bdate, 'birth_place' : bplace,
                        'death_place' : dplace }
                    else:
                        text = _("%(male_name)s "
                            "Born: %(birth_date)s %(birth_place)s.") % {
                        'male_name' : person_name, 
                        'birth_date' : bdate, 'birth_place' : bplace }
            else:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s Born: %(birth_date)s "
                            "Died: %(death_date)s %(death_place)s.") % {
                        'male_name' : person_name, 'birth_date' : bdate, 
                        'death_date' : ddate,'death_place' : dplace }
                    else:
                        text = _("%(male_name)s "
                            "Born: %(birth_date)s Died: %(death_date)s.") % {
                        'male_name' : person_name, 'birth_date' : bdate, 
                        'death_date' : ddate }
                else:
                    if dplace:
                        text = _("%(male_name)s "
                            "Born: %(birth_date)s Died: %(death_place)s.") % {
                        'male_name' : person_name, 
                        'birth_date' : bdate, 'death_place' : dplace }
                    else:
                        text = _("%(male_name)s Born: %(birth_date)s.") % {
                        'male_name' : person_name, 'birth_date' : bdate }
        else:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s "
                            "Born: %(birth_place)s "
                            "Died: %(death_date)s %(death_place)s.") % {
                        'male_name' : person_name, 
                        'birth_place' : bplace,
                        'death_date' : ddate,'death_place' : dplace }
                    else:
                        text = _("%(male_name)s "
                            "Born: %(birth_place)s "
                            "Died: %(death_date)s.") % {
                        'male_name' : person_name, 
                        'birth_place' : bplace,
                        'death_date' : ddate }
                else:
                    if dplace:
                        text = _("%(male_name)s "
                            "Born: %(birth_place)s "
                            "Died: %(death_place)s.") % {
                        'male_name' : person_name, 
                        'birth_place' : bplace,
                        'death_place' : dplace }
                    else:
                        text = _("%(male_name)s "
                            "Born: %(birth_place)s.") % {
                        'male_name' : person_name, 'birth_place' : bplace }
            else:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s "
                            "Died: %(death_date)s %(death_place)s.") % {
                        'male_name' : person_name, 
                        'death_date' : ddate,'death_place' : dplace }
                    else:
                        text = _("%(male_name)s "
                            "Died: %(death_date)s.") % {
                        'male_name' : person_name, 'death_date' : ddate }
                else:
                    if dplace:
                        text = _("%(male_name)s Died: %(death_place)s.") % {
                        'male_name' : person_name, 'death_place' : dplace }
                    else:
                        text = _("%(male_name)s.") % {
                        'male_name' : person_name }
    else:
        if bdate:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s "
                            "Born: %(birth_date)s %(birth_place)s "
                            "Died: %(death_date)s %(death_place)s.") % {
                        'female_name' : person_name, 
                        'birth_date' : bdate, 'birth_place' : bplace,
                        'death_date' : ddate,'death_place' : dplace }
                    else:
                        text = _("%(female_name)s "
                            "Born: %(birth_date)s %(birth_place)s "
                            "Died: %(death_date)s.") % {
                        'female_name' : person_name, 
                        'birth_date' : bdate, 'birth_place' : bplace,
                        'death_date' : ddate }
                else:
                    if dplace:
                        text = _("%(female_name)s "
                            "Born: %(birth_date)s %(birth_place)s "
                            "Died: %(death_place)s.") % {
                        'female_name' : person_name, 
                        'birth_date' : bdate, 'birth_place' : bplace,
                        'death_place' : dplace }
                    else:
                        text = _("%(female_name)s "
                            "Born: %(birth_date)s %(birth_place)s.") % {
                        'female_name' : person_name, 
                        'birth_date' : bdate, 'birth_place' : bplace }
            else:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s Born: %(birth_date)s "
                            "Died: %(death_date)s %(death_place)s.") % {
                        'female_name' : person_name, 'birth_date' : bdate, 
                        'death_date' : ddate,'death_place' : dplace }
                    else:
                        text = _("%(female_name)s "
                            "Born: %(birth_date)s Died: %(death_date)s.") % {
                        'female_name' : person_name, 'birth_date' : bdate, 
                        'death_date' : ddate }
                else:
                    if dplace:
                        text = _("%(female_name)s "
                            "Born: %(birth_date)s Died: %(death_place)s.") % {
                        'female_name' : person_name, 
                        'birth_date' : bdate, 'death_place' : dplace }
                    else:
                        text = _("%(female_name)s Born: %(birth_date)s.") % {
                        'female_name' : person_name, 'birth_date' : bdate }
        else:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s "
                            "Born: %(birth_place)s "
                            "Died: %(death_date)s %(death_place)s.") % {
                        'female_name' : person_name, 
                        'birth_place' : bplace,
                        'death_date' : ddate,'death_place' : dplace }
                    else:
                        text = _("%(female_name)s "
                            "Born: %(birth_place)s "
                            "Died: %(death_date)s.") % {
                        'female_name' : person_name, 
                        'birth_place' : bplace,
                        'death_date' : ddate }
                else:
                    if dplace:
                        text = _("%(female_name)s "
                            "Born: %(birth_place)s "
                            "Died: %(death_place)s.") % {
                        'female_name' : person_name, 
                        'birth_place' : bplace,
                        'death_place' : dplace }
                    else:
                        text = _("%(female_name)s "
                            "Born: %(birth_place)s.") % {
                        'female_name' : person_name, 'birth_place' : bplace }
            else:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s "
                            "Died: %(death_date)s %(death_place)s.") % {
                        'female_name' : person_name, 
                        'death_date' : ddate,'death_place' : dplace }
                    else:
                        text = _("%(female_name)s "
                            "Died: %(death_date)s.") % {
                        'female_name' : person_name, 'death_date' : ddate }
                else:
                    if dplace:
                        text = _("%(female_name)s Died: %(death_place)s.") % {
                        'female_name' : person_name, 'death_place' : dplace }
                    else:
                        text = _("%(female_name)s.") % {
                        'female_name' : person_name }

    if text:
        text = "- %s " % text
    return text

 
_rtype = {
    const.FAMILY_MARRIED       : _("Married"),
    const.FAMILY_UNMARRIED     : _("Unmarried"),
    const.FAMILY_CIVIL_UNION   : _("Civil Union"),
    const.FAMILY_UNKNOWN       : _("Unknown"),
    const.FAMILY_CUSTOM         : _("Other"),
    }

def relationship_name(rtype):
    return _rtype.get(rtype)


def old_calc_age(database,person):
    """
    Calulate age. 
    
    Returns a tuple (age,units) where units is an integer representing
    time units:
        no age info:    0
        years:          1
        months:         2
        days:           3
    """

    # This is an old and ugly implementation. 
    # It must be changed to use the new age calculator.
    age = 0
    units = 0

    birth_handle = person.get_birth_handle()
    if birth_handle:
        birth = database.get_event_from_handle(birth_handle).get_date_object()
        birth_year_valid = birth.get_year_valid()
    else:
        birth_year_valid = None
    death_handle = person.get_death_handle()
    if death_handle:
        death = database.get_event_from_handle(death_handle).get_date_object()
        death_year_valid = death.get_year_valid()
    else:
        death_year_valid = None

    if birth_year_valid and death_year_valid:
        age = death.get_year() - birth.get_year()
        units = 1                          # year
        if birth.get_month_valid() and death.get_month_valid():
            if birth.get_month() > death.get_month():
                age = age - 1
            if birth.get_day_valid() and death.get_day_valid():
                if birth.get_month() == death.get_month() and birth.get_day() > death.get_day():
                    age = age - 1
                if age == 0:
                    age = death.get_month() - birth.get_month()   # calc age in months
                    if birth.get_day() > death.get_day():
                        age = age - 1
                        units = 2                        # month
                    if age == 0:
                        age = death.get_day() + 31 - birth.get_day() # calc age in days
                        units  = 3            # day
    return (age,units)
