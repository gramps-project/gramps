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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import string
import os

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
import intl
_ = intl.gettext

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gtk import *
from gnome.ui import *
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from RelLib import *

import const
import sort
import utils
import Config

class SelectChild:

    def __init__(self,db,family,person,redraw):
        self.db = db
        self.person = person
        self.family = family
        self.redraw = redraw
        self.xml = libglade.GladeXML(const.gladeFile,"selectChild")
    
        self.xml.signal_autoconnect({
            "on_combo_insert_text"     : utils.combo_insert_text,
            "on_save_child_clicked"    : self.on_save_child_clicked,
            "on_show_toggled"          : self.on_show_toggled,
            "destroy_passed_object"    : utils.destroy_passed_object
            })

        self.select_child_list = {}
        self.top = self.xml.get_widget("selectChild")
        self.add_child = self.xml.get_widget("addChild")
        self.add_child.set_column_visibility(1,Config.id_visible)

        father = self.family.getFather()
        if father != None:
            fname = father.getPrimaryName().getName()
            ftitle = _("Relationship to %s") % fname
            self.xml.get_widget("flabel").set_text(ftitle)

        mother = self.family.getMother()
        if mother != None:
            mname = mother.getPrimaryName().getName()
            mtitle = _("Relationship to %s") % mname
            self.xml.get_widget("mlabel").set_text(mtitle)

        self.mrel = self.xml.get_widget("mrel")
        self.frel = self.xml.get_widget("frel")
        self.mrel.set_text(_("Birth"))
        self.frel.set_text(_("Birth"))
    
        self.redraw_child_list(2)
        self.top.show()

    def redraw_child_list(self,filter):
        person_list = self.db.getPersonMap().values()
        person_list.sort(sort.by_last_name)
        self.add_child.freeze()
        self.add_child.clear()
        index = 0

        bday = self.person.getBirth().getDateObj()
        dday = self.person.getDeath().getDateObj()

        bday_valid = (bday.getYear() != -1)
        dday_valid = (dday.getYear() != -1)
    
        slist = []
        for f in [self.person.getMainFamily()] + self.person.getFamilyList():
            if f:
                if f.getFather():
                    slist.append(f.getFather())
                elif f.getMother():
                    slist.append(f.getMother())
                for c in f.getChildList():
                    slist.append(c)
            
        personmap = {}
        for person in person_list:
            if filter:
                if person in slist:
                    continue
                if person.getMainFamily() != None:
                    continue
            
                pdday = person.getDeath().getDateObj()
                pbday = person.getBirth().getDateObj()

                if bday_valid:
                    if pbday.getYear() != -1:

                        # reject if child birthdate < parents birthdate + 10
                        if pbday.getLowYear() < bday.getHighYear()+10:
                            continue

                        # reject if child birthdate > parents birthdate + 90
                        if pbday.getLowYear() > bday.getHighYear()+90:
                            continue

                    if pdday.getYear() != -1:
                        # reject if child deathdate < parents birthdate+ 10
                        if pdday.getLowYear() < bday.getHighYear()+10:
                            continue
                
                if dday_valid:
                    if pbday.getYear() != -1:
                    
                        # reject if childs birth date > parents deathday + 3
                        if pdday.getLowYear() > dday.getHighYear()+3:
                            continue

                    if pdday.getYear() != -1:

                        # reject if childs death date > parents deathday + 150
                        if pbday.getLowYear() > dday.getHighYear() + 150:
                            continue
        
            personmap[utils.phonebook_name(person)] = person

        keynames = personmap.keys()
        keynames.sort()
        for key in keynames:
            person = personmap[key]
            self.add_child.append([utils.phonebook_name(person),utils.birthday(person),\
                                  person.getId()])
            self.add_child.set_row_data(index,person)
            index = index + 1
        self.add_child.thaw()

    def on_save_child_clicked(self,obj):
        for row in self.add_child.selection:
            select_child = self.add_child.get_row_data(row)
            if self.family == None:
                self.family = database.newFamily()
                self.person.addFamily(self.family)
                if self.person.getGender() == Person.male:
                    self.family.setFather(self.person)
                else:	
                    self.family.setMother(self.person)

            self.family.addChild(select_child)
		
            mrel = const.childRelations[self.mrel.get_text()]
            mother = self.family.getMother()
            if mother and mother.getGender() != Person.female:
                if mrel == "Birth":
                    mrel = "Unknown"
                
            frel = const.childRelations[self.frel.get_text()]
            father = self.family.getFather()
            if father and father.getGender() != Person.male:
                if frel == "Birth":
                    frel = "Unknown"

            if mrel == "Birth" and frel == "Birth":
                family = select_child.getMainFamily()
                if family != None and family != self.family:
                    family.removeChild(select_child)

                select_child.setMainFamily(self.family)
            else:
                select_child.addAltFamily(self.family,mrel,frel)

            utils.modified()
        
        utils.destroy_passed_object(obj)
        self.redraw(self.family)
        
    def on_show_toggled(self,obj):
        self.redraw_child_list(obj.get_active())

