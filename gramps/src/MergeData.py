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

import RelLib
import soundex
import intl
import utils
import Config
import const
_ = intl.gettext

import string

import gtk
import gnome.ui 
import libglade

class MergePeople:

    def __init__(self,db,person1,person2,update):
        self.db = db
        self.p1 = person1
        self.p2 = person2
        self.update = update

        self.glade = libglade.GladeXML(const.mergeFile,"merge")
        self.top = self.glade.get_widget("merge")
        self.altname = self.glade.get_widget("altname")
        self.altbirth = self.glade.get_widget("altbirth")
        self.altdeath = self.glade.get_widget("altdeath")
        self.family_list = db.getFamilyMap().values()

        self.glade.signal_autoconnect({
            "on_merge_clicked" : self.on_merge_clicked,
            "on_next_clicked" : self.on_merge_edit_clicked,
            "destroy_passed_object" : utils.destroy_passed_object,
            })

        label_text = "Merge %s and %s" % (Config.nameof(person1),Config.nameof(person2))
        self.glade.get_widget("progress").set_text(label_text)
        f1 = person1.getMainFamily()
        f2 = person2.getMainFamily()
        
        name1 = Config.nameof(person1)
        death1 = person1.getDeath().getDate()
        dplace1 = self.place_name(person1.getDeath())
        birth1 = person1.getBirth().getDate()
        bplace1 = self.place_name(person1.getBirth())

        name2 = Config.nameof(person2)
        death2 = person2.getDeath().getDate()
        dplace2 = self.place_name(person2.getDeath())
        birth2 = person2.getBirth().getDate()
        bplace2 = self.place_name(person2.getBirth())

        if f2 and not f1:
            self.glade.get_widget("bfather2").set_active(1)
        else:
            self.glade.get_widget("bfather1").set_active(1)
            
        if f1:
            father1 = name_of(f1.getFather())
            mother1 = name_of(f1.getMother())
        else:
            father1 = ""
            mother1 = ""

        if f2:
            father2 = name_of(f2.getFather())
            mother2 = name_of(f2.getMother())
        else:
            father2 = ""
            mother2 = ""

        label1 = "%s (%s)" % (_("First Person"),person1.getId())
        label2 = "%s (%s)" % (_("Second Person"),person2.getId())
        
        self.glade.get_widget("PersonFrame1").set_label(label1)
        self.glade.get_widget("PersonFrame2").set_label(label2)
        self.glade.get_widget("name1_text").set_text(name1)
        self.glade.get_widget("name1_text").set_position(0)
        self.glade.get_widget("name2_text").set_text(name2)
        self.glade.get_widget("name2_text").set_position(0)

        self.bname1 = self.glade.get_widget("bname1")
        self.bname1.set_active(1)

        self.glade.get_widget("birth1_text").set_text(birth1)
        self.glade.get_widget("birth1_text").set_position(0)
        self.glade.get_widget("birth2_text").set_text(birth2)
        self.glade.get_widget("birth2_text").set_position(0)
        self.glade.get_widget("bplace1_text").set_text(bplace1)
        self.glade.get_widget("bplace1_text").set_position(0)
        self.glade.get_widget("bplace2_text").set_text(bplace2)
        self.glade.get_widget("bplace2_text").set_position(0)

        if not birth1 and not bplace1 and birth2 or bplace2:
            self.glade.get_widget('bbirth2').set_active(1)
        else:
            self.glade.get_widget('bbirth1').set_active(1)

        if not death1 and not dplace1 and death2 or dplace2:
            self.glade.get_widget('death2').set_active(1)
        else:
            self.glade.get_widget('death1').set_active(1)

        self.glade.get_widget("death1_text").set_text(death1)
        self.glade.get_widget("death1_text").set_position(0)
        self.glade.get_widget("dplace1_text").set_text(dplace1)
        self.glade.get_widget("dplace1_text").set_position(0)

        self.glade.get_widget("death2_text").set_text(death2)
        self.glade.get_widget("death2_text").set_position(0)
        self.glade.get_widget("dplace2_text").set_text(dplace2)
        self.glade.get_widget("dplace2_text").set_position(0)

        self.glade.get_widget("father1").set_text(father1)
        self.glade.get_widget("father1").set_position(0)
        self.glade.get_widget("father2").set_text(father2)
        self.glade.get_widget("father2").set_position(0)
        self.glade.get_widget("mother1").set_text(mother1)
        self.glade.get_widget("mother1").set_position(0)
        self.glade.get_widget("mother2").set_text(mother2)
        self.glade.get_widget("mother2").set_position(0)

        p1list = person1.getFamilyList()
        p2list = person2.getFamilyList()
        
        length = min(len(p1list),3)
        self.glade.get_widget("spouse1").clear()
        for index in range(0,3):
            if index < length and p1list[index]:
                if person1.getGender() == RelLib.Person.male:
                    spouse = p1list[index].getMother()
                else:
                    spouse = p1list[index].getFather()

                if spouse == None:
                    name = "unknown"
                else:
                    name = "%s (%s)" % (Config.nameof(spouse),spouse.getId())
                self.glade.get_widget("spouse1").append([name])

        length = min(len(p2list),3)
        self.glade.get_widget("spouse2").clear()
        for index in range(0,3):
            if index < length and p2list[index]:
                if person2.getGender() == RelLib.Person.male:
                    spouse = p2list[index].getMother()
                else:
                    spouse = p2list[index].getFather()

                if spouse == None:
                    name = "unknown"
                else:
                    name = "%s (%s)" % (Config.nameof(spouse),spouse.getId())
                self.glade.get_widget("spouse2").append([name])

        if name1 != name2:
            self.altname.set_sensitive(1)
            self.altname.set_active(1)
        else:
            self.altname.set_sensitive(0)
            self.altname.set_active(0)

        if not birth1 and not bplace1 or not birth2 and not bplace2:
            self.altbirth.set_active(0)
        else:
            self.altbirth.set_active(1)

        if not death1 and not dplace1 or not death2 and not dplace2:
            self.altdeath.set_active(0)
        else:
            self.altdeath.set_active(1)

    def place_name(self,event):
        place = event.getPlace()
        if place:
            return "%s (%s)" % (place.get_title(),place.getId())
        else:
            return ""

    def on_merge_edit_clicked(self,obj):
        import EditPerson
        self.on_merge_clicked(obj)
        EditPerson.EditPerson(self.p1,self.db,self.update)

    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def on_merge_clicked(self,obj):
        utils.modified()

        for name in self.p2.getAlternateNames():
            self.p1.addAlternateName(name)
        for event in self.p2.getEventList():
            self.p1.addEvent(event)

        if self.bname1.get_active():
            if self.altname.get_active():
                self.p1.addAlternateName(self.p2.getPrimaryName())
        else:
            if self.altname.get_active():
                self.p1.addAlternateName(self.p1.getPrimaryName())
            self.p1.setPrimaryName(self.p2.getPrimaryName())

        alt = self.glade.get_widget("altbirth").get_active()
        if self.glade.get_widget("bbirth2").get_active():
            if alt:
                event = self.p1.getBirth()
                event.setName("Alternate Birth")
                self.p1.addEvent(event)
            self.p1.setBirth(self.p2.getBirth())
        else:
            if alt:
                event = self.p2.getBirth()
                event.setName("Alternate Birth")
                self.p1.addEvent(event)

        alt = self.glade.get_widget("altdeath").get_active()
        if self.glade.get_widget("bbirth2").get_active():
            if alt:
                event = self.p1.getDeath()
                event.setName("Alternate Death")
                self.p1.addEvent(event)
            self.p1.setDeath(self.p2.getDeath())
        else:
            if alt:
                event = self.p2.getDeath()
                event.setName("Alternate Death")
                self.p1.addEvent(event)
            
        if self.glade.get_widget("bfather2").get_active():
            orig_family = self.p1.getMainFamily()
            if orig_family:
                orig_family.removeChild(self.p1)
            
            source_family = self.p2.getMainFamily()
            self.p1.setMainFamily(source_family)

            if source_family:
                if self.p2 in source_family.getChildList():
                    source_family.removeChild(self.p2)
                if self.p1 not in source_family.getChildList():
                    source_family.addChild(self.p1)
        else:
            source_family = self.p2.getMainFamily()
            if source_family:
                source_family.removeChild(self.p2)
                self.p2.setMainFamily(None)

        self.merge_families()

        for photo in self.p2.getPhotoList():
            self.p1.addPhoto(photo)

        if self.p1.getNickName() == "":
            self.p1.setNickName(self.p2.getNickName())
        if self.p2.getNote() != "":
            old_note = self.p1.getNote()
            if old_note:
                old_note = old_note + "\n\n"
            self.p1.setNote(old_note + self.p2.getNote())

        del self.db.getPersonMap()[self.p2.getId()]
        self.update(self.p2)
        utils.destroy_passed_object(self.top)
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def find_family(self,family):
        if self.p1.getGender() == RelLib.Person.male:
            mother = family.getMother()
            father = self.p1
        else:
            father = family.getFather()
            mother = self.p1

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
        mylist = self.p2.getFamilyList()[:]
        for src_family in mylist:
            
            family_num = family_num + 1

            if not self.db.getFamilyMap().has_key(src_family.getId()):
                continue
            if src_family in self.p1.getFamilyList():
                continue

            tgt_family = self.find_family(src_family)


            #
            # This is the case where a new family to be added to the
            # p1 as a result of the merge already exists as a
            # family.  In this case, we need to remove the old source
            # family (with the pre-merge identity of the p1) from
            # both the parents
            #
            if tgt_family in self.p1.getFamilyList():
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
                # the p2 family, and delete the family.  Not sure
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
                self.remove_marriage(src_family,self.p2)
                if src_family not in self.p1.getFamilyList():
                    self.p1.addFamily(src_family)
                    if self.p1.getGender() == RelLib.Person.male:
                        src_family.setFather(self.p1)
                    else:
                        src_family.setMother(self.p1)

        # a little debugging here
        
        for fam in self.db.getFamilyMap().values():
            name = self.p2.getPrimaryName().getName()
            if self.p2 in fam.getChildList():
                fam.removeChild(self.p2)
                fam.addChild(self.p1)
            if self.p2 == fam.getFather():
                fam.setFather(self.p1)
            if self.p2 == fam.getMother():
                fam.setMother(self.p1)
                
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


