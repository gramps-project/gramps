#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# GNOME
#
#-------------------------------------------------------------------------
import gtk.glade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import RelLib
import Utils
import GrampsCfg
import ListModel
import const
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Merge People
#
#-------------------------------------------------------------------------
class MergePeople:

    def __init__(self,db,person1,person2,update,ep_update=None):
        self.db = db
        self.p1 = person1
        self.p2 = person2
        self.update = update
        self.ep_update = ep_update

        self.glade = gtk.glade.XML(const.mergeFile,"merge","gramps")
        self.top = self.glade.get_widget("merge")

        Utils.set_titles(self.top,self.glade.get_widget('title'),
                         _('Merge Places'), _('Select the title for the merged place'))
        
        self.altname = self.glade.get_widget("altname")
        self.altbirth = self.glade.get_widget("altbirth")
        self.altdeath = self.glade.get_widget("altdeath")
        self.family_list = db.getFamilyMap().values()

        self.glade.signal_autoconnect({
            "on_merge_clicked" : self.on_merge_clicked,
            "on_next_clicked" : self.on_merge_edit_clicked,
            "destroy_passed_object" : Utils.destroy_passed_object,
            })

        fname = GrampsCfg.nameof(person1)
        mname = GrampsCfg.nameof(person2)

        Utils.set_titles(self.top, self.glade.get_widget('title'),
                         _("Merge %s and %s") % (fname,mname),
                         _("Merge people"))

        f1 = person1.getMainParents()
        f2 = person2.getMainParents()
        
        name1 = GrampsCfg.nameof(person1)
        death1 = person1.getDeath().getDate()
        dplace1 = self.place_name(person1.getDeath())
        birth1 = person1.getBirth().getDate()
        bplace1 = self.place_name(person1.getBirth())

        name2 = GrampsCfg.nameof(person2)
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

        self.set_field(self.glade.get_widget("id1_text"),person1.getId())
        self.set_field(self.glade.get_widget("id2_text"),person2.getId())
        self.set_field(self.glade.get_widget("name1_text"),name1)
        self.set_field(self.glade.get_widget("name2_text"),name2)

        self.bname1 = self.glade.get_widget("bname1")
        self.bname1.set_active(1)

        self.set_field(self.glade.get_widget("birth1_text"),birth1)
        self.set_field(self.glade.get_widget("birth2_text"),birth2)
        self.set_field(self.glade.get_widget("bplace1_text"),bplace1)
        self.set_field(self.glade.get_widget("bplace2_text"),bplace2)

        if ((not birth1 and not bplace1) and (birth2 or bplace2) or
            (not birth1 or not bplace1) and (birth2 and bplace2)):
            self.glade.get_widget('bbirth2').set_active(1)
        else:
            self.glade.get_widget('bbirth1').set_active(1)

        if ((not death1 and not dplace1) and (death2 or dplace2) or
            (not death1 or not dplace1) and (death2 and dplace2)):
            self.glade.get_widget('death2').set_active(1)
        else:
            self.glade.get_widget('death1').set_active(1)

        self.set_field(self.glade.get_widget("death1_text"),death1)
        self.set_field(self.glade.get_widget("dplace1_text"),dplace1)
        self.set_field(self.glade.get_widget("death2_text"),death2)
        self.set_field(self.glade.get_widget("dplace2_text"),dplace2)

        self.set_field(self.glade.get_widget("father1"),father1)
        self.set_field(self.glade.get_widget("father2"),father2)
        self.set_field(self.glade.get_widget("mother1"),mother1)
        self.set_field(self.glade.get_widget("mother2"),mother2)

        sp1_list = [('-',0,100)]
        self.sp1 = ListModel.ListModel(self.glade.get_widget('spouse1'),sp1_list)
        self.sp2 = ListModel.ListModel(self.glade.get_widget('spouse2'),sp1_list)
        
        self.build_spouse_list(person1,self.sp1)
        self.build_spouse_list(person2,self.sp2)

        if name1 != name2:
            self.altname.set_sensitive(1)
            self.altname.set_active(1)
        else:
            self.altname.set_sensitive(0)
            self.altname.set_active(0)

        if birth1 and birth2 and birth1 != birth2:
            self.altbirth.set_active(1)
        if bplace1 and bplace2 or bplace1 != bplace2:
            self.altbirth.set_active(1)
        else:
            self.altbirth.set_active(0)

        if death1 and death2 and death1 != death2:
            self.altdeath.set_active(1)
        if dplace1 and dplace2 or dplace1 != dplace2:
            self.altdeath.set_active(1)
        else:
            self.altdeath.set_active(0)

    def build_spouse_list(self,person,widget):

        widget.clear()
        for fam in person.getFamilyList():
            if person.getGender() == RelLib.Person.male:
                spouse = fam.getMother()
            else:
                spouse = fam.getFather()

            if spouse == None:
                name = "unknown"
            else:
                sname = GrampsCfg.nameof(spouse)
                name = "%s [%s]" % (sname,spouse.getId())
            widget.add([name])

    def set_field(self,widget,value):
        """Sets the string of the entry field at positions it a space 0"""
        widget.set_text(value)

    def place_name(self,event):
        place = event.getPlace()
        if place:
            return "%s (%s)" % (place.get_title(),place.getId())
        else:
            return ""

    def empty(self,junk):
        pass
    
    def on_merge_edit_clicked(self,obj):
        import EditPerson
        self.on_merge_clicked(obj)
        # This needs to be fixed to provide an update call
        EditPerson.EditPerson(self.p1,self.db,self.ep_update)

    def copy_note(self,one,two):
        if one.getNote() != two.getNote():
            one.setNote("%s\n\n%s" % (one.getNote(),two.getNote()))

    def copy_sources(self,one,two):
        slist = one.getSourceRefList()[:]
        for xsrc in two.getSourceRefList():
            for src in slist:
                if src.are_equal(xsrc):
                    break
            else:
                one.addSourceRef(xsrc)

    def on_merge_clicked(self,obj):
        Utils.modified()

        list = self.p1.getAlternateNames()[:]
        for xdata in self.p2.getAlternateNames():
            for data in list:
                if data.are_equal(xdata):
                    self.copy_note(xdata,data)
                    self.copy_sources(xdata,data)
                    break
            else:
                self.p1.addAlternateName(xdata)

        list = self.p1.getAttributeList()[:]
        for xdata in self.p2.getAttributeList():
            for data in list:
                if data.getType() == xdata.getType() and \
                   data.getValue() == xdata.getValue():
                    self.copy_note(xdata,data)
                    self.copy_sources(xdata,data)
                    break
            else:
                self.p1.addAttribute(xdata)

        list = self.p1.getEventList()[:]
        for xdata in self.p2.getEventList():
            for data in list:
                if data.are_equal(xdata):
                    self.copy_note(xdata,data)
                    self.copy_sources(xdata,data)
                    break
            else:
                self.p1.addEvent(xdata)

        list = self.p1.getUrlList()[:]
        for xdata in self.p2.getUrlList():
            for data in list:
                if data.are_equal(xdata):
                    break
            else:
                self.p1.addUrl(xdata)

        self.id2 = self.glade.get_widget("id2")
        old_id = self.p1.getId()
        if self.id2.get_active():
            self.p1.setId(self.p2.getId())
            
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
            orig_family = self.p1.getMainParents()
            if orig_family:
                orig_family.removeChild(self.p1)
                self.p1.removeAltFamily(orig_family)
           
            (source_family,mrel,frel) = self.p2.getMainParentsRel()
            self.p1.setMainParents(source_family)

            if source_family:
                if self.p2 in source_family.getChildList():
                    source_family.removeChild(self.p2)
                    self.p2.removeAltFamily(source_family)
                if self.p1 not in source_family.getChildList():
                    source_family.addChild(self.p1)
                    self.p1.addAltFamily(source_family,mrel,frel)
        else:
            source_family = self.p2.getMainParents()
            if source_family:
                source_family.removeChild(self.p2)
                self.p2.setMainParents(None)

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

        try:
            self.db.removePerson(self.p2.getId())
            self.db.personMap[self.p1.getId()] = self.p1
            self.db.buildPersonDisplay(self.p1.getId(),old_id)
        except:
            print "%s is not in the person map!" % (GrampsCfg.nameof(self.p2))
        self.update(self.p1,self.p2,old_id)
        Utils.destroy_passed_object(self.top)
        
    def find_family(self,family):
        if self.p1.getGender() == RelLib.Person.male:
            mother = family.getMother()
            father = self.p1
        else:
            father = family.getFather()
            mother = self.p1

        for myfamily in self.family_list:
            if myfamily.getFather() == father and myfamily.getMother() == mother:
                return myfamily
        return None

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

                for child in src_family.getChildList():
                    if child not in tgt_family.getChildList():
                        parents = child.getParentList()
                        tgt_family.addChild(child)
                        if child.getMainParents() == src_family:
                            child.setMainParents(tgt_family)
                        i = 0
                        for fam in parents[:]:
                            if fam[0] == src_family:
                                parents[i] = (tgt_family,fam[1],fam[2])
                            i = i + 1
                        
                # delete the old source family
                del self.db.getFamilyMap()[src_family.getId()]

                continue
            
            # This is the case where a new family to be added 
            # and it is not already in the list.

            if tgt_family:

                # tgt_family a duplicate family, transfer children from
                # the p2 family, and delete the family.  Not sure
                # what to do about marriage/divorce date/place yet.

                # transfer child to new family, alter children to
                # point to the correct family
                
                for child in src_family.getChildList():
                    if child not in tgt_family.getChildList():
                        parents = child.getParentList()
                        tgt_family.addChild(child)
                        if child.getMainParents() == src_family:
                            child.setMainParents(tgt_family)
                        i = 0
                        for fam in parents[:]:
                            if fam[0] == src_family:
                                parents[i] = (tgt_family,fam[1],fam[2])
                            i = i + 1

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
                if src_family not in self.p1.getFamilyList():
                    self.p1.addFamily(src_family)
                    if self.p1.getGender() == RelLib.Person.male:
                        src_family.setFather(self.p1)
                    else:
                        src_family.setMother(self.p1)
                self.remove_marriage(src_family,self.p2)

        # a little debugging here
        
        for fam in self.db.getFamilyMap().values():
            if self.p2 in fam.getChildList():
                fam.removeChild(self.p2)
                fam.addChild(self.p1)
            if self.p2 == fam.getFather():
                fam.setFather(self.p1)
            if self.p2 == fam.getMother():
                fam.setMother(self.p1)
            if fam.getFather() == None and fam.getMother() == None:
                self.delete_empty_family(fam)
                
    def remove_marriage(self,family,person):
        if person:
            person.removeFamily(family)
            if family.getFather() == None and family.getMother() == None:
                self.delete_empty_family(family)

    def delete_empty_family(self,family):
        for child in family.getChildList():
            if child.getMainParents() == family:
                child.setMainParents(None)
            else:
                child.removeAltFamily(family)
        self.db.deleteFamily(family)

