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
import Utils
import soundex
import intl
import GrampsCfg
_ = intl.gettext

import string
import os
import MergeData

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

def ancestors_of(p1,list):
    if p1 == None or p1 in list:
        return
    list.append(p1)
    f1 = p1.getMainParents()
    if f1 != None:
        ancestors_of(f1.getFather(),list)
        ancestors_of(f1.getMother(),list)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class Merge:

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
        self.glade_file = "%s/%s" % (base,"merge.glade")
        top = GladeXML(self.glade_file,"dialog")
        
        my_menu = GtkMenu()
        item = GtkMenuItem(_("Low"))
        item.set_data("v",0.25)
        item.show()
        my_menu.append(item)
        item = GtkMenuItem(_("Medium"))
        item.set_data("v",1.0)
        item.show()
        my_menu.append(item)
        item = GtkMenuItem(_("High"))
        item.set_data("v",2.0)
        item.show()
        my_menu.append(item)

        self.soundex_obj = top.get_widget("soundex")
        self.menu = top.get_widget("menu")
        self.menu.set_menu(my_menu)

        top.signal_autoconnect({
            "on_merge_ok_clicked" : self.on_merge_ok_clicked,
            "destroy_passed_object" : Utils.destroy_passed_object
            })

    def on_merge_ok_clicked(self,obj):
        active = self.menu.get_menu().get_active().get_data("v")
        self.use_soundex = self.soundex_obj.get_active()
        Utils.destroy_passed_object(obj)
        self.find_potentials(active)
        self.show()
    
    def progress_update(self,val):
        self.progress.set_value(val)
        while events_pending():
            mainiteration()

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
                if self.map.has_key(p2):
                    (v,c) = self.map[p2]
                    if v == p1:
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
        self.dellist = {}

    def show(self):
        top = GladeXML(self.glade_file,"mergelist")
        self.window = top.get_widget("mergelist")
        self.mlist = top.get_widget("mlist")
        top.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_do_merge_clicked" : self.on_do_merge_clicked,
            })
        self.mlist.connect('button-press-event',self.button_press_event)
        self.redraw()

    def redraw(self):
        list = []
        for p1 in self.map.keys():
            if self.dellist.has_key(p1):
                continue
            (p2,c) = self.map[p1]
            if self.dellist.has_key(p2):
                p2 = self.dellist[p2]
            if p1 == p2:
                continue
            list.append((c,p1,p2))
        list.sort()
        list.reverse()

        index = 0
        self.mlist.freeze()
        self.mlist.clear()
        for (c,p1,p2) in list:
            c = "%5.2f" % c
            self.mlist.append([c, name_of(p1), name_of(p2)])
            self.mlist.set_row_data(index,(p1,p2))
            index = index + 1
        self.mlist.thaw()

    def button_press_event(self,obj,event):
        if event.button != 1 or event.type != GDK._2BUTTON_PRESS:
            return
        if len(self.mlist.selection) <= 0:
            return
        row = self.mlist.selection[0]
        (p1,p2) = self.mlist.get_row_data(row)
        MergeData.MergePeople(self.db,p1,p2,self.on_update)

    def on_do_merge_clicked(self,obj):
        if len(self.mlist.selection) != 1:
            return
        row = self.mlist.selection[0]
        (p1,p2) = self.mlist.get_row_data(row)
        MergeData.MergePeople(self.db,p1,p2,self.on_update)

    def on_update(self,p1,p2,old_id):
        self.dellist[p2] = p1
        for key in self.dellist.keys():
            if self.dellist[key] == p2:
                self.dellist[key] = p1
        self.redraw()
        
    def update_and_destroy(self,obj):
        self.update(1)
        Utils.destroy_passed_object(obj)
        
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
        
    def gen_key(self,val):
        if self.use_soundex:
            return soundex.soundex(val)
        else:
            return val

    def name_compare(self,s1,s2):
        if self.use_soundex:
            return soundex.compare(s1,s2)
        else:
            return s1 == s2

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
            if not date1.getMonthValid() or not date2.getMonthValid():
                return 0.75
            else:
                return -1
        else:
            return -1

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
            
    def place_match(self,p1,p2):
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
                if name[0] == name2[0] and self.name_compare(name,name2):
                    value = value + 0.25
                    break
        if value == 0:
            return -1
        else:
            return min(value,1)
        
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
        
        f1 = p1.getMainParents()
        f2 = p2.getMainParents()

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


def name_of(p):
    if not p:
        return ""
    return "%s (%s)" % ( GrampsCfg.nameof(p),p.getId())

def get_name_obj(person):
    if person:
        return person.getPrimaryName()
    else:
        return None
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback):
    try:
        Merge(database,callback)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_id(p1,p2):
    return cmp(p1.getId(),p2.getId())

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_tool

register_tool(
    runTool,
    _("Find possible duplicate people"),
    category=_("Database Processing"),
    description=_("Searches the entire database, looking for individual entries that may represent the same person.")
    )

