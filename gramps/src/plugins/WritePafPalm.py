#
# WritePafPalm.py - export module to write pdb files for use with PAF for PalmOS
#
# Copyright (C) 2001 Jesper Zedlitz <jesper@zedlitz.de>
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

"Export to PAF for PalmOS"

from RelLib import *
import os
import string
import time
import const
import Utils
import intl
_ = intl.gettext

from gtk import *
from gnome.ui import *
from libglade import *

import const
from latin_ansel import latin_to_ansel
from latin_utf8  import latin_to_utf8

cnvtxt = latin_to_ansel
database_name = "Untitled"
description = ""

topDialog = None
db = None

people_list = []
family_list = []
source_list = []
string_list = {}
number_of_records = 0

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def entire_database():
    global people_list
    global family_list
    global source_list
    
    people_list = db.getPersonMap().values()
    family_list = db.getFamilyMap().values()
    source_list = db.getSourceMap().values()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def active_person_descendants():
    global people_list
    global family_list
    global source_list
    
    people_list = []
    family_list = []
    source_list = []
    descend(active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def active_person_ancestors_and_descendants():
    global people_list
    global family_list
    global source_list
    
    people_list = []
    family_list = []
    source_list = []
    descend(active_person)
    ancestors(active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def active_person_ancestors():
    global people_list
    global family_list
    global source_list
    
    people_list = []
    family_list = []
    source_list = []
    ancestors(active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def interconnected():
    global people_list
    global family_list
    global source_list
    
    people_list = []
    family_list = []
    source_list = []
    walk(active_person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def descend(person):
    if person == None or person in people_list:
        return
    people_list.append(person)
    add_persons_sources(person)
    for family in person.getFamilyList():
        add_familys_sources(family)
        family_list.append(family)
        father = family.getFather()
        mother = family.getMother()
        if father != None and father not in people_list:
            people_list.append(father)
            add_persons_sources(father)
        if mother != None and mother not in people_list:
            people_list.append(mother)
            add_persons_sources(mother)
        for child in family.getChildList():
            descend(child)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def ancestors(person):
    if person == None or person in people_list:
        return
    people_list.append(person)
    add_persons_sources(person)
    family = person.getMainParents()
    if family == None or family in family_list:
        return
    add_familys_sources(family)
    family_list.append(family)
    ancestors(family.getMother())
    ancestors(family.getFather())

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def walk(person):
    if person == None or person in people_list:
        return
    people_list.append(person)
    add_persons_sources(person)
    families = person.getFamilyList()
    for f in person.getAltParentList():
        families.append(f[0])
    for family in families:
        if family == None or family in family_list:
            continue
        add_familys_sources(family)
        family_list.append(family)
        walk(family.getFather())
        walk(family.getMother())
        for child in family.getChildList():
            walk(child)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_persons_sources(person):
    elist = person.getEventList()[:]

    elist.append(person.getBirth())
    elist.append(person.getDeath())
    for event in elist:
        if private and event.getPrivacy():
            continue
        source_ref = event.getSourceRef()
        if source_ref != None:
            source_list.append(source_ref)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_familys_sources(family):
    for event in family.getEventList():
        if private and event.getPrivacy():
            continue
        source_ref = event.getSourceRef()
        if source_ref != None:
            source_list.append(source_ref)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def sortById(first,second):
    fid = first.getId()
    sid = second.getId()

    if fid == sid:
        return 0
    elif fid < sid:
        return -1
    else:
        return 1
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def sortByName(first,second):
    fsn = first.getPrimaryName().getSurname()
    ssn = second.getPrimaryName().getSurname()

    if fsn == ssn:
        ffn = first.getPrimaryName().getFirstName()
        sfn = second.getPrimaryName().getFirstName()
	if ffn == sfn:
            return 0
	elif ffn < sfn:
	    return -1
	else:
	    return 1
    elif fsn < ssn:
        return -1
    else:
        return 1

       
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_year( event ):
    year = 0
    if event != None:
        dateObj = event.getDateObj()
        if dateObj != None:
	    year = dateObj.getYear()
    if year < 0:
        year = 0
    return year

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_place( event ):
    place = ""
    if event != None:
        place = event.getPlaceName()
    if place == "":
        place = " "
    return place

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_date( event ):
    date = ""
    if event != None:
        date = event.getDate()
    if date == "":
        date = " "
    return date

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def text_ref( s ):
    global string_list
    global number_of_records
    text_offset = string_list[s]
    data = chr( (number_of_records-1)/256 ) + chr( (number_of_records-1) % 256 )
    data = data + chr( text_offset/256 ) + chr( text_offset % 256 )
    return data

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_16_bit( i ):
    return chr( i / 256 ) + chr ( i % 256 )
    
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def write_32_bit( i ):
    return write_16_bit( i / 65536 ) + write_16_bit( i % 65536 )
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def exportData(database, filename):
    global database_name
    global description
    global string_list
    global number_of_records

    g = open(filename,"wb")

    number_of_records = len(people_list)+len(family_list)+1

    g.write("%s-PAFg" % (database_name))
    g.write("\0"*( 27-len(database_name) ) )
    g.write("\0\x08\0\4")
    g.write("\xb7\xd7\x66\xf1")    # creation time in seconds since 1904-01-01
    g.write("\xb7\xd7\x66\xf1")    # modification time 
    g.write("\0\0\0\0")            # backup time
    g.write("\0\0\0\0\0\0")
    
    offset_infoblock = 80 + 8 * number_of_records 
    g.write( write_16_bit( offset_infoblock ) )
    g.write("\0\0\0\0GdatPAFg\0\0\0\0\0\0\0\0")
    g.write( write_16_bit( number_of_records ) )

    # collect all string contained in the data
    for person in people_list:
        string_list[person.getPrimaryName().getFirstName()] = 0
        string_list[person.getPrimaryName().getSurname()] = 0
        string_list[ get_place( person.getBirth() ) ] = 0
        string_list[ get_date( person.getBirth() ) ] = 0
        string_list[ get_place( person.getDeath() ) ] = 0
        string_list[ get_date( person.getDeath() ) ] = 0
        string_list[ person.getNote() ] = 0
    for family in family_list:
        string_list[ get_place( family.getMarriage() ) ] = 0
        string_list[ get_date( family.getMarriage() ) ] = 0
    strings = string_list.keys()
    strings.sort()

    offset = 0
    text_block = ""
    for s in strings:
        text_block = text_block + s + "\0"
        string_list[s] = offset
	offset = offset + len(s) +1
	
    id_to_record = {}
    fid_to_record = {}
    
    record_nr = len(people_list)
    for family in family_list:
        fid_to_record[ family.getId() ] = record_nr
	record_nr = record_nr +1
    
    next_pointer = offset_infoblock + 512
    person_data = []
    people_list.sort(sortByName)
    record_nr = 0
    for person in people_list:
        id_to_record[ person.getId() ] = record_nr
	record_nr = record_nr +1
        data = "\0\0"
	
	if person.getNote() != "":
	    data = data + "\x10"
	else:
	    data = data + "\0"
	
	data = data + "\x0f"
	data = data + write_16_bit( int(person.getId()[1:])+1 )
	data = data + write_16_bit( get_year(person.getBirth()) )
	data = data + write_16_bit( get_year(person.getDeath()) )
	
	if person.getMainParents() != None:
	    data = data + write_16_bit( fid_to_record[person.getMainParents().getId()] )
	else:
	    data = data + "\xff\xff"
	    
	families = person.getFamilyList()
	if len(families) > 0:
	    data = data + "\1"
	else:
	    data = data + "\0"
	    
	if person.getGender() == Person.female:
	   data = data + "\1"
	else:
	   data = data + "\2"

	if len(families) > 0:
	    data = data + write_16_bit( fid_to_record[ families[0].getId() ] )

	data = data + text_ref( person.getPrimaryName().getSurname() )
	data = data + text_ref( person.getPrimaryName().getFirstName() )
	if get_year(person.getBirth()) > 0 :
	    data = data + text_ref( get_date(person.getBirth()) )
	    data = data + text_ref( get_place(person.getBirth()) )
	if get_year(person.getDeath()) > 0 :
	    data = data + text_ref( get_date(person.getDeath()) )
	    data = data + text_ref( get_place(person.getDeath()) )

	if person.getNote() != "":
	    data = data + text_ref( person.getNote() )
	    
        person_data.append(data)
	
	# pointer to record
	g.write( write_32_bit( next_pointer ) )
	g.write("\0\0\0\0")
	next_pointer = next_pointer + len(data)

    family_data = []
    for family in family_list:
        data = "\0\1"
	father = family.getFather()
	mother = family.getMother()
	
	if father != None:
	   data = data + write_16_bit( id_to_record[father.getId()] )
	else:
	   data = data + "\xff\xff" 
	   
	if mother != None:
	   data = data + write_16_bit( id_to_record[mother.getId()] )
	else:
	   data = data + "\xff\xff" 
	   
	data = data + write_16_bit( get_year( family.getMarriage() ) )
	data = data + "\3"
	
	children = family.getChildList()
	data = data + chr( len(children) )
	for child in children:
	    data = data + write_16_bit( id_to_record[child.getId()] )
	    
	data = data + text_ref( get_date(family.getMarriage()) )
	data = data + text_ref( get_place(family.getMarriage()) )
        family_data.append(data)

	# pointer to record
	g.write( write_32_bit( next_pointer ) )
	g.write("\0\0\0\0")
	next_pointer = next_pointer + len(data)
        

    # pointer to textblock
    g.write( write_32_bit( next_pointer ) )
    g.write("\0\0\0\0\0\0")
    
    
    infoblock = "\xb7\xd7\x66\xf1\0\0\0\0\0\0\0\0\0\0\0\0"
    infoblock = infoblock + "\0\0\0\0\0\0\0\0\0\1\0\1\0\1\0\1"
    infoblock = infoblock + "\0\1\0\1\0\1\0\1\0\1\0\1\0\1\0\1"
    infoblock = infoblock + "\0\1\0\1\0\1\0\1\0\x03" \
                          + write_16_bit( len(people_list) ) \
			  + write_16_bit( len(family_list) )
    infoblock = infoblock + "\0\1\0\0\0" 
    infoblock = infoblock + description
#    owner = database.getResearcher()
#    if owner.getName() != "":
    infoblock = infoblock + ( "\0"*(512- len(infoblock)) )
    g.write(infoblock)

    for data in person_data:
        g.write(data)

    for data in family_data:
        g.write(data)
  
    g.write(text_block)    
    g.close()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_ok_clicked(obj):
    global db
    global database_name
    global description
    global topDialog
    global restrict
    global private
    
    database_name = topDialog.get_widget("dbname").get_text()
    description = topDialog.get_widget("description").get_text()
    restrict = topDialog.get_widget("restrict").get_active()
    private = topDialog.get_widget("private").get_active()
    filter_obj = topDialog.get_widget("filter").get_menu().get_active()
    filter = filter_obj.get_data("filter")

    name = topDialog.get_widget("filename").get_text()
    filter()
    
    exportData(db,name)
    Utils.destroy_passed_object(obj)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def writeData(database,person):
    global db
    global topDialog
    global active_person
    
    db = database
    active_person = person
    
    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "pafexport.glade"
        
    dic = {
        "destroy_passed_object" : Utils.destroy_passed_object,
        "on_ok_clicked" : on_ok_clicked
        }

    topDialog = GladeXML(glade_file,"pafExport")
    topDialog.signal_autoconnect(dic)

    filter_obj = topDialog.get_widget("filter")
    myMenu = GtkMenu()
    menuitem = GtkMenuItem(_("Entire Database"))
    myMenu.append(menuitem)
    menuitem.set_data("filter",entire_database)
    menuitem.show()
    name = active_person.getPrimaryName().getRegularName()
    menuitem = GtkMenuItem(_("Ancestors of %s") % name)
    myMenu.append(menuitem)
    menuitem.set_data("filter",active_person_ancestors)
    menuitem.show()
    menuitem = GtkMenuItem(_("Descendants of %s") % name)
    myMenu.append(menuitem)
    menuitem.set_data("filter",active_person_descendants)
    menuitem.show()
    menuitem = GtkMenuItem(_("Ancestors and Descendants of %s") % name)
    myMenu.append(menuitem)
    menuitem.set_data("filter",active_person_ancestors_and_descendants)
    menuitem.show()
    menuitem = GtkMenuItem(_("People somehow connected to %s") % name)
    myMenu.append(menuitem)
    menuitem.set_data("filter",interconnected)
    menuitem.show()
    filter_obj.set_menu(myMenu)

    topDialog.get_widget("pafExport").show()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_export

register_export(writeData,_("Export to PAF for PalmOS"))