def compare_people(p1,p2):

    name1 = p1.getPrimaryName()
    name2 = p2.getPrimaryName()
                
    chance = name_match(name1,name2)
    if chance == -1.0  :
        return -1.0

    birth1 = p1.getBirth()
    death1 = p1.getDeath()
    birth2 = p2.getBirth()
    death2 = p2.getDeath()

    value = date_match(birth1.getDateObj(),birth2.getDateObj()) 
    if value == -1.0 :
        return -1.0
    chance = chance + value

    value = date_match(death1.getDateObj(),death2.getDateObj()) 
    if value == -1.0 :
        return -1.0
    chance = chance + value

    value = place_match(birth1.getPlace(),birth2.getPlace()) 
    if value == -1.0 :
        return -1.0
    chance = chance + value

    value = place_match(death1.getPlace(),death2.getPlace()) 
    if value == -1.0 :
        return -1.0
    chance = chance + value

    ancestors = []
    ancestors_of(p1,ancestors)
    if p2 in ancestors:
        return -1.0

    ancestors = []
    ancestors_of(p2,ancestors)
    if p1 in ancestors:
        return -1.0
        
    f1 = p1.getMainParents()
    f2 = p2.getMainParents()

    if f1 and f1.getFather():
        dad1 = f1.getFather().getPrimaryName()
    else:
        dad1 = None

    if f2 and f2.getFather():
        dad2 = f2.getFather().getPrimaryName()
    else:
        dad2 = None
        
    value = name_match(dad1,dad2)
            
    if value == -1.0:
        return -1.0

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
    if value == -1.0:
        return -1.0
            
    chance = chance + value

    for f1 in p1.getFamilyList():
        for f2 in p2.getFamilyList():
            if p1.getGender() == RelLib.Person.female:
                father1 = f1.getFather()
                father2 = f2.getFather()
                if father1 and father2:
                    if father1 == father2:
                        chance = chance + 1.0
                    else:
                        fname1 = GrampsCfg.nameof(father1)
                        fname2 = GrampsCfg.nameof(father2)
                        value = name_match(fname1,fname2)
                        if value != -1.0:
                            chance = chance + value
            else:
                mother1 = f1.getMother()
                mother2 = f2.getMother()
                if mother1 and mother2:
                    if mother1 == mother2:
                        chance = chance + 1.0
                    else:
                        mname1 = GrampsCfg.nameof(mother1)
                        mname2 = GrampsCfg.nameof(mother2)
                        value = name_match(mname1,mname2)
                        if value != -1.0:
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
        return 0.0
    if date1.getDate() == date2.getDate():
        return 1.0
    
    if date1.isRange() or date2.isRange():
        return range_compare(date1,date2)

    date1 = date1.get_start_date()
    date2 = date2.get_start_date()
        
    if date1.getYear() == date2.getYear():
        if date1.getMonth() == date2.getMonth():
            return 0.75
        if not date1.getMonthValid() or not date2.getMonthValid():
            return 0.75
        else:
            return -1.0
    else:
        return -1.0

