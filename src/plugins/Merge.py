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

"Database Processing/Merge people"

import RelLib
import utils
import soundex
import Check
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
def is_initial(name):
    if len(name) > 2:
        return 0
    elif len(name) == 2:
        if name[0] in string.uppercase and name[1] == '.':
            return 1
    else:
        return name[0] in string.uppercase

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def ancestors_of(p1,list):

    if p1 == None:
        return
    list.append(p1)
    f1 = p1.getMainFamily()
    if f1 != None:
        ancestors_of(f1.getFather(),list)
        ancestors_of(f1.getMother(),list)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_name_obj(p1):
    if p1 == None:
        return None
    else:
        return p1.getPrimaryName()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_merge_ok_clicked(obj):
    
    myobj = obj.get_data("t")
    active = myobj.menu.get_menu().get_active().get_data("v")
    myobj.use_soundex = myobj.soundex_obj.get_active()
    utils.destroy_passed_object(obj)
    myobj.find_potentials(active)
    myobj.show()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class Merge:

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def __init__(self,database,callback):
        self.db = database
        self.map = {}
        self.list = []
        self.index = 0
        self.merger = None
        self.mergee = None
        self.removed = {}
        self.update = callback
        self.use_soundex = 1

        self.family_list = database.getFamilyMap().values()[:]
        self.person_list = database.getPersonMap().values()[:]

        base = os.path.dirname(__file__)
        self.glade_file = base + os.sep + "merge.glade"
        top = GladeXML(self.glade_file,"dialog")
        topWin = top.get_widget("dialog")
        topWin.set_data("t",self)
        
        my_menu = GtkMenu()
        item = GtkMenuItem("Low")
        item.set_data("v",0.25)
        item.show()
        my_menu.append(item)
        item = GtkMenuItem("Medium")
        item.set_data("v",1.0)
        item.show()
        my_menu.append(item)
        item = GtkMenuItem("High")
        item.set_data("v",2.0)
        item.show()
        my_menu.append(item)

        self.soundex_obj = top.get_widget("soundex")
        self.menu = top.get_widget("menu")
        self.menu.set_menu(my_menu)

        top.signal_autoconnect({
            "on_merge_ok_clicked" : on_merge_ok_clicked,
            "destroy_passed_object" : utils.destroy_passed_object
            })
    
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def progress_update(self,val):
        self.progress.set_value(val)
        while events_pending():
            mainiteration()

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def find_potentials(self,thresh):

        top = GladeXML(self.glade_file,"message")
        self.topWin = top.get_widget("message")
        self.progress = top.get_widget("progressbar1")
        self.topWin.show()

        index = 0

        males = {}
        females = {}
        for p1 in self.person_list:
            key = self.gen_key(p1.getPrimaryName().getSurname())
            if p1.getGender() == RelLib.Person.male:
                if males.has_key(key):
                    males[key].append(p1)
                else:
                    males[key] = [p1]
            else:
                if females.has_key(key):
                    females[key].append(p1)
                else:
                    females[key] = [p1]
                
        length = len(self.person_list)

        num = 0
        for p1 in self.person_list:
            if num % 25 == 0:
                self.progress_update((float(num)/float(length))*100)
            num = num + 1

            key = self.gen_key(p1.getPrimaryName().getSurname())
            if p1.getGender() == RelLib.Person.male:
                remaining = males[key]
            else:
                remaining = females[key]

            index = 0
            for p2 in remaining:
                index = index + 1
                if p1 == p2:
                    continue
                chance = self.compare_people(p1,p2)
                if chance >= thresh:
                    if self.map.has_key(p1):
                        val = self.map[p1]
                        if val[1] > chance:
                            self.map[p1] = (p2,chance)
                    else:
                        self.map[p1] = (p2,chance)

        self.list = self.map.keys()[:]
        self.list.sort(by_id)
        self.length = len(self.list)
        self.topWin.destroy()

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def show(self):
        self.topDialog = GladeXML(self.glade_file,"merge")
        self.merge_btn = self.topDialog.get_widget("merge_btn")
        self.next_btn = self.topDialog.get_widget("next_btn")
        self.altname = self.topDialog.get_widget("altname")
        
        self.topDialog.signal_autoconnect({
            "on_next_clicked" : on_next_clicked,
            "on_merge_clicked" : on_merge_clicked,
            "destroy_passed_object" : update_and_destroy
            })

        if len(self.map) > 0:
            top = self.topDialog.get_widget("merge")
            top.set_data("MergeObject",self)
            top.show()
            top.set_data("t",self)
            self.load_next()
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def merge(self):
        self.merge_btn.set_sensitive(0)
        utils.modified()
        if self.topDialog.get_widget("bname2").get_active():
            if self.altname.get_active():
                self.mergee.addAlternateName(self.mergee.getPrimaryName())
            self.mergee.setPrimaryName(self.merger.getPrimaryName())
        else:
            if self.altname.get_active():
                self.mergee.addAlternateName(self.merger.getPrimaryName())
        if self.topDialog.get_widget("bbirth2").get_active():
            self.mergee.getBirth().setDate(self.merger.getBirth().getDate())
        if self.topDialog.get_widget("bplace2").get_active():
            self.mergee.getBirth().setPlace(self.merger.getBirth().getPlace())
        if self.topDialog.get_widget("death2").get_active():
            self.mergee.getDeath().setDate(self.merger.getDeath().getDate())
        if self.topDialog.get_widget("dplace2").get_active():
            self.mergee.getDeath().setPlace(self.merger.getDeath().getPlace())

        if self.topDialog.get_widget("bfather2").get_active():
            orig_family = self.mergee.getMainFamily()
            if orig_family:
                orig_family.removeChild(self.mergee)
            
            source_family = self.merger.getMainFamily()
            self.mergee.setMainFamily(source_family)

            if source_family:
                if self.merger in source_family.getChildList():
                    source_family.removeChild(self.merger)
                if self.mergee not in source_family.getChildList():
                    source_family.addChild(self.mergee)
        else:
            source_family = self.merger.getMainFamily()
            if source_family:
                source_family.removeChild(self.merger)
                self.merger.setMainFamily(None)

        self.merge_families()

        for event in self.merger.getEventList():
            self.mergee.addEvent(event)
        for photo in self.merger.getPhotoList():
            self.mergee.addPhoto(photo)
        for name in self.merger.getAlternateNames():
            self.mergee.addAlternateName(name)
        if self.mergee.getNickName() == "":
            self.mergee.setNickName(self.merger.getNickName())
        if self.merger.getNote() != "":
            old_note = self.mergee.getNote()
            if old_note:
                old_note = old_note + "\n\n"
            self.mergee.setNote(old_note + self.merger.getNote())

        del self.db.getPersonMap()[self.merger.getId()]
            
        self.removed[self.merger] = self.mergee
        self.removed[self.mergee] = self.mergee

        checker = Check.CheckIntegrity(self.db)
        checker.cleanup_empty_families(1)
        checker.check_for_broken_family_links()
        self.load_next()

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def find_family(self,family):
        if self.mergee.getGender() == RelLib.Person.male:
            mother = family.getMother()
            father = self.mergee
        else:
            father = family.getFather()
            mother = self.mergee

        for myfamily in self.family_list:
            if myfamily.getFather() == father and \
               myfamily.getMother() == mother:
                return myfamily

        return None

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def merge_families(self):
        
        family_num = 0
        mylist = self.merger.getFamilyList()[:]
        for src_family in mylist:
            
            family_num = family_num + 1

            if not self.db.getFamilyMap().has_key(src_family.getId()):
                continue
            if src_family in self.mergee.getFamilyList():
                continue

            tgt_family = self.find_family(src_family)


            #
            # This is the case where a new family to be added to the
            # mergee as a result of the merge already exists as a
            # family.  In this case, we need to remove the old source
            # family (with the pre-merge identity of the mergee) from
            # both the parents
            #
            if tgt_family in self.mergee.getFamilyList():
                if tgt_family.getFather() != None and \
                   src_family in tgt_family.getFather().getFamilyList():
                    tgt_family.getFather().removeFamily(src_family)
                if tgt_family.getMother() != None and \
                   src_family in tgt_family.getMother().getFamilyList():
                    tgt_family.getMother().removeFamily(src_family)

                # copy children from source to target

                # delete the old source family
                del self.db.getFamilyMap()[src_family.getId()]

                continue
            
            #
            # This is the case where a new family to be added 
            # and it is not already in the list.
            #

            if tgt_family:

                # tgt_family a duplicate family, transfer children from
                # the merger family, and delete the family.  Not sure
                # what to do about marriage/divorce date/place yet.

                # transfer child to new family, alter children to
                # point to the correct family
                
                for child in src_family.getChildList():
                    if child not in tgt_family.getChildList():
                        tgt_family.addChild(child)
                        if child.getMainFamily() == src_family:
                            child.setMainFamily(tgt_family)
                        else:
                            index = 0
                            for fam in child.getAltFamilies():
                                if fam == src_family:
                                    child.getAltFamilies()[index] = tgt_family
                                index = index + 1

                # add family events from the old to the new
                for event in src_family.getEventList():
                    tgt_family.addEvent(event)

                # add mariage information
                marriage = src_family.getMarriage()
                if marriage:
                    other_marriage = tgt_family.getMarriage()
                    if other_marriage != None:
                        if other_marriage.getPlace() == "":
                            other_marriage.setPlace(marriage.getPlace())
                        if other_marriage.getDate() == "":
                            other_marriage.setDate(marriage.getDate())
                    else:
                        tgt_family.setMarriage(marriage)

                # add divorce information
                divorce = src_family.getDivorce()
                if divorce != None:
                    other_divorce = tgt_family.getDivorce()
                    if other_divorce != None:
                        if other_divorce.getPlace() == "":
                            other_divorce.setPlace(divorce.getPlace())
                        if other_divorce.getDate() == "":
                            other_divorce.setDate(divorce.getDate())
                    else:
                        tgt_family.setDivorce(divorce)

                # change parents of the family to point to the new
                # family
                
                if src_family.getFather():
                    src_family.getFather().removeFamily(src_family)
                    src_family.getFather().addFamily(tgt_family)

                if src_family.getMother():
                    src_family.getMother().removeFamily(src_family)
                    src_family.getMother().addFamily(tgt_family)

                del self.db.getFamilyMap()[src_family.getId()]
            else:
                self.remove_marriage(src_family,self.merger)
                if src_family not in self.mergee.getFamilyList():
                    self.mergee.addFamily(src_family)
                    if self.mergee.getGender() == RelLib.Person.male:
                        src_family.setFather(self.mergee)
                    else:
                        src_family.setMother(self.mergee)

        # a little debugging here
        
        for fam in self.db.getFamilyMap().values():
            name = self.merger.getPrimaryName().getName()
            if self.merger in fam.getChildList():
                fam.removeChild(self.merger)
                fam.addChild(self.mergee)
            if self.merger == fam.getFather():
                fam.setFather(self.mergee)
            if self.merger == fam.getMother():
                fam.setMother(self.mergee)
                
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def remove_marriage(self,family,person):
        if not person:
            return
        index = 0
        for fam in person.getFamilyList():
            if fam == family:
                del person.getFamilyList()[index]
                return
            index = index + 1

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def load_next(self):

        if self.length == 0:
            return

        done = 0
        while not done:
            person1 = self.list[self.index]
            self.index = self.index + 1
            if self.index > len(self.list):
                return
            if self.removed.has_key(person1):
                continue
            (person2,val) = self.map[person1]
            if self.removed.has_key(person2):
                continue
            done = 1

        label_text = "Merge %d of %d" % (self.index,self.length)
        self.topDialog.get_widget("progress").set_text(label_text)
        f1 = person1.getMainFamily()
        f2 = person2.getMainFamily()
        
        name1 = person1.getPrimaryName().getName()
        death1 = person1.getDeath().getDate()
        dplace1 = person1.getDeath().getPlace()
        birth1 = person1.getBirth().getDate()
        bplace1 = person1.getBirth().getPlace()

        name2 = person2.getPrimaryName().getName()
        death2 = person2.getDeath().getDate()
        dplace2 = person2.getDeath().getPlace()
        birth2 = person2.getBirth().getDate()
        bplace2 = person2.getBirth().getPlace()

        if f2 and not f1:
            self.topDialog.get_widget("bfather2").set_active(1)
        else:
            self.topDialog.get_widget("bfather1").set_active(1)
            
        if f1 and f1.getFather():
            father1 = f1.getFather().getPrimaryName().getName() 
        else:
            father1 = ""

        if f1 and f1.getMother():
            mother1 = f1.getMother().getPrimaryName().getName()
        else:
            mother1 = ""

        if f2 and f2.getFather():
            father2 = f2.getFather().getPrimaryName().getName()
        else:
            father2 = ""

        if f2 and f2.getMother():
            mother2 = f2.getMother().getPrimaryName().getName()
        else:
            mother2 = ""

        label1 = "%s (%s)" % (_("First Person"),str(person1.getId()))
        label2 = "%s (%s)" % (_("Second Person"),str(person2.getId()))
        
        self.topDialog.get_widget("PersonFrame1").set_label(label1)
        self.topDialog.get_widget("PersonFrame2").set_label(label2)
        self.topDialog.get_widget("name1_text").set_text(name1)
        self.topDialog.get_widget("name1_text").set_position(0)
        self.topDialog.get_widget("name2_text").set_text(name2)
        self.topDialog.get_widget("name2_text").set_position(0)

        self.topDialog.get_widget("bname1").set_active(1)

        self.topDialog.get_widget("birth1_text").set_text(birth1)
        self.topDialog.get_widget("birth1_text").set_position(0)
        self.topDialog.get_widget("birth2_text").set_text(birth2)
        self.topDialog.get_widget("birth2_text").set_position(0)
        if birth2 and not birth1:
            self.topDialog.get_widget("bbirth2").set_active(1)
        else:
            self.topDialog.get_widget("bbirth1").set_active(1)

        self.topDialog.get_widget("bplace1_text").set_text(bplace1)
        self.topDialog.get_widget("bplace1_text").set_position(0)
        self.topDialog.get_widget("bplace2_text").set_text(bplace2)
        self.topDialog.get_widget("bplace2_text").set_position(0)
        if bplace2 and not bplace1:
            self.topDialog.get_widget("bplace2").set_active(1)
        else:
            self.topDialog.get_widget("bplace1").set_active(1)

        self.topDialog.get_widget("death1_text").set_text(death1)
        self.topDialog.get_widget("death1_text").set_position(0)
        self.topDialog.get_widget("death2_text").set_text(death2)
        self.topDialog.get_widget("death2_text").set_position(0)
        if death2 and not death1:
            self.topDialog.get_widget("death2").set_active(1)
        else:
            self.topDialog.get_widget("death1").set_active(1)

        self.topDialog.get_widget("dplace1_text").set_text(dplace1)
        self.topDialog.get_widget("dplace1_text").set_position(0)
        self.topDialog.get_widget("dplace2_text").set_text(dplace2)
        self.topDialog.get_widget("dplace2_text").set_position(0)
        if dplace2 and not dplace1:
            self.topDialog.get_widget("dplace2").set_active(1)
        else:
            self.topDialog.get_widget("dplace1").set_active(1)

        self.topDialog.get_widget("father1").set_text(father1)
        self.topDialog.get_widget("father1").set_position(0)
        self.topDialog.get_widget("father2").set_text(father2)
        self.topDialog.get_widget("father2").set_position(0)
        self.topDialog.get_widget("mother1").set_text(mother1)
        self.topDialog.get_widget("mother1").set_position(0)
        self.topDialog.get_widget("mother2").set_text(mother2)
        self.topDialog.get_widget("mother2").set_position(0)

        p1list = person1.getFamilyList()
        p2list = person2.getFamilyList()
        
        length = min(len(p1list),3)
        self.topDialog.get_widget("spouse1").clear()
        for index in range(0,3):
            if index < length and p1list[index]:
                if person1.getGender() == RelLib.Person.male:
                    spouse = p1list[index].getMother()
                    x = p1list[index].getFather()
                else:
                    spouse = p1list[index].getFather()
                    x = p1list[index].getMother()

                if spouse == None:
                    name = "unknown"
                else:
                    name = spouse.getPrimaryName().getName() + \
                           " (" + str(spouse.getId()) + ")"
                self.topDialog.get_widget("spouse1").append([name])

        length = min(len(p2list),3)
        self.topDialog.get_widget("spouse2").clear()
        for index in range(0,3):
            if index < length and p2list[index]:
                if person2.getGender() == RelLib.Person.male:
                    spouse = p2list[index].getMother()
                    x = p2list[index].getFather()
                else:
                    spouse = p2list[index].getFather()
                    x = p2list[index].getMother()

                if spouse == None:
                    name = "unknown"
                else:
                    name = spouse.getPrimaryName().getName()  + \
                           " (" + str(spouse.getId()) + ")"
                self.topDialog.get_widget("spouse2").append([name])

        self.mergee = person1
        self.merger = person2

        self.topDialog.get_widget("chance").set_text(str(val))

        if len(self.list) > self.index+1:
            self.merge_btn.set_sensitive(1)
            self.next_btn.set_sensitive(1)
        else:
            self.merge_btn.set_sensitive(0)
            self.next_btn.set_sensitive(0)

        if name1 != name2:
            self.altname.set_sensitive(1)
            self.altname.set_active(1)
        else:
            self.altname.set_sensitive(0)
            self.altname.set_active(0)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def list_reduce(self,list1,list2):
        value = 0
        for name in list1:
            for name2 in list2:
                if is_initial(name) and name[0] == name2[0]:
                    value = value + 0.25
                    break
                if is_initial(name2) and name2[0] == name[0]:
                    value = value + 0.25
                    break
                if name == name2:
                    value = value + 0.5
                    break
                if name[0] == name2[0] and self.name_compare(name,name2):
                    value = value + 0.25
                    break
        if value == 0:
            return -1
        else:
            return min(value,1)
        
    #-----------------------------------------------------------------
    #
    #
    #
    #-----------------------------------------------------------------
    def gen_key(self,val):
        if self.use_soundex:
            return soundex.soundex(val)
        else:
            return val

    #-----------------------------------------------------------------
    #
    #
    #
    #-----------------------------------------------------------------
    def name_compare(self,s1,s2):
        if self.use_soundex:
            return soundex.compare(s1,s2)
        else:
            return s1 == s2

    #-----------------------------------------------------------------
    #
    #
    #
    #-----------------------------------------------------------------
    def date_match(self,date1,date2):
        if date1.getDate() == "" or date2.getDate() == "":
            return 0
        if date1.getDate() == date2.getDate():
            return 1

        if date1.isRange() or date2.isRange():
            return self.range_compare(date1,date2)

        date1 = date1.get_start_date()
        date2 = date2.get_start_date()
        
        if date1.getYear() == date2.getYear():
            if date1.getMonth() == date2.getMonth():
                return 0.75
            if date1.getMonth() == -1 or date2.getMonth() == -1:
                return 0.75
            else:
                return -1
        else:
            return -1

    #-----------------------------------------------------------------
    #
    #
    #
    #-----------------------------------------------------------------
    def range_compare(self,date1,date2):
        if date1.isRange() and date2.isRange():
            if date1.get_start_date() >= date2.get_start_date() and \
               date1.get_start_date() <= date2.get_stop_date() or \
               date2.get_start_date() >= date1.get_start_date() and \
               date2.get_start_date() <= date1.get_stop_date() or \
               date1.get_stop_date() >= date2.get_start_date() and \
               date1.get_stop_date() <= date2.get_stop_date() or \
               date2.get_stop_date() >= date1.get_start_date() and \
               date2.get_stop_date() <= date1.get_stop_date():
                return 0.5
            else:
                return -1
        elif date2.isRange():
            if date1.get_start_date() >= date2.get_start_date() and \
               date1.get_start_date() <= date2.get_stop_date():
                return 0.5
            else:
                return -1
        else:
            if date2.get_start_date() >= date1.get_start_date() and \
               date2.get_start_date() <= date1.get_stop_date():
                return 0.5
            else:
                return -1

    #-----------------------------------------------------------------
    #
    #
    #
    #-----------------------------------------------------------------
    def name_match(self,name,name1):

        if not name1 or not name:
            return 0
    
        srn1 = name.getSurname()
        sfx1 = name.getSuffix()
        srn2 = name1.getSurname()
        sfx2 = name1.getSuffix()

        if not self.name_compare(srn1,srn2):
            return -1
        if sfx1 != sfx2:
            if sfx1 != "" and sfx2 != "":
                return -1

        if name.getFirstName() == name1.getFirstName():
            return 1
        else:
            list1 = string.split(name.getFirstName())
            list2 = string.split(name1.getFirstName())

            if len(list1) < len(list2):
                return self.list_reduce(list1,list2)
            else:
                return self.list_reduce(list2,list1)
            
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def place_match(self,name1,name2):

        if name1 == "" or name2 == "":
            return 0
        if name1 == name2:
            return 1

        list1 = string.split(string.replace(name1,","," "))
        list2 = string.split(string.replace(name2,","," "))

        value = 0
        for name in list1:
            for name2 in list2:
                if name == name2:
                    value = value + 0.5
                    break
                if name[0] == name2[0] and self.name_compare(name,name2):
                    value = value + 0.25
                    break
        if value == 0:
            return -1
        else:
            return min(value,1)
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def compare_people(self,p1,p2):

        name1 = p1.getPrimaryName()
        name2 = p2.getPrimaryName()
                
        chance = self.name_match(name1,name2)
        if chance == -1  :
            return -1

        birth1 = p1.getBirth()
        death1 = p1.getDeath()
        birth2 = p2.getBirth()
        death2 = p2.getDeath()

        value = self.date_match(birth1.getDateObj(),birth2.getDateObj()) 
        if value == -1 :
            return -1
        chance = chance + value

        value = self.date_match(death1.getDateObj(),death2.getDateObj()) 
        if value == -1 :
            return -1
        chance = chance + value

        value = self.place_match(birth1.getPlace(),birth2.getPlace()) 
        if value == -1 :
            return -1
        chance = chance + value

        value = self.place_match(death1.getPlace(),death2.getPlace()) 
        if value == -1 :
            return -1
        chance = chance + value

        ancestors = []
        ancestors_of(p1,ancestors)
        if p2 in ancestors:
            return -1

        ancestors = []
        ancestors_of(p2,ancestors)
        if p1 in ancestors:
            return -1
        
        f1 = p1.getMainFamily()
        f2 = p2.getMainFamily()

        if f1 and f2:
            dad1 = get_name_obj(f1.getFather())
            dad2 = get_name_obj(f2.getFather())
            
            value = self.name_match(dad1,dad2)
            
            if value == -1:
                return -1

            chance = chance + value
            
            mom1 = get_name_obj(f1.getMother())
            mom2 = get_name_obj(f2.getMother())

            value = self.name_match(mom1,mom2)
            if value == -1:
                return -1
            
            chance = chance + value

        for f1 in p1.getFamilyList():
            for f2 in p2.getFamilyList():
                if p1.getGender() == RelLib.Person.female:
                    father1 = f1.getFather()
                    father2 = f2.getFather()
                    if father1 and father2:
                        if father1 == father2:
                            chance = chance + 1
                        else:
                            fname1 = get_name_obj(father1)
                            fname2 = get_name_obj(father2)
                            value = self.name_match(fname1,fname2)
                            if value != -1:
                                chance = chance + value
                else:
                    mother1 = f1.getMother()
                    mother2 = f2.getMother()
                    if mother1 and mother2:
                        if mother1 == mother2:
                            chance = chance + 1
                        else:
                            mname1 = get_name_obj(mother1)
                            mname2 = get_name_obj(mother2)
                            value = self.name_match(mname1,mname2)
                            if value != -1:
                                chance = chance + value

        return chance

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback):
    mergeObj = Merge(database,callback)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_description():
    return _("Searches the entire database, looking for individual entries that may represent the same person")

def get_name():
    return _("Database Processing/Merge people")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def update_and_destroy(obj):
    obj.get_data("t").update(1)
    utils.destroy_passed_object(obj)
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_next_clicked(obj):
    myObject = obj.get_data("MergeObject")
    myObject.load_next()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_merge_clicked(obj):
    myObject = obj.get_data("MergeObject")
    myObject.merge()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_id(p1,p2):
    return cmp(p1.getId(),p2.getId())
