#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

"View/Summary of the database"

from RelLib import *
import os
import posixpath
import re
import sort
import string
import utils
import intl
_ = intl.gettext

from gtk import *
from gnome.ui import *
from libglade import *

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    
    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "summary.glade"

    topDialog = GladeXML(glade_file,"summary")
    topDialog.signal_autoconnect({
        "destroy_passed_object" : utils.destroy_passed_object,
    })

    personList = database.getPersonMap().values()
    familyList = database.getFamilyMap().values()

    with_photos = 0
    total_photos = 0
    incomp_names = 0
    disconnected = 0
    missing_bday = 0
    males = 0
    females = 0
    people = 0
    bytes = 0
    namelist = []
    
    for person in personList:
        length = len(person.getPhotoList())
        if length > 0:
            with_photos = with_photos + 1
            total_photos = total_photos + length
            for file in person.getPhotoList():
                bytes = bytes + posixpath.getsize(file.getPath())
                
        name = person.getPrimaryName()
        if name.getFirstName() == "" or name.getSurname() == "":
            incomp_names = incomp_names + 1
        if person.getMainFamily() == None and len(person.getFamilyList()) == 0:
            disconnected = disconnected + 1
        if person.getBirth().getDate() == "":
            missing_bday = missing_bday + 1
        if person.getGender() == Person.female:
            females = females + 1
        else:
            males = males + 1
        if name.getSurname() not in namelist:
            namelist.append(name.getSurname())
            
    text = "Individuals\n"
    text = text + "----------------------------\n"
    text = text + "Number of individuals : %d\n" % len(personList)
    text = text + "Males : %d\n" % males
    text = text + "Females : %d\n" % females
    text = text + "Individuals with incomplete names : %d\n" % incomp_names
    text = text + "Individuals missing birth dates : %d\n" % missing_bday
    text = text + "Disconnected individuals : %d\n" % disconnected
    text = text + "\nPhotos and files\n"
    text = text + "----------------------------\n"
    text = text + "Individuals with photos : %d\n" % with_photos
    text = text + "Total number of photos : %d\n" % total_photos
    text = text + "Total size of photos : %d bytes\n" % bytes
    text = text + "\nFamily Information\n"
    text = text + "----------------------------\n"
    text = text + "Number of families : %d\n" % len(familyList)
    text = text + "Unique surnames : %d\n" % len(namelist)
    
    
    top = topDialog.get_widget("summary")
    textwindow = topDialog.get_widget("textwindow")
    textwindow.show_string(text)
    top.show()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_description():
    return _("Provides a summary of the current database")


def get_name():
    return _("View/Summary of the database")