#-----------------------------------------------------------------
#
#
#
#-----------------------------------------------------------------
def range_compare(date1,date2):
    d1_start = date1.get_start_date()
    d2_start = date2.get_start_date()
    d1_stop  = date1.get_stop_date()
    d2_stop  = date2.get_stop_date()

    if date1.isRange() and date2.isRange():
        if d1_start >= d2_start and d1_start <= d2_stop or \
           d2_start >= d1_start and d2_start <= d1_stop or \
           d1_stop >= d2_start and d1_stop <= d2_stop or \
           d2_stop >= d1_start and d2_stop <= d1_stop:
            return 0.5
        else:
            return -1.0
    elif date2.isRange():
        if d1_start >= d2_start and d1_start <= d2_stop:
            return 0.5
        else:
            return -1.0
    else:
        if d2_start >= d1_start and d2_start <= d1_stop:
            return 0.5
        else:
            return -1.0

#---------------------------------------------------------------------
#
#
#
#---------------------------------------------------------------------
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

#---------------------------------------------------------------------
#
#
#
#---------------------------------------------------------------------
def ancestors_of(p1,list):
    if p1 == None:
        return
    list.append(p1)
    f1 = p1.getMainParents()
    if f1 != None:
        ancestors_of(f1.getFather(),list)
        ancestors_of(f1.getMother(),list)

