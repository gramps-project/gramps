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

"Database Processing/Merge people"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import RelLib
import Utils
import soundex
import GrampsCfg
import ListModel
import MergeData
from gettext import gettext as _ 

#-------------------------------------------------------------------------
#
# standard python models
#
#-------------------------------------------------------------------------
import string
import os

#-------------------------------------------------------------------------
#
# GNOME libraries
#
#-------------------------------------------------------------------------
from gnome.ui import *
import gtk 
import gtk.glade

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def is_initial(name):
    if len(name) > 2:
        return 0
    elif len(name) == 2:
        if name[0] == name[0].upper() and name[1] == '.':
            return 1
    else:
        return name[0] == name[0].upper()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class Merge:

    def __init__(self,database,callback,parent):
        self.db = database
        self.parent = parent
        self.win_key = self
        self.map = {}
        self.list = []
        self.index = 0
        self.merger = None
        self.mergee = None
        self.removed = {}
        self.update = callback
        self.use_soundex = 1

        self.family_list = database.get_family_keys()[:]
        self.person_list = database.get_person_keys()[:]

        base = os.path.dirname(__file__)
        self.glade_file = "%s/%s" % (base,"merge.glade")
        top = gtk.glade.XML(self.glade_file,"dialog","gramps")
        
        my_menu = gtk.Menu()
        item = gtk.MenuItem(_("Low"))
        item.set_data("v",0.25)
        item.show()
        my_menu.append(item)
        item = gtk.MenuItem(_("Medium"))
        item.set_data("v",1.0)
        item.show()
        my_menu.append(item)
        item = gtk.MenuItem(_("High"))
        item.set_data("v",2.0)
        item.show()
        my_menu.append(item)

        self.soundex_obj = top.get_widget("soundex")
        self.menu = top.get_widget("menu")
        self.menu.set_menu(my_menu)

        self.dialog_window = top.get_widget('dialog')
        Utils.set_titles(self.dialog_window, top.get_widget('title'),
                         _('Merge people'))

        top.signal_autoconnect({
            "on_merge_ok_clicked" : self.on_merge_ok_clicked,
            "destroy_passed_object" : self.close,
            "on_delete_merge_event"   : self.on_delete_event,
            })
        self.add_itself_to_menu()
        self.dialog_window.show()

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,obj):
        self.remove_itself_from_menu()
        self.dialog_window.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        self.parent_menu_item = gtk.MenuItem(_('Merge people'))
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.dialog_window.present()

    def ancestors_of(self,p1_id,id_list):
        if (not p1_id) or (p1_id in id_list):
            return
        id_list.append(p1_id)
        p1 = self.db.find_person_from_id(p1_id)
        f1_id = p1.get_main_parents_family_id()
        if f1_id:
            f1 = self.db.find_family_from_id(f1_id)
            self.ancestors_of(f1.get_father_id(),id_list)
            self.ancestors_of(f1.get_mother_id(),id_list)

    def on_merge_ok_clicked(self,obj):
        active = self.menu.get_menu().get_active().get_data("v")
        self.use_soundex = self.soundex_obj.get_active()
        self.close(obj)
        self.find_potentials(active)
        self.show()
    
    def progress_update(self,val):
        self.progress.set_fraction(val/100.0)
        while gtk.events_pending():
            gtk.main_iteration()

    def find_potentials(self,thresh):
        top = gtk.glade.XML(self.glade_file,"message","gramps")
        self.topWin = top.get_widget("message")
        self.progress = top.get_widget("progressbar1")

        Utils.set_titles(self.topWin,top.get_widget('title'),
                         _('Determining possible merges'))
        
        index = 0

        males = {}
        females = {}
        for p1_id in self.person_list:
            p1 = self.db.find_person_from_id(p1_id)
            key = self.gen_key(p1.get_primary_name().get_surname())
            if p1.get_gender() == RelLib.Person.male:
                if males.has_key(key):
                    males[key].append(p1_id)
                else:
                    males[key] = [p1_id]
            else:
                if females.has_key(key):
                    females[key].append(p1_id)
                else:
                    females[key] = [p1_id]
                
        length = len(self.person_list)

        num = 0
        for p1key in self.person_list:
            p1 = self.db.find_person_from_id(p1key)
            if num % 25 == 0:
                self.progress_update((float(num)/float(length))*100)
            num = num + 1

            key = self.gen_key(p1.get_primary_name().get_surname())
            if p1.get_gender() == RelLib.Person.male:
                remaining = males[key]
            else:
                remaining = females[key]

            index = 0
            for p2key in remaining:
                index = index + 1
                if p1key == p2key:
                    continue
                p2 = self.db.find_person_from_id(p2key)
                if self.map.has_key(p2key):
                    (v,c) = self.map[p2key]
                    if v == p1key:
                        continue
                    
                chance = self.compare_people(p1,p2)
                if chance >= thresh:
                    if self.map.has_key(p1key):
                        val = self.map[p1key]
                        if val[1] > chance:
                            self.map[p1key] = (p2key,chance)
                    else:
                        self.map[p1key] = (p2key,chance)

        self.list = self.map.keys()
        self.list.sort()
        self.length = len(self.list)
        self.topWin.destroy()
        self.dellist = {}

    def show(self):
        top = gtk.glade.XML(self.glade_file,"mergelist","gramps")
        self.window = top.get_widget("mergelist")
        self.win_show_key = self.window

        Utils.set_titles(self.window, top.get_widget('title'),
                         _('Potential Merges'))
        
        self.mlist = top.get_widget("mlist")
        top.signal_autoconnect({
            "destroy_passed_object" : self.close_show,
            "on_do_merge_clicked" : self.on_do_merge_clicked,
            "on_delete_show_event" : self.on_delete_show_event,
            })

        mtitles = [(_('Rating'),3,75),(_('First Person'),1,200),
                   (_('Second Person'),2,200),('',-1,0)]
        self.list = ListModel.ListModel(self.mlist,mtitles,
                                        event_func=self.on_do_merge_clicked)
        
        self.redraw()
        self.add_show_to_menu()
        self.window.show()

    def on_delete_show_event(self,obj,b):
        self.remove_show_from_menu()

    def close_show(self,obj):
        self.remove_show_from_menu()
        self.window.destroy()

    def add_show_to_menu(self):
        self.parent.child_windows[self.win_show_key] = self.window
        self.show_parent_menu_item = gtk.MenuItem(_('Potential Merges'))
        self.show_parent_menu_item.connect("activate",self.present_show)
        self.show_parent_menu_item.show()
        self.parent.winsmenu.append(self.show_parent_menu_item)

    def remove_show_from_menu(self):
        del self.parent.child_windows[self.win_show_key]
        self.show_parent_menu_item.destroy()

    def present_show(self,obj):
        self.window.present()

    def redraw(self):
        list = []
        for p1key in self.map.keys():
            if self.dellist.has_key(p1key):
                continue
            (p2key,c) = self.map[p1key]
            if p1key == p2key:
                continue
            list.append((c,p1key,p2key))

        self.list.clear()
        for (c,p1key,p2key) in list:
            c1 = "%5.2f" % c
            c2 = "%5.2f" % (100-c)
            pn1 = self.db.find_person_from_id(p1key).get_primary_name().get_name()
            pn2 = self.db.find_person_from_id(p2key).get_primary_name().get_name()
            self.list.add([c, pn1, pn2,c2],(p1key,p2key))

    def on_do_merge_clicked(self,obj):
        store,iter = self.list.selection.get_selected()
        if not iter:
            return

        (p1,p2) = self.list.get_object(iter)
        pn1 = self.db.find_person_from_id(p1)
        pn2 = self.db.find_person_from_id(p2)
        MergeData.MergePeople(self.parent,self.db,pn1,pn2,self.on_update)

    def on_update(self,p1_id,p2_id,old_id):
        self.dellist[p2_id] = p1_id
        for key in self.dellist.keys():
            if self.dellist[key] == p2_id:
                self.dellist[key] = p1_id
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
            try:
                return soundex.soundex(val)
            except UnicodeEncodeError:
                return val
        else:
            return val

    def name_compare(self,s1,s2):
        if self.use_soundex:
            try:
                return soundex.compare(s1,s2)
            except UnicodeEncodeError:
                return s1 == s2
        else:
            return s1 == s2

    def date_match(self,date1,date2):
        if date1.get_date() == "" or date2.get_date() == "":
            return 0
        if date1.get_date() == date2.get_date():
            return 1

        if date1.is_range() or date2.is_range():
            return self.range_compare(date1,date2)

        date1 = date1.get_start_date()
        date2 = date2.get_start_date()
        
        if date1.get_year() == date2.get_year():
            if date1.get_month() == date2.get_month():
                return 0.75
            if not date1.get_month_valid() or not date2.get_month_valid():
                return 0.75
            else:
                return -1
        else:
            return -1

    def range_compare(self,date1,date2):
        if date1.is_range() and date2.is_range():
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
        elif date2.is_range():
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
    
        srn1 = name.get_surname()
        sfx1 = name.get_suffix()
        srn2 = name1.get_surname()
        sfx2 = name1.get_suffix()

        if not self.name_compare(srn1,srn2):
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
                return self.list_reduce(list1,list2)
            else:
                return self.list_reduce(list2,list1)
            
    def place_match(self,p1_id,p2_id):
        if p1_id == p2_id:
            return 1
        
        if not p1_id:
            name1 = ""
        else:
            p1 = self.db.find_place_from_id(p1_id)
            name1 = p1.get_title()

        if not p2_id:
            name2 = ""
        else:
            p2 = self.db.find_place_from_id(p2_id)
            name2 = p2.get_title()
        
        if not (name1 and name2):
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

        name1 = p1.get_primary_name()
        name2 = p2.get_primary_name()

        chance = self.name_match(name1,name2)
        if chance == -1  :
            return -1

        birth1_id = p1.get_birth_id()
        if birth1_id:
            birth1 = self.db.find_event_from_id(birth1_id)
        else:
            birth1 = RelLib.Event()

        death1_id = p1.get_death_id()
        if death1_id:
            death1 = self.db.find_event_from_id(death1_id)
        else:
            death1 = RelLib.Event()

        birth2_id = p2.get_birth_id()
        if birth2_id:
            birth2 = self.db.find_event_from_id(birth2_id)
        else:
            birth2 = RelLib.Event()

        death2_id = p2.get_death_id()
        if death2_id:
            death2 = self.db.find_event_from_id(death2_id)
        else:
            death2 = RelLib.Event()

        value = self.date_match(birth1.get_date_object(),birth2.get_date_object()) 
        if value == -1 :
            return -1
        chance = chance + value

        value = self.date_match(death1.get_date_object(),death2.get_date_object()) 
        if value == -1 :
            return -1
        chance = chance + value

        value = self.place_match(birth1.get_place_id(),birth2.get_place_id()) 
        if value == -1 :
            return -1
        chance = chance + value

        value = self.place_match(death1.get_place_id(),death2.get_place_id()) 
        if value == -1 :
            return -1
        chance = chance + value

        ancestors = []
        self.ancestors_of(p1.get_id(),ancestors)
        if p2.get_id() in ancestors:
            return -1

        ancestors = []
        self.ancestors_of(p2.get_id(),ancestors)
        if p1.get_id() in ancestors:
            return -1
        
        f1_id = p1.get_main_parents_family_id()
        f2_id = p2.get_main_parents_family_id()

        if f1_id and f2_id:
            f1 = self.db.find_family_from_id(f1_id)
            f2 = self.db.find_family_from_id(f2_id)
            dad1_id = f1.get_father_id()
            if dad1_id:
            	dad1 = get_name_obj(self.db.find_person_from_id(dad1_id))
            else:
                dad1 = None
            dad2_id = f2.get_father_id()
            if dad2_id:
            	dad2 = get_name_obj(self.db.find_person_from_id(dad2_id))
            else:
                dad2 = None
            
            value = self.name_match(dad1,dad2)
            
            if value == -1:
                return -1

            chance = chance + value
            
            mom1_id = f1.get_mother_id()
            if mom1_id:
            	mom1 = get_name_obj(self.db.find_person_from_id(mom1_id))
            else:
                mom1 = None
            mom2_id = f2.get_mother_id()
            if mom2_id:
            	mom2 = get_name_obj(self.db.find_person_from_id(mom2_id))
            else:
                mom2 = None

            value = self.name_match(mom1,mom2)
            if value == -1:
                return -1
            
            chance = chance + value

        for f1_id in p1.get_family_id_list():
            f1 = self.db.find_family_from_id(f1_id)
            for f2_id in p2.get_family_id_list():
                f2 = self.db.find_family_from_id(f2_id)
                if p1.get_gender() == RelLib.Person.female:
                    father1_id = f1.get_father_id()
                    father2_id = f2.get_father_id()
                    if father1_id and father2_id:
                        if father1_id == father2_id:
                            chance = chance + 1
                        else:
                            father1 = self.db.find_person_from_id(father1_id)
                            father2 = self.db.find_person_from_id(father2_id)
                            fname1 = get_name_obj(father1)
                            fname2 = get_name_obj(father2)
                            value = self.name_match(fname1,fname2)
                            if value != -1:
                                chance = chance + value
                else:
                    mother1_id = f1.get_mother_id()
                    mother2_id = f2.get_mother_id()
                    if mother1_id and mother2_id:
                        if mother1_id == mother2_id:
                            chance = chance + 1
                        else:
                            mother1 = self.db.find_person_from_id(mother1_id)
                            mother2 = self.db.find_person_from_id(mother2_id)
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
def name_of(p):
    if not p:
        return ""
    return "%s (%s)" % ( GrampsCfg.nameof(p),p.get_id())

def get_name_obj(person):
    if person:
        return person.get_primary_name()
    else:
        return None
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback,parent=None):
    try:
        Merge(database,callback,parent)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_id(p1,p2):
    return cmp(p1.get_id(),p2.get_id())

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
    description=_("Searches the entire database, looking for "
                  "individual entries that may represent the same person.")
    )