def compare_people(p1,p2):

    name1 = p1.getPrimaryName()
    name2 = p2.getPrimaryName()
                
    chance = name_match(name1,name2)
    if chance == -1  :
        return -1

    birth1 = p1.getBirth()
    death1 = p1.getDeath()
    birth2 = p2.getBirth()
    death2 = p2.getDeath()

    value = date_match(birth1.getDateObj(),birth2.getDateObj()) 
    if value == -1 :
        return -1
    chance = chance + value

    value = date_match(death1.getDateObj(),death2.getDateObj()) 
    if value == -1 :
        return -1
    chance = chance + value

    value = place_match(birth1.getPlace(),birth2.getPlace()) 
    if value == -1 :
        return -1
    chance = chance + value

    value = place_match(death1.getPlace(),death2.getPlace()) 
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

    if f1 and f1.getFather():
        dad1 = f1.getFather().getPrimaryName()
    else:
        dad1 = None

    if f2 and f2.getFather():
        dad2 = f2.getFather().getPrimaryName()
    else:
        dad2 = None
        
    value = name_match(dad1,dad2)
            
    if value == -1:
        return -1

    chance = chance + value
            
    if f1 and f1.getMother():
        mom1 = f1.getMother().getPrimaryName()
    else:
        mom1 = None

    if f2 and f2.getMother():
        mom2 = f2.getMother().getPrimaryName()
    else:
        mom2 = None

    value = name_match(mom1,mom2)
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
                        fname1 = Config.nameof(father1)
                        fname2 = Config.nameof(father2)
                        value = name_match(fname1,fname2)
                        if value != -1:
                            chance = chance + value
            else:
                mother1 = f1.getMother()
                mother2 = f2.getMother()
                if mother1 and mother2:
                    if mother1 == mother2:
                        chance = chance + 1
                    else:
                        mname1 = Config.nameof(mother1)
                        mname2 = Config.nameof(mother2)
                        value = name_match(mname1,mname2)
                        if value != -1:
                            chance = chance + value

    return chance