#---------------------------------------------------------------------
#
#
#
#---------------------------------------------------------------------
def name_of(p):
    if not p:
        return ""
    return "%s (%s)" % (GrampsCfg.nameof(p),p.getId())

#-------------------------------------------------------------------------
#
# Merge Places
#
#-------------------------------------------------------------------------
class MergePlaces:
    """
    Merges to places into a single place. Displays a dialog box that
    allows the places to be combined into one.
    """
    def __init__(self,database,place1,place2,update):
        self.db = database
        self.p1 = place1
        self.p2 = place2
        self.update = update

        self.glade = gtk.glade.XML(const.mergeFile,"merge_places","gramps")
        self.top = self.glade.get_widget("merge_places")
        self.glade.get_widget("title1_text").set_text(place1.get_title())
        self.glade.get_widget("title2_text").set_text(place2.get_title())
        self.t3 = self.glade.get_widget("title3_text")
        self.t3.set_text(place1.get_title())
        
        self.glade.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_merge_places_clicked" : self.on_merge_places_clicked,
            })
        self.top.show()

    def on_merge_places_clicked(self,obj):
        """
        Performs the merge of the places when the merge button is clicked.
        """
        t2active = self.glade.get_widget("title2").get_active()

        old_id = self.p1.getId()
        
        if t2active:
            self.p1.set_title(self.p2.get_title())
        elif self.glade.get_widget("title3").get_active():
            self.p1.set_title(unicode(self.t3.get_text()))

        # Set longitude
        if self.p1.get_longitude() == "" and self.p2.get_longitude() != "":
            self.p1.set_longitude(self.p2.get_longitude())

        # Set latitude
        if self.p1.get_latitude() == "" and self.p2.get_latitude() != "":
            self.p1.set_latitude(self.p2.get_latitude())

        # Add URLs from P2 to P1
        for url in self.p2.getUrlList():
            self.p1.addUrl(url)

        # Copy photos from P2 to P1
        for photo in self.p2.getPhotoList():
            self.p1.addPhoto(photo)

        # Copy sources from P2 to P1
        for source in self.p2.getSourceRefList():
            self.p1.addSource(source)

        # Add notes from P2 to P1
        note = self.p2.getNote()
        if note != "":
            if self.p1.getNote() == "":
                self.p1.setNote(note)
            elif self.p1.getNote() != note:
                self.p1.setNote("%s\n\n%s" % (self.p1.getNote(),note))

        if t2active:
            list = [self.p1.get_main_location()] + self.p1.get_alternate_locations()
            self.p1.set_main_location(self.p2.get_main_location())
            for l in list:
                if not l.is_empty():
                    self.p1.add_alternate_locations(l)
        else:
            list = [self.p2.get_main_location()] + self.p2.get_alternate_locations()
            for l in list:
                if not l.is_empty():
                    self.p1.add_alternate_locations(l)

        # loop through people, changing event references to P2 to P1
        for key in self.db.getPersonKeys():
            p = self.db.getPerson(key)
            for event in [p.getBirth(), p.getDeath()] + p.getEventList():
                if event.getPlace() == self.p2:
                    event.setPlace(self.p1)

        # loop through families, changing event references to P2 to P1
        for f in self.db.getFamilyMap().values():
            for event in f.getEventList():
                if event.getPlace() == self.p2:
                    event.setPlace(self.p1)
                    
        self.db.removePlace(self.p2.getId())
        self.db.buildPlaceDisplay(self.p1.getId(),old_id)
        
        self.update(self.p1.getId())
        Utils.modified()
        Utils.destroy_passed_object(obj)

