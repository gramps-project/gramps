#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

    def __init__(self,parent,db,person1,person2,update,ep_update=None):
        self.parent = parent
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

        self.glade.signal_autoconnect({
            "on_merge_clicked" : self.on_merge_clicked,
            "on_next_clicked" : self.on_merge_edit_clicked,
            "destroy_passed_object" : Utils.destroy_passed_object,
            })

        fname = GrampsCfg.get_nameof()(person1)
        mname = GrampsCfg.get_nameof()(person2)

        Utils.set_titles(self.top, self.glade.get_widget('title'),
                         _("Merge %s and %s") % (fname,mname),
                         _("Merge people"))

        f1 = person1.get_main_parents_family_handle()
        f2 = person2.get_main_parents_family_handle()
        
        name1 = GrampsCfg.get_nameof()(person1)
        death1 = person1.get_death().get_date()
        dplace1 = self.place_name(person1.get_death())
        birth1 = person1.get_birth().get_date()
        bplace1 = self.place_name(person1.get_birth())

        name2 = GrampsCfg.get_nameof()(person2)
        death2 = person2.get_death().get_date()
        dplace2 = self.place_name(person2.get_death())
        birth2 = person2.get_birth().get_date()
        bplace2 = self.place_name(person2.get_birth())

        if f2 and not f1:
            self.glade.get_widget("bfather2").set_active(1)
        else:
            self.glade.get_widget("bfather1").set_active(1)
            
        if f1:
            father1 = name_of(f1.get_father_handle())
            mother1 = name_of(f1.get_mother_handle())
        else:
            father1 = ""
            mother1 = ""

        if f2:
            father2 = name_of(f2.get_father_handle())
            mother2 = name_of(f2.get_mother_handle())
        else:
            father2 = ""
            mother2 = ""

        self.set_field(self.glade.get_widget("id1_text"),person1.get_handle())
        self.set_field(self.glade.get_widget("id2_text"),person2.get_handle())
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
        for fam in person.get_family_handle_list():
            if person.get_gender() == RelLib.Person.male:
                spouse = fam.get_mother_handle()
            else:
                spouse = fam.get_father_handle()

            if spouse == None:
                name = "unknown"
            else:
                sname = GrampsCfg.get_nameof()(spouse)
                name = "%s [%s]" % (sname,spouse.get_handle())
            widget.add([name])

    def set_field(self,widget,value):
        """Sets the string of the entry field at positions it a space 0"""
        widget.set_text(value)

    def place_name(self,event):
        place = event.get_place_handle()
        if place:
            return "%s (%s)" % (place.get_title(),place.get_handle())
        else:
            return ""

    def empty(self,junk):
        pass
    
    def on_merge_edit_clicked(self,obj):
        import EditPerson
        self.on_merge_clicked(obj)
        # This needs to be fixed to provide an update call
        EditPerson.EditPerson(self.parent,self.p1,self.db,self.ep_update)

    def copy_note(self,one,two):
        if one.get_note() != two.get_note():
            one.set_note("%s\n\n%s" % (one.get_note(),two.get_note()))

    def copy_sources(self,one,two):
        slist = one.get_source_references()[:]
        for xsrc in two.get_source_references():
            for src in slist:
                if src.are_equal(xsrc):
                    break
            else:
                one.add_source_reference(xsrc)

    def on_merge_clicked(self,obj):
        lst = self.p1.get_alternate_names()[:]
        for xdata in self.p2.get_alternate_names():
            for data in lst:
                if data.are_equal(xdata):
                    self.copy_note(xdata,data)
                    self.copy_sources(xdata,data)
                    break
            else:
                self.p1.add_alternate_name(xdata)

        lst = self.p1.get_attribute_list()[:]
        for xdata in self.p2.get_attribute_list():
            for data in lst:
                if data.get_type() == xdata.get_type() and \
                   data.getValue() == xdata.get_value():
                    self.copy_note(xdata,data)
                    self.copy_sources(xdata,data)
                    break
            else:
                self.p1.add_attribute(xdata)

        lst = self.p1.get_event_list()[:]
        for xdata in self.p2.get_event_list():
            for data in lst:
                if data.are_equal(xdata):
                    self.copy_note(xdata,data)
                    self.copy_sources(xdata,data)
                    break
            else:
                self.p1.add_event(xdata)

        lst = self.p1.get_url_list()[:]
        for xdata in self.p2.get_url_list():
            for data in lst:
                if data.are_equal(xdata):
                    break
            else:
                self.p1.add_url(xdata)

        self.id2 = self.glade.get_widget("id2")
        old_id = self.p1.get_handle()
        if self.id2.get_active():
            self.p1.set_handle(self.p2.get_handle())
            
        if self.bname1.get_active():
            if self.altname.get_active():
                self.p1.add_alternate_name(self.p2.get_primary_name())
        else:
            if self.altname.get_active():
                self.p1.add_alternate_name(self.p1.get_primary_name())
            self.p1.set_primary_name(self.p2.get_primary_name())

        alt = self.glade.get_widget("altbirth").get_active()
        if self.glade.get_widget("bbirth2").get_active():
            if alt:
                event = self.p1.get_birth()
                event.set_name("Alternate Birth")
                self.p1.add_event(event)
            self.p1.set_birth(self.p2.get_birth())
        else:
            if alt:
                event = self.p2.get_birth()
                event.set_name("Alternate Birth")
                self.p1.add_event(event)

        alt = self.glade.get_widget("altdeath").get_active()
        if self.glade.get_widget("bbirth2").get_active():
            if alt:
                event = self.p1.get_death()
                event.set_name("Alternate Death")
                self.p1.add_event(event)
            self.p1.set_death(self.p2.get_death())
        else:
            if alt:
                event = self.p2.get_death()
                event.set_name("Alternate Death")
                self.p1.add_event(event)

        if self.glade.get_widget("bfather2").get_active():
            orig_family = self.p1.get_main_parents_family_handle()
            if orig_family:
                orig_family.remove_child_handle(self.p1)
                self.p1.remove_parent_family_handle(orig_family)
           
            (source_family,mrel,frel) = self.p2.get_main_parents_family_handle()
            self.p1.set_main_parent_family_handle(source_family)

            if source_family:
                if self.p2 in source_family.get_child_handle_list():
                    source_family.remove_child_handle(self.p2)
                    self.p2.remove_parent_family_handle(source_family)
                if self.p1 not in source_family.get_child_handle_list():
                    source_family.add_child_handle(self.p1)
                    self.p1.add_parent_family_handle(source_family.get_handle(),mrel,frel)
        else:
            source_family = self.p2.get_main_parents_family_handle()
            if source_family:
                source_family.remove_child_handle(self.p2)
                self.p2.set_main_parent_family_handle(None)

        self.merge_families()

        for photo in self.p2.get_media_list():
            self.p1.add_media_reference(photo)

        if self.p1.get_nick_name() == "":
            self.p1.set_nick_name(self.p2.get_nick_name())
            
        if self.p2.get_note() != "":
            old_note = self.p1.get_note()
            if old_note:
                old_note = old_note + "\n\n"
            self.p1.set_note(old_note + self.p2.get_note())

        try:
            self.db.remove_person(self.p2.get_handle())
            self.db.personMap[self.p1.get_handle()] = self.p1
        except:
            print "%s is not in the person map!" % (GrampsCfg.get_nameof()(self.p2))
        self.update(self.p1,self.p2,old_id)
        Utils.destroy_passed_object(self.top)
        
    def find_family(self,family):
        if self.p1.get_gender() == RelLib.Person.male:
            mother = family.get_mother_handle()
            father = self.p1.get_handle()
        else:
            father = family.get_father_handle()
            mother = self.p1.get_handle()

        for myfamily_handle in self.db.get_family_handles():
            myfamily = self.db.get_family_from_handle(myfamily_handle)
            if myfamily.get_father_handle() == father and myfamily.get_mother_handle() == mother:
                return myfamily
        return None

    def merge_families(self):
        
        family_num = 0
        mylist = self.p2.get_family_handle_list()[:]
        for src_family in mylist:
            
            family_num = family_num + 1

            if not self.db.get_family_handle_map().has_key(src_family.get_handle()):
                continue
            if src_family in self.p1.get_family_handle_list():
                continue

            tgt_family = self.find_family(src_family)

            #
            # This is the case where a new family to be added to the
            # p1 as a result of the merge already exists as a
            # family.  In this case, we need to remove the old source
            # family (with the pre-merge identity of the p1) from
            # both the parents
            #
            if tgt_family in self.p1.get_family_handle_list():
                if tgt_family.get_father_handle() != None and \
                   src_family in tgt_family.get_family_handle_list():
                    tgt_family.get_father_handle().remove_family_handle(src_family)
                if tgt_family.get_mother_handle() != None and \
                   src_family in tgt_family.get_mother_handle().get_family_handle_list():
                    tgt_family.get_mother_handle().remove_family_handle(src_family)

                # copy children from source to target

                for child in src_family.get_child_handle_list():
                    if child not in tgt_family.get_child_handle_list():
                        parents = child.get_parent_family_handle_list()
                        tgt_family.add_child_handle(child)
                        if child.get_main_parents_family_handle() == src_family:
                            child.set_main_parent_family_handle(tgt_family)
                        i = 0
                        for fam in parents[:]:
                            if fam[0] == src_family:
                                parents[i] = (tgt_family,fam[1],fam[2])
                            i = i + 1
                        
                # delete the old source family
                del self.db.get_family_handle_map()[src_family.get_handle()]

                continue
            
            # This is the case where a new family to be added 
            # and it is not already in the list.

            if tgt_family:

                # tgt_family a duplicate family, transfer children from
                # the p2 family, and delete the family.  Not sure
                # what to do about marriage/divorce date/place yet.

                # transfer child to new family, alter children to
                # point to the correct family
                
                for child in src_family.get_child_handle_list():
                    if child not in tgt_family.get_child_handle_list():
                        parents = child.get_parent_family_handle_list()
                        tgt_family.add_child_handle(child)
                        if child.get_main_parents_family_handle() == src_family:
                            child.set_main_parent_family_handle(tgt_family)
                        i = 0
                        for fam in parents[:]:
                            if fam[0] == src_family:
                                parents[i] = (tgt_family,fam[1],fam[2])
                            i = i + 1

                # add family events from the old to the new
                for event in src_family.get_event_list():
                    tgt_family.add_event(event)

                # change parents of the family to point to the new
                # family
                
                if src_family.get_father_handle():
                    src_family.get_father_handle().remove_family_handle(src_family.get_handle())
                    src_family.get_father_handle().add_family_handle(tgt_family.get_handle())

                if src_family.get_mother_handle():
                    src_family.get_mother_handle().remove_family_handle(src_family.get_handle())
                    src_family.get_mother_handle().add_family_handle(tgt_family.get_handle())

                del self.db.get_family_handle_map()[src_family.get_handle()]
            else:
                if src_family not in self.p1.get_family_handle_list():
                    self.p1.add_family_handle(src_family)
                    if self.p1.get_gender() == RelLib.Person.male:
                        src_family.set_father_handle(self.p1)
                    else:
                        src_family.set_mother_handle(self.p1)
                self.remove_marriage(src_family,self.p2)

        # a little debugging here
        
        for fam in self.db.get_family_handle_map().values():
            if self.p2 in fam.get_child_handle_list():
                fam.remove_child_handle(self.p2)
                fam.add_child_handle(self.p1)
            if self.p2 == fam.get_father_handle():
                fam.set_father_handle(self.p1)
            if self.p2 == fam.get_mother_handle():
                fam.set_mother_handle(self.p1)
            if fam.get_father_handle() == None and fam.get_mother_handle() == None:
                self.delete_empty_family(fam)
                
    def remove_marriage(self,family,person):
        if person:
            person.remove_family_handle(family)
            if family.get_father_handle() == None and family.get_mother_handle() == None:
                self.delete_empty_family(family)

    def delete_empty_family(self,family_handle):
        family = self.db.get_family_from_handle(family_handle)
        for child in family.get_child_handle_list():
            if child.get_main_parents_family_handle() == family_handle:
                child.set_main_parent_family_handle(None)
            else:
                child.remove_parent_family_handle(family_handle)
        self.db.delete_family(family_handle)