class NewChild:

    def __init__(self,db,family,person,update):
        self.db = db
        self.person = person
        self.family = family
        self.update = update
        
        self.xml = libglade.GladeXML(const.gladeFile,"addChild")
        self.xml.signal_autoconnect({
            "on_addchild_ok_clicked" : self.on_addchild_ok_clicked,
            "on_combo_insert_text"   : utils.combo_insert_text,
            "destroy_passed_object" : utils.destroy_passed_object
            })

        self.mrel = self.xml.get_widget("mrel")
        self.frel = self.xml.get_widget("frel")
        self.top  = self.xml.get_widget("addChild")
        self.surname = self.xml.get_widget("childSurname")
        self.given = self.xml.get_widget("childGiven")
        utils.attach_surnames(self.xml.get_widget("surname_combo"))

        surname = ""
        if self.person.getGender() == Person.male:
            surname = self.person.getPrimaryName().getSurname()
        elif self.family:
            f = self.family.getFather()
            if f:
                surname = f.getPrimaryName().getSurname()

        if self.family:
            father = self.family.getFather()
            mother = self.family.getMother()

            if father != None:
                fname = father.getPrimaryName().getName()
                label = _("Relationship to %s") % fname
                self.xml.get_widget("flabel").set_text(label)

            if mother != None:
                mname = mother.getPrimaryName().getName()
                label = _("Relationship to %s") % mname
                self.xml.get_widget("mlabel").set_text(label)
        else:
            fname = self.person.getPrimaryName().getName()
            label = _("Relationship to %s") % fname
            
            if self.person.getGender() == Person.male:
                self.xml.get_widget("flabel").set_text(label)
                self.xml.get_widget("mcombo").set_sensitive(0)
            else:
                self.xml.get_widget("mlabel").set_text(label)
                self.xml.get_widget("fcombo").set_sensitive(0)

        self.surname.set_text(surname)
        self.mrel.set_text(_("Birth"))
        self.frel.set_text(_("Birth"))

        # Typing CR selects OK button
        self.top.editable_enters(self.given)
        self.top.editable_enters(self.surname)
        self.top.editable_enters(self.mrel)
        self.top.editable_enters(self.frel)
        self.top.show()
        
    def on_addchild_ok_clicked(self,obj):
    
        surname = self.surname.get_text()
        given = self.given.get_text()
    
        person = Person()
        self.db.addPerson(person)

        name = Name()
        name.setSurname(surname)
        name.setFirstName(given)
        person.setPrimaryName(name)

        if self.xml.get_widget("childMale").get_active():
            person.setGender(Person.male)
        elif self.xml.get_widget("childFemale").get_active():
            person.setGender(Person.female)
        else:
            person.setGender(Person.unknown)
        
        if not self.family:
            self.family = self.db.newFamily()
            if self.person.getGender() == Person.male:
                self.family.setFather(self.person)
            else:
                self.family.setMother(self.person)
            self.person.addFamily(active_family)

        mrel = const.childRelations[self.mrel.get_text()]
        frel = const.childRelations[self.frel.get_text()]

        if mrel == "Birth" and frel == "Birth":
            person.setMainFamily(self.family)
        else:
            person.addAltFamily(self.family,mrel,frel)

        self.family.addChild(person)
        
        # must do an apply filter here to make sure the main window gets updated
    
        self.update(self.family,person)
        utils.modified()
        utils.destroy_passed_object(obj)

