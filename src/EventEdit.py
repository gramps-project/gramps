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
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Sources
import const
import utils
from RelLib import *

#-------------------------------------------------------------------------
#
# EventEditor class
#
#-------------------------------------------------------------------------
class EventEditor:

    def __init__(self,parent,name,list,trans,event,def_placename,read_only):
        self.parent = parent
        self.event = event
        self.trans = trans
        if event:
            self.srcreflist = self.event.getSourceRefList()
        else:
            self.srcreflist = []
        self.top = libglade.GladeXML(const.dialogFile, "event_edit")
        self.window = self.top.get_widget("event_edit")
        self.name_field  = self.top.get_widget("eventName")
        self.place_field = self.top.get_widget("eventPlace")
        self.cause_field = self.top.get_widget("eventCause")
        self.place_combo = self.top.get_widget("eventPlace_combo")
        self.date_field  = self.top.get_widget("eventDate")
        self.cause_field  = self.top.get_widget("eventCause")
        self.descr_field = self.top.get_widget("eventDescription")
        self.note_field = self.top.get_widget("eventNote")
        self.event_menu = self.top.get_widget("personalEvents")
        self.priv = self.top.get_widget("priv")

        self.top.get_widget("eventTitle").set_text(name) 
        self.event_menu.set_popdown_strings(list)
        if read_only:
            self.event_menu.set_sensitive(0)
            self.date_field.grab_focus()

        # Typing CR selects OK button
        self.window.editable_enters(self.name_field);
        self.window.editable_enters(self.place_field);
        self.window.editable_enters(self.date_field);
        self.window.editable_enters(self.cause_field);
        self.window.editable_enters(self.descr_field);

        values = self.parent.db.getPlaceMap().values()
        if event != None:
            self.name_field.set_text(event.getName())

            utils.attach_places(values,self.place_combo,event.getPlace())
            self.place_field.set_text(event.getPlaceName())
            if (def_placename):
                self.place_field.set_text(def_placename)
            self.date_field.set_text(event.getDate())
            self.cause_field.set_text(event.getCause())
            self.descr_field.set_text(event.getDescription())
            self.priv.set_active(event.getPrivacy())
            
            self.note_field.set_point(0)
            self.note_field.insert_defaults(event.getNote())
            self.note_field.set_word_wrap(1)
        else:
            utils.attach_places(values,self.place_combo,None)
            if (def_placename):
                self.place_field.set_text(def_placename)

        if (not read_only):
            self.name_field.select_region(0, -1)
        self.window.set_data("o",self)
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_combo_insert_text"     : utils.combo_insert_text,
            "on_event_edit_ok_clicked" : self.on_event_edit_ok_clicked,
            "on_source_clicked" : self.on_edit_source_clicked
            })

    def on_edit_source_clicked(self,obj):
        Sources.SourceSelector(self.srcreflist,self.parent,src_changed)

    def on_event_edit_ok_clicked(self,obj):

        ename = self.name_field.get_text()
        edate = self.date_field.get_text()
        ecause = self.cause_field.get_text()
        eplace = strip(self.place_field.get_text())
        eplace_obj = utils.get_place_from_list(self.place_combo)
        enote = self.note_field.get_chars(0,-1)
        edesc = self.descr_field.get_text()
        epriv = self.priv.get_active()

        if self.event == None:
            self.event = Event()
            self.event.setSourceRefList(self.srcreflist)
            self.parent.elist.append(self.event)
        
        if eplace_obj == None and eplace != "":
            eplace_obj = Place()
            eplace_obj.set_title(eplace)
            self.parent.db.addPlace(eplace_obj)

        self.update_event(ename,edate,eplace_obj,edesc,enote,epriv,ecause)
        self.parent.redraw_event_list()
        utils.destroy_passed_object(obj)

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

        if self.event.getDate() != date:
            self.event.setDate(date)
            self.parent.lists_changed = 1

        if self.event.getCause() != cause:
            self.event.setCause(cause)
            self.parent.lists_changed = 1

        if self.event.getPrivacy() != priv:
            self.event.setPrivacy(priv)
            self.parent.lists_changed = 1

def src_changed(parent):
    parent.lists_changed = 1
            