def compare_people(p1,p2):

    name1 = p1.get_primary_name()
    name2 = p2.get_primary_name()
                
    chance = name_match(name1,name2)
    if chance == -1.0  :
        return -1.0

    birth1 = p1.get_birth()
    death1 = p1.get_death()
    birth2 = p2.get_birth()
    death2 = p2.get_death()

    value = date_match(birth1.get_date_object(),birth2.get_date_object()) 
    if value == -1.0 :
        return -1.0
    chance = chance + value

    value = date_match(death1.get_date_object(),death2.get_date_object()) 
    if value == -1.0 :
        return -1.0
    chance = chance + value

    value = place_match(birth1.get_place_handle(),birth2.get_place_handle()) 
    if value == -1.0 :
        return -1.0
    chance = chance + value

    value = place_match(death1.get_place_handle(),death2.get_place_handle()) 
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
        
    f1 = p1.get_main_parents_family_handle()
    f2 = p2.get_main_parents_family_handle()

    if f1 and f1.get_father_handle():
        dad1 = f1.get_father_handle().get_primary_name()
    else:
        dad1 = None

    if f2 and f2.get_father_handle():
        dad2 = f2.get_father_handle().get_primary_name()
    else:
        dad2 = None
        
    value = name_match(dad1,dad2)
            
    if value == -1.0:
        return -1.0

    chance = chance + value
            
    if f1 and f1.get_mother_handle():
        mom1 = f1.get_mother_handle().get_primary_name()
    else:
        mom1 = None

    if f2 and f2.get_mother_handle():
        mom2 = f2.get_mother_handle().get_primary_name()
    else:
        mom2 = None

    value = name_match(mom1,mom2)
    if value == -1.0:
        return -1.0
            
    chance = chance + value

    for f1 in p1.get_family_handle_list():
        for f2 in p2.get_family_handle_list():
            if p1.get_gender() == RelLib.Person.female:
                father1 = f1.get_father_handle()
                father2 = f2.get_father_handle()
                if father1 and father2:
                    if father1 == father2:
                        chance = chance + 1.0
                    else:
                        fname1 = GrampsCfg.get_nameof()(father1)
                        fname2 = GrampsCfg.get_nameof()(father2)
                        value = name_match(fname1,fname2)
                        if value != -1.0:
                            chance = chance + value
            else:
                mother1 = f1.get_mother_handle()
                mother2 = f2.get_mother_handle()
                if mother1 and mother2:
                    if mother1 == mother2:
                        chance = chance + 1.0
                    else:
                        mname1 = GrampsCfg.get_nameof()(mother1)
                        mname2 = GrampsCfg.get_nameof()(mother2)
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
    if date1.get_date() == "" or date2.get_date() == "":
        return 0.0
    if date1.get_date() == date2.get_date():
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
    
    srn1 = name.get_surname()
    sfx1 = name.get_suffix()
    srn2 = name1.get_surname()
    sfx2 = name1.get_suffix()

    if not name_compare(srn1,srn2):
        return -1
    if sfx1 != sfx2:
        if sfx1 != "" and sfx2 != "":
            return -1

    if name.get_first_name() == name1.get_first_name():
        return 1
    else:
        list1 = string.split(name.get_first_name())
        list2 = string.split(name1.get_first_name())

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
def ancestors_of(p1,lst):
    if p1 == None:
        return
    lst.append(p1)
    f1 = p1.get_main_parents_family_handle()
    if f1 != None:
        ancestors_of(f1.get_father_handle(),lst)
        ancestors_of(f1.get_mother_handle(),lst)

