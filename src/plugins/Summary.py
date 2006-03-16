#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"View/Summary of the database"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os
import posixpath
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
import gtk.glade

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import Utils
import RelLib
from PluginUtils import Report, register_report
import DateHandler

#------------------------------------------------------------------------
#
# Build the text of the report
#
#------------------------------------------------------------------------
def build_report(database,person):

    personList = database.get_person_handles(sort_handles=False)
    familyList = database.get_family_handles()

    with_photos = 0
    total_photos = 0
    incomp_names = 0
    disconnected = 0
    missing_bday = 0
    males = 0
    females = 0
    bytes = 0
    namelist = []
    notfound = []
    
    pobjects = len(database.get_media_object_handles())
    for photo_id in database.get_media_object_handles():
        photo = database.get_object_from_handle(photo_id)
        try:
            bytes = bytes + posixpath.getsize(photo.get_path())
        except:
            notfound.append(photo.get_path())
        
    for person_handle in personList:
        person = database.get_person_from_handle(person_handle)
        if not person:
            continue
        length = len(person.get_media_list())
        if length > 0:
            with_photos = with_photos + 1
            total_photos = total_photos + length
                
        person = database.get_person_from_handle(person_handle)
        name = person.get_primary_name()
        if name.get_first_name() == "" or name.get_surname() == "":
            incomp_names = incomp_names + 1
        if (not person.get_main_parents_family_handle()) and (not len(person.get_family_handle_list())):
            disconnected = disconnected + 1
        birth_handle = person.get_birth_handle()
        if birth_handle:
            birth = database.get_event_from_handle(birth_handle)
            if not DateHandler.get_date(birth):
                missing_bday = missing_bday + 1
        else:
            missing_bday = missing_bday + 1
        if person.get_gender() == RelLib.Person.FEMALE:
            females = females + 1
        else:
            males = males + 1
        if name.get_surname() not in namelist:
            namelist.append(name.get_surname())
            
    text = _("Individuals") + "\n"
    text = text + "----------------------------\n"
    text = text + "%s: %d\n" % (_("Number of individuals"),len(personList))
    text = text + "%s: %d\n" % (_("Males"),males)
    text = text + "%s: %d\n" % (_("Females"),females)
    text = text + "%s: %d\n" % (_("Individuals with incomplete names"),incomp_names)
    text = text + "%s: %d\n" % (_("Individuals missing birth dates"),missing_bday)
    text = text + "%s: %d\n" % (_("Disconnected individuals"),disconnected)
    text = text + "\n%s\n" % _("Family Information")
    text = text + "----------------------------\n"
    text = text + "%s: %d\n" % (_("Number of families"),len(familyList))
    text = text + "%s: %d\n" % (_("Unique surnames"),len(namelist))
    text = text + "\n%s\n" % _("Media Objects")
    text = text + "----------------------------\n"
    text = text + "%s: %d\n" % (_("Individuals with media objects"),with_photos)
    text = text + "%s: %d\n" % (_("Total number of media object references"),total_photos)
    text = text + "%s: %d\n" % (_("Number of unique media objects"),pobjects)
    text = text + "%s: %d %s\n" % (_("Total size of media objects"),bytes,\
                                    _("bytes"))

    if len(notfound) > 0:
        text = text + "\n%s\n" % _("Missing Media Objects")
        text = text + "----------------------------\n"
        for p in notfound:
            text = text + "%s\n" % p
    
    return text
    
#------------------------------------------------------------------------
#
# Output report in a window
#
#------------------------------------------------------------------------
class SummaryReport:
    def __init__(self,database,person):
        text = build_report(database,person)
    
        base = os.path.dirname(__file__)
        glade_file = "%s/summary.glade" % base

        topDialog = gtk.glade.XML(glade_file,"summary","gramps")
        topDialog.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
        })

        Utils.set_titles(topDialog.get_widget('summary'),
                     topDialog.get_widget('title'),
                     _('Database summary'))

    
        top = topDialog.get_widget("summary")
        textwindow = topDialog.get_widget("textwindow")
        textwindow.get_buffer().set_text(text)
        top.show()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
register_report(
    name = 'summary',
    category = Report.CATEGORY_VIEW,
    report_class = SummaryReport,
    options_class = None,
    modes = Report.MODE_GUI,
    translated_name = _("Summary of the database"),
    status = _("Beta"),
    description= _("Provides a summary of the current database"),
    )
