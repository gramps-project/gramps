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

"Database Processing/Check database integrity"

import RelLib
import utils
import soundex
import Config
import intl
_ = intl.gettext

import string
import os

from gtk import *
from gnome.ui import *
from libglade import *

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback):

    checker = CheckIntegrity(database)
    checker.check_for_broken_family_links()
    checker.cleanup_missing_photos()
    checker.check_parent_relationships()
    checker.cleanup_empty_families(0)
    checker.report()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

class CheckIntegrity:
    
    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def __init__(self,db):
        self.db = db
        self.bad_family_photo = []
        self.bad_person_photo = []
        self.empty_family = []
        self.broken_links = []
        self.fam_rel = []

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def check_for_broken_family_links(self):
        self.broken_links = []
        family_list = self.db.getFamilyMap().values()[:]
        for family in family_list:
            for child in family.getChildList():
                if family == child.getMainFamily():
                    continue
                for family_type in child.getAltFamilyList():
                    if family_type[0] == family:
                        break
                else:
                    self.broken_links.append((child,family))

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def cleanup_missing_photos(self):
        for family in self.db.getFamilyMap().values():
            for photo in family.getPhotoList():
                if not os.path.isfile(photo.getPath()):
                    self.bad_family_photo.append(family,photo)

        for person in self.db.getPersonMap().values():
            for photo in person.getPhotoList():
                if not os.path.isfile(photo.getPath()):
                    self.bad_person_photo.append(person,photo)

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def cleanup_empty_families(self,automatic):

        family_list = self.db.getFamilyMap().values()[:]
        for family in family_list:
            child_list = family.getChildList()[:]
            num_kids = len(child_list)
            father = family.getFather()
            mother = family.getMother()

            if num_kids == 0:
                if father or mother:
                    continue
                elif not father and not mother:
                    self.db.deleteFamily(family)
                elif automatic:
                    self.db.deleteFamily(family)
                else:
                    self.empty_family.append(family)

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def check_parent_relationships(self):

        family_list = self.db.getFamilyMap().values()[:]
        for family in family_list:
            father = family.getFather()
            mother = family.getMother()
            type = family.getRelationship()

            if type != "Partners":
                if father.getGender() == mother.getGender():
                    family.setRelationship("Partners")
                    self.fam_rel.append(family)
                elif father.getGender() != RelLib.Person.male or \
                     mother.getGender() != RelLib.Person.female:
                    family.setFather(mother)
                    family.setMother(father)
                    self.fam_rel.append(family)
            else:
                if father.getGender() != mother.getGender():
                    family.setRelationship("Unknown")
                    self.fam_rel.append(family)
                    if father.getGender() == RelLib.Person.female:
                        family.setFather(mother)
                        family.setMother(father)

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def report(self):
        fphotos = len(self.bad_family_photo)
        pphotos = len(self.bad_person_photo)
        efam = len(self.empty_family)
        blink = len(self.broken_links)
        rel = len(self.fam_rel)
        
        errors = blink + efam + pphotos + fphotos + rel
        
        if errors == 0:
            GnomeOkDialog(_("No errors were found"))
            return

        text = ""
        if blink == 1:
            text = text + _("1 broken family link was found\n")
        elif blink > 1:
            text = text + _("%d broken family links were found\n") % blink
        if efam == 1:
            text = text + _("1 empty family was found\n")
        elif efam > 1:
            text = text + _("%d empty families were found\n") % efam
        if rel == 1:
            text = text + _("1 corrupted family relationship fixed\n")
        elif rel > 1:
            text = text + _("%d corrupted family relationship fixed\n") % rel
        if fphotos == 1:
            text = text + _("1 broken family image was found\n")
        elif fphotos > 1:
            text = text + _("%d broken family images were found\n") % fphotos
        if pphotos == 1:
            text = text + _("1 broken personal image was found\n")
        elif pphotos > 1:
            text = text + _("%d broken personal images were found\n") % pphotos
                
        GnomeWarningDialog(string.strip(text))
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_description():
    return _("Checks the database for any relationship errors")

def get_name():
    return _("Database Processing/Check database integrity")
