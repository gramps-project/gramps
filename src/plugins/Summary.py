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
            
    text = _("Individuals") + "\n"
    text = text + "----------------------------\n"
    text = text + "%s : %d\n" % (_("Number of individuals"),len(personList))
    text = text + "%s : %d\n" % (_("Males"),males)
    text = text + "%s : %d\n" % (_("Females"),females)
    text = text + "%s : %d\n" % (_("Individuals with incomplete names"),incomp_names)
    text = text + "%s : %d\n" % (_("Individuals missing birth dates"),missing_bday)
    text = text + "%s : %d\n" % (_("Disconnected individuals"),disconnected)
    text = text + "\n%s\n" % _("Images and files")
    text = text + "----------------------------\n"
    text = text + "%s : %d\n" % (_("Individuals with images"),with_photos)
    text = text + "%s : %d\n" % (_("Total number of images"),total_photos)
    text = text + "%s : %d %s\n" % (_("Total size of images"),bytes,\
                                    _("bytes"))
    text = text + "\n%s\n" % _("Family Information")
    text = text + "----------------------------\n"
    text = text + "%s : %d\n" % (_("Number of families"),len(familyList))
    text = text + "%s : %d\n" % (_("Unique surnames"),len(namelist))
    
    
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