#-----------------------------------------------------------------
#
#
#
#-----------------------------------------------------------------
def name_compare(s1,s2):
    return s1 == s2

#-----------------------------------------------------------------
#
#
#
#-----------------------------------------------------------------
def date_match(date1,date2):
    if date1.getDate() == "" or date2.getDate() == "":
        return 0
    if date1.getDate() == date2.getDate():
        return 1
    
    if date1.isRange() or date2.isRange():
        return range_compare(date1,date2)

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
def range_compare(date1,date2):
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

def name_match(name,name1):

    if not name1 or not name:
        return 0
    
    srn1 = name.getSurname()
    sfx1 = name.getSuffix()
    srn2 = name1.getSurname()
    sfx2 = name1.getSuffix()

    if not name_compare(srn1,srn2):
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
            return list_reduce(list1,list2)
        else:
            return list_reduce(list2,list1)

#---------------------------------------------------------------------
#
#
#
#---------------------------------------------------------------------
def list_reduce(list1,list2):
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
            if name[0] == name2[0] and name_compare(name,name2):
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
def place_match(p1,p2):
    if p1 == p2:
        return 1
    
    if p1 == None:
        name1 = ""
    else:
        name1 = p1.get_title()
        
    if p2 == None:
        name2 = ""
    else:
        name2 = p2.get_title()
        
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
            if name[0] == name2[0] and name_compare(name,name2):
                value = value + 0.25
                break
    if value == 0:
        return -1
    else:
        return min(value,1)

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

