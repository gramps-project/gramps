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

from string import strip

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Sources
import const
import Utils
import GrampsCfg
import AutoComp
import Calendar
import RelLib
import Date

from DateEdit import DateEdit
from intl import gettext as _

#-------------------------------------------------------------------------
#
# EventEditor class
#
#-------------------------------------------------------------------------
class EventEditor:

    def __init__(self,parent,name,list,trans,event,def_placename,read_only,cb):
        self.parent = parent
        self.event = event
        self.trans = trans
        self.callback = cb
        self.plist = []
        self.pmap = {}
        
        for key in self.parent.db.getPlaceKeys():
            p = self.parent.db.getPlaceDisplay(key)
            self.pmap[p[0]] = key

        if event:
            self.srcreflist = self.event.getSourceRefList()
            self.date = Date.Date(self.event.getDateObj())
        else:
            self.srcreflist = []
            self.date = Date.Date(None)

        self.top = gtk.glade.XML(const.dialogFile, "event_edit")
        self.window = self.top.get_widget("event_edit")
        self.name_field  = self.top.get_widget("eventName")
        self.place_field = self.top.get_widget("eventPlace")
        self.cause_field = self.top.get_widget("eventCause")
        self.slist = self.top.get_widget("slist")
        self.place_combo = self.top.get_widget("eventPlace_combo")
        self.date_field  = self.top.get_widget("eventDate")
        self.cause_field  = self.top.get_widget("eventCause")
        self.descr_field = self.top.get_widget("event_description")
        self.note_field = self.top.get_widget("eventNote")
        self.event_menu = self.top.get_widget("personalEvents")
        self.priv = self.top.get_widget("priv")
        self.calendar = self.top.get_widget("calendar")

        if GrampsCfg.calendar:
            self.calendar.show()
        else:
            self.calendar.hide()
        
        self.top.get_widget("eventTitle").set_text(name) 
        if read_only:
            self.event_menu.set_sensitive(0)
            self.date_field.grab_focus()

        self.sourcetab = Sources.SourceTab(self.srcreflist,self.parent,
                                           self.top,self.slist,
                                           self.top.get_widget('add_src'),
                                           self.top.get_widget('del_src'))

        AutoComp.AutoCombo(self.event_menu,list)
        AutoComp.AutoEntry(self.place_field,self.pmap.keys())

        if event != None:
            self.name_field.set_text(event.getName())
            if (def_placename):
                self.place_field.set_text(def_placename)
            else:
                self.place_field.set_text(event.getPlaceName())

            self.date_field.set_text(self.date.getDate())
            self.cause_field.set_text(event.getCause())
            self.descr_field.set_text(event.getDescription())
            self.priv.set_active(event.getPrivacy())
            
            self.note_field.get_buffer().set_text(event.getNote())
        else:
            if (def_placename):
                self.place_field.set_text(def_placename)
        self.date_check = DateEdit(self.date_field,self.top.get_widget("date_stat"))

#        if not read_only:
#            self.name_field.select_region(0, -1)

        self.top.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_add_src_clicked" : self.add_source,
            "on_del_src_clicked" : self.del_source,
            "on_event_edit_ok_clicked" : self.on_event_edit_ok_clicked,
            })

        menu = gtk.Menu()
        index = 0
        for cobj in Calendar.calendar_names():
            item = gtk.MenuItem(cobj.TNAME)
            item.set_data("d",cobj)
            item.connect("activate",self.on_menu_changed)
            item.show()
            menu.append(item)
            if self.date.get_calendar().NAME == cobj.NAME:
                menu.set_active(index)
                self.date_check.set_calendar(cobj())
            index = index + 1
        self.calendar.set_menu(menu)

    def add_source(self,obj):
        pass

    def del_source(self,obj):
        pass

    def on_menu_changed(self,obj):
        cobj = obj.get_data("d")
        self.date.set(self.date_field.get_text())
        self.date.set_calendar(cobj)
        self.date_field.set_text(self.date.getDate())
        self.date_check.set_calendar(cobj())
        
    def get_place(self,field,makenew=0):
        text = strip(field.get_text())
        if text:
            if self.pmap.has_key(text):
                return self.parent.db.getPlaceMap()[self.pmap[text]]
            elif makenew:
                place = RelLib.Place()
                place.set_title(text)
                self.parent.db.addPlace(place)
                self.pmap[text] = place.getId()
                self.plist.append(place)
                Utils.modified()
                return place
            else:
                return None
        else:
            return None

    def on_event_edit_ok_clicked(self,obj):

        ename = self.name_field.get_text()
        self.date.set(self.date_field.get_text())
        ecause = self.cause_field.get_text()
        eplace_obj = self.get_place(self.place_field,1)
        buf = self.note_field.get_buffer()

        enote = buf.get_text(buf.get_start_iter(),buf.get_end_iter(),gtk.FALSE)
        edesc = self.descr_field.get_text()
        epriv = self.priv.get_active()

        if self.event == None:
            self.event = RelLib.Event()
            self.event.setSourceRefList(self.srcreflist)
            self.parent.elist.append(self.event)
        
        self.update_event(ename,self.date,eplace_obj,edesc,enote,epriv,ecause)
        self.parent.redraw_event_list()
        self.callback(None,self.plist)
        Utils.destroy_passed_object(obj)

    def update_event(self,name,date,place,desc,note,priv,cause):
        if self.event.getPlace() != place:
            self.event.setPlace(place)
            self.parent.lists_changed = 1
        
        if self.event.getName() != self.trans(name):
            self.event.setName(self.trans(name))
            self.parent.lists_changed = 1
        
        if self.event.getDescription() != desc:
            self.event.setDescription(desc)
            self.parent.lists_changed = 1

        if self.event.getNote() != note:
            self.event.setNote(note)
            self.parent.lists_changed = 1

        dobj = self.event.getDateObj()

        self.event.setSourceRefList(self.srcreflist)
        
        if Date.compare_dates(dobj,date) != 0:
            self.event.setDateObj(date)
            self.parent.lists_changed = 1

        if self.event.getCause() != cause:
            self.event.setCause(cause)
            self.parent.lists_changed = 1

        if self.event.getPrivacy() != priv:
            self.event.setPrivacy(priv)
            self.parent.lists_changed = 1