#---------------------------------------------------------------------
#
#
#
#---------------------------------------------------------------------
def name_of(p):
    if not p:
        return ""
    return "%s (%s)" % (GrampsCfg.get_nameof()(p),p.get_handle())

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

        old_id = self.p1.get_handle()
        
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
        for url in self.p2.get_url_list():
            self.p1.add_url(url)

        # Copy photos from P2 to P1
        for photo in self.p2.get_media_list():
            self.p1.add_media_reference(photo)

        # Copy sources from P2 to P1
        for source in self.p2.get_source_references():
            self.p1.add_source(source)

        # Add notes from P2 to P1
        note = self.p2.get_note()
        if note != "":
            if self.p1.get_note() == "":
                self.p1.set_note(note)
            elif self.p1.get_note() != note:
                self.p1.set_note("%s\n\n%s" % (self.p1.get_note(),note))

        if t2active:
            lst = [self.p1.get_main_location()] + self.p1.get_alternate_locations()
            self.p1.set_main_location(self.p2.get_main_location())
            for l in lst:
                if not l.is_empty():
                    self.p1.add_alternate_locations(l)
        else:
            lst = [self.p2.get_main_location()] + self.p2.get_alternate_locations()
            for l in lst:
                if not l.is_empty():
                    self.p1.add_alternate_locations(l)

        # loop through people, changing event references to P2 to P1
        for key in self.db.get_person_handles(sort_handles=False):
            p = self.db.get_person_from_handle(key)
            for event in [p.get_birth(), p.get_death()] + p.get_event_list():
                if event.get_place_handle() == self.p2:
                    event.set_place_handle(self.p1)

        # loop through families, changing event references to P2 to P1
        for f in self.db.get_family_handle_map().values():
            for event in f.get_event_list():
                if event.get_place_handle() == self.p2:
                    event.set_place_handle(self.p1)
                    
        self.db.remove_place(self.p2.get_handle())
        self.db.build_place_display(self.p1.get_handle(),old_id)
        
        self.update(self.p1.get_handle())
        Utils.destroy_passed_object(obj)