def ancestors_of(p1,list):
    if p1 == None:
        return
    list.append(p1)
    f1 = p1.getMainFamily()
    if f1 != None:
        ancestors_of(f1.getFather(),list)
        ancestors_of(f1.getMother(),list)

def name_of(p):
    if not p:
        return ""
    return "%s (%s)" % ( Config.nameof(p),p.getId())

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class MergePlaces:
    def __init__(self,database,place1,place2,update):
        self.db = database
        self.p1 = place1
        self.p2 = place2
        self.update = update

        self.glade = libglade.GladeXML(const.mergeFile,"merge_places")
        self.top = self.glade.get_widget("merge_places")
        self.glade.get_widget("title1_text").set_text(place1.get_title())
        self.glade.get_widget("title2_text").set_text(place2.get_title())
        self.t3 = self.glade.get_widget("title3_text")
        self.t3.set_text(place1.get_title())
        
        self.glade.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_merge_places_clicked" : self.on_merge_places_clicked,
            })
        self.top.show()

    def on_merge_places_clicked(self,obj):
        if self.glade.get_widget("title2").get_active():
            self.p1.set_title(self.p2.get_title())
        elif self.glade.get_widget("title3").get_active():
            self.p1.set_title(self.t3.get_text())
        if self.p1.get_longitude() == "" and self.p2.get_longitude() != "":
            self.p1.set_longitude(self.p2.get_longitude())
        if self.p1.get_latitude() == "" and self.p2.get_latitude() != "":
            self.p1.set_latitude(self.p2.get_latitude())
        for url in self.p2.getUrlList():
            self.p1.addUrl(url)
        for photo in self.p2.getPhotoList():
            self.p1.addPhoto(photo)
        for source in self.p2.getSourceRefList():
            self.p1.addSource(source)
        note = self.p2.getNote()
        if note != "":
            if self.p1.getNote() == "":
                self.p1.setNote(note)
            elif self.p1.getNote() != note:
                self.p1.setNote("%s\n\n%s" % (self.p1.getNote(),note))
        for l in [self.p2.get_main_location()] + self.p2.get_alternate_locations():
            if not l.is_empty():
                self.p1.add_alternate_locations(l)
        for p in self.db.getPersonMap().values():
            for event in [p.getBirth(), p.getDeath()] + p.getEventList():
                if event.getPlace() == self.p2:
                    event.setPlace(self.p1)
        for f in self.db.getFamilyMap().values():
            for event in f.getEventList():
                if event.getPlace() == self.p2:
                    event.setPlace(self.p1)
        del self.db.getPlaceMap()[self.p2.getId()]
        self.update()
        utils.modified()
        utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def new_after_edit(epo):
    pass
        
if __name__ == "__main__":
    import sys
    import ReadXML

    database = RelLib.RelDataBase()
    ReadXML.loadData(database,sys.argv[1])

    person1 = database.getPersonMap().values()[0]
    person2 = database.getPersonMap().values()[1]
    MergePeople(database,person1,person2)
    gtk.mainloop()
