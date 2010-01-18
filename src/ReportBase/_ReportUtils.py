#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2009  Brian G. Matherly
# Copyright (C) 2008       James Friedmann <jfriedmannj@gmail.com>
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

# $Id:_ReportUtils.py 9912 2008-01-22 09:17:46Z acraphae $

"""
A collection of utilities to aid in the generation of reports.
"""

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import os
from gen.ggettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import DateHandler
from Utils import media_path_full
from gen.plug.docgen import IndexMark, INDEX_TYPE_ALP
   
#-------------------------------------------------------------------------
#
#  Convert points to cm and back
#
#-------------------------------------------------------------------------
def pt2cm(pt):
    """
    Convert points to centimeters. Fonts are typically specified in points, 
    but the BaseDoc classes use centimeters.

    @param pt: points
    @type pt: float or int
    @returns: equivalent units in centimeters
    @rtype: float
    """
    return pt/28.3465

def cm2pt(cm):
    """
    Convert centimeters to points. Fonts are typically specified in points, 
    but the BaseDoc classes use centimeters.

    @param cm: centimeters
    @type cm: float or int
    @returns: equivalent units in points
    @rtype: float
    """
    return cm*28.3465

def rgb_color(color):
    """
    Convert color value from 0-255 integer range into 0-1 float range.

    @param color: list or tuple of integer values for red, green, and blue
    @type color: int
    @returns: (r, g, b) tuple of floating point color values
    @rtype: 3-tuple
    """
    r = float(color[0])/255.0
    g = float(color[1])/255.0
    b = float(color[2])/255.0
    return (r, g, b)

#-------------------------------------------------------------------------
#
#  Roman numbers
#
#-------------------------------------------------------------------------
def roman(num):
    """ Integer to Roman numeral converter for 0 < num < 4000 """
    if not isinstance(num, int):
        return "?"
    if not 0 < num < 4000:
        return "?"
    vals = (1000, 900, 500, 400, 100,  90,  50,  40,  10,   9,   5,   4,   1)
    nums = ( 'M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
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
def place_name(db, place_handle):
    if place_handle:
        place = db.get_place_from_handle(place_handle).get_title()
    else:
        place = ""
    return unicode(place)
    
#-------------------------------------------------------------------------
#
# Functions commonly used in reports
#
#-------------------------------------------------------------------------
def insert_image(database, doc, photo, w_cm=4.0, h_cm=4.0):
    """
    Insert pictures of a person into the document.
    """

    object_handle = photo.get_reference_handle()
    media_object = database.get_object_from_handle(object_handle)
    mime_type = media_object.get_mime_type()
    if mime_type and mime_type.startswith("image"):
        filename = media_path_full(database, media_object.get_path())
        if os.path.exists(filename):
            doc.add_media_object(filename, "right", w_cm, h_cm)
        else:
            from QuestionDialog import WarningDialog
            WarningDialog(_("Could not add photo to page"), 
                          "%s: %s" % (filename, _('File does not exist')))

#-------------------------------------------------------------------------
#
# find_spouse
#
#-------------------------------------------------------------------------
def find_spouse(person, family):
    if person.get_handle() == family.get_father_handle():
        spouse_handle = family.get_mother_handle()
    else:
        spouse_handle = family.get_father_handle()
    return spouse_handle

#-------------------------------------------------------------------------
#
# find_marriage
#
#-------------------------------------------------------------------------
def find_marriage(database, family):    
    for event_ref in family.get_event_ref_list():
        event = database.get_event_from_handle(event_ref.ref)
        if (event and event.type.is_marriage() and
            event_ref.role.is_family()):
            return event
    return None

#-------------------------------------------------------------------------
#
# Indexing function
#
#-------------------------------------------------------------------------
def get_person_mark(db, person):
    """
    Return a IndexMark that can be used to index a person in a report
    
    @param db: the GRAMPS database instance
    @param person: the the key is for
    """
    if not person:
        return None
    
    name = person.get_primary_name().get_name()
    birth = " "
    death = " "
    key = ""
    
    birth_ref = person.get_birth_ref()
    if birth_ref:
        birthEvt = db.get_event_from_handle(birth_ref.ref)
        birth = DateHandler.get_date(birthEvt)

    death_ref = person.get_death_ref()
    if death_ref:
        deathEvt = db.get_event_from_handle(death_ref.ref)
        death = DateHandler.get_date(deathEvt)

    if birth == death == " ":
        key = name
    else:
        key = "%s (%s - %s)" % (name, birth, death)
        
    return IndexMark( key, INDEX_TYPE_ALP )

#-------------------------------------------------------------------------
#
# Address String
#
#-------------------------------------------------------------------------
def get_address_str(addr):
    """
    Return a string that combines the elements of an addres
    
    @param addr: the GRAMPS address instance
    """
    str = ""
    elems = [ addr.get_street(), 
              addr.get_city(), 
              addr.get_county(), 
              addr.get_state(), 
              addr.get_country(), 
              addr.get_postal_code(), 
              addr.get_phone()   ]
    
    for info in elems:
        if info:
            if str == "":
                str = info
            else:
                str = "%s, %s" % (str, info)
    return str
    
#-------------------------------------------------------------------------
#
# People Filters
#
#-------------------------------------------------------------------------
def get_person_filters(person, include_single=True):
    """
    Return a list of filters that are relevant for the given person

    @param person: the person the filters should apply to.
    @type person: L{Person}
    @param include_single: include a filter to include the single person
    @type person: boolean
    """
    from Filters import GenericFilter, Rules, CustomFilters
    from gen.display.name import displayer as name_displayer

    if person:
        name = name_displayer.display(person)
        gramps_id = person.get_gramps_id()
    else:
        # Do this in case of command line options query (show=filter)
        name = 'PERSON'
        gramps_id = ''
    
    if include_single:
        filt_id = GenericFilter()
        filt_id.set_name(name)
        filt_id.add_rule(Rules.Person.HasIdOf([gramps_id]))

    all = GenericFilter()
    all.set_name(_("Entire Database"))
    all.add_rule(Rules.Person.Everyone([]))

    des = GenericFilter()
    des.set_name(_("Descendants of %s") % name)
    des.add_rule(Rules.Person.IsDescendantOf([gramps_id, 1]))

    df = GenericFilter()
    df.set_name(_("Descendant Families of %s") % name)
    df.add_rule(Rules.Person.IsDescendantFamilyOf([gramps_id, 1]))

    ans = GenericFilter()
    ans.set_name(_("Ancestors of %s") % name)
    ans.add_rule(Rules.Person.IsAncestorOf([gramps_id, 1]))

    com = GenericFilter()
    com.set_name(_("People with common ancestor with %s") % name)
    com.add_rule(Rules.Person.HasCommonAncestorWith([gramps_id]))

    if include_single:
        the_filters = [filt_id, all, des, df, ans, com]
    else:
        the_filters = [all, des, df, ans, com]
    the_filters.extend(CustomFilters.get_filters('Person'))
    return the_filters
