#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modiy
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

import pickle

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

import const
import GrampsCfg
import Utils
import AutoComp
import ListModel
import RelLib
import ImageSelect
import Date

from QuestionDialog import QuestionDialog, WarningDialog
from intl import gettext as _

#-------------------------------------------------------------------------
#
# Globals
#
#-------------------------------------------------------------------------
_temple_names = const.lds_temple_codes.keys()
_temple_names.sort()
_temple_names = [""] + _temple_names

pycode_tgts = [('fevent', 0, 0), ('fattr', 0, 1)]

#-------------------------------------------------------------------------
#
# Marriage class
#
#-------------------------------------------------------------------------
class Marriage:

    def __init__(self,family,db,callback):
        """Initializes the Marriage class, and displays the window"""
        self.family = family
        self.db = db
        self.path = db.getSavePath()
        self.cb = callback
        self.pmap = {}

        for key in db.getPlaceKeys():
            p = db.getPlaceDisplay(key)
            self.pmap[p[0]] = key

        self.top = gtk.glade.XML(const.marriageFile,"marriageEditor")
        top_window = self.get_widget("marriageEditor")
        self.icon_list = self.get_widget('iconlist')
        self.gallery = ImageSelect.Gallery(family, self.path, self.icon_list, db, self)

        self.top.signal_autoconnect({
            "destroy_passed_object" : self.on_cancel_edit,
            "on_up_clicked" : self.on_up_clicked,
            "on_down_clicked" : self.on_down_clicked,
            "on_attr_up_clicked" : self.on_attr_up_clicked,
            "on_attr_down_clicked" : self.on_attr_down_clicked,
            "on_add_attr_clicked" : self.on_add_attr_clicked,
            "on_delete_attr_clicked" : self.on_delete_attr_clicked,
            "on_addphoto_clicked" : self.gallery.on_add_photo_clicked,
            "on_close_marriage_editor" : self.on_close_marriage_editor,
            "on_delete_event" : self.on_delete_event,
            "on_lds_src_clicked" : self.lds_src_clicked,
            "on_lds_note_clicked" : self.lds_note_clicked,
            "on_deletephoto_clicked" : self.gallery.on_delete_photo_clicked,
            "on_edit_properties_clicked": self.gallery.popup_change_description,
            "on_marriageAddBtn_clicked" : self.on_add_clicked,
            "on_marriageDeleteBtn_clicked" : self.on_delete_clicked,
            })

        text_win = self.get_widget("marriageTitle")
        title = _("%s and %s") % (GrampsCfg.nameof(family.getFather()),
                                  GrampsCfg.nameof(family.getMother()))
        text_win.set_text(title)
        
        self.event_list = self.get_widget("marriageEventList")

        # widgets
        self.date_field  = self.get_widget("marriageDate")
        self.place_field = self.get_widget("marriagePlace")
        self.cause_field = self.get_widget("marriageCause")
        self.name_field  = self.get_widget("marriageEventName")
        self.descr_field = self.get_widget("marriageDescription")
        self.type_field  = self.get_widget("marriage_type")
        self.notes_field = self.get_widget("marriageNotes")
        self.gid = self.get_widget("gid")
        self.attr_list = self.get_widget("attr_list")
        self.attr_type = self.get_widget("attr_type")
        self.attr_value = self.get_widget("attr_value")
        self.event_src_field = self.get_widget("event_srcinfo")
        self.event_conf_field = self.get_widget("event_conf")
        self.attr_src_field = self.get_widget("attr_srcinfo")
        self.attr_conf_field = self.get_widget("attr_conf")
        self.lds_date = self.get_widget("lds_date")
        self.lds_temple = self.get_widget("lds_temple")
        self.lds_status = self.get_widget("lds_status")
        self.lds_place = self.get_widget("lds_place")
        
        self.elist = family.getEventList()[:]
        self.alist = family.getAttributeList()[:]
        self.lists_changed = 0

        # set initial data
        self.gallery.load_images()

        etitles = [(_('Event'),-1,150),(_('Date'),-1,150),(_('Place'),-1,150)]
        atitles = [(_('Attribute'),-1,150),(_('Value'),-1,150)]

        self.etree = ListModel.ListModel(self.event_list, etitles,
                                         self.on_select_row,
                                         self.on_update_clicked)
        self.atree = ListModel.ListModel(self.attr_list, atitles,
                                         self.on_attr_list_select_row,
                                         self.on_update_attr_clicked)

        self.type_field.set_popdown_strings(const.familyRelations)
        frel = const.display_frel(family.getRelationship())
        self.type_field.entry.set_text(frel)
        self.gid.set_text(family.getId())
        self.gid.set_editable(GrampsCfg.id_edit)

        self.lds_temple.set_popdown_strings(_temple_names)

        ord = self.family.getLdsSeal()
        if ord:
            if ord.getPlace():
                self.lds_place.entry.set_text(ord.getPlace().get_title())
            self.lds_date.set_text(ord.getDate())
            if ord.getTemple() != "":
                name = const.lds_temple_to_abrev[ord.getTemple()]
            else:
                name = ""
            self.lds_temple.entry.set_text(name)
            self.seal_stat = ord.getStatus()
        else:
            self.lds_temple.entry.set_text("")
            self.seal_stat = 0
        self.autoplace = AutoComp.AutoCombo(self.lds_place,self.pmap.keys())

        self.build_seal_menu()
        
        self.event_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,pycode_tgts,gtk.gdk.ACTION_COPY)
        self.event_list.drag_source_set(gtk.gdk.BUTTON1_MASK,pycode_tgts, gtk.gdk.ACTION_COPY)
        self.event_list.connect('drag_data_get', self.ev_source_drag_data_get)
        self.event_list.connect('drag_data_received',self.ev_dest_drag_data_received)
        self.event_list.connect('drag_begin', self.ev_drag_begin)

        self.attr_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,pycode_tgts,gtk.gdk.ACTION_COPY)
        self.attr_list.drag_source_set(gtk.gdk.BUTTON1_MASK, pycode_tgts,gtk.gdk.ACTION_COPY)
        self.attr_list.connect('drag_data_get', self.at_source_drag_data_get)
        self.attr_list.connect('drag_data_received',self.at_dest_drag_data_received)
        self.attr_list.connect('drag_begin', self.at_drag_begin)

        # set notes data
        self.notes_buffer = self.notes_field.get_buffer()
        self.notes_buffer.set_text(family.getNote())

        self.redraw_event_list()
        self.redraw_attr_list()
        top_window.show()

    def ev_drag_begin(self, context, a):
        return

    def at_drag_begin(self, context, a):
        return

    def build_seal_menu(self):
        menu = gtk.Menu()
        index = 0
        for val in const.lds_ssealing:
            menuitem = gtk.MenuItem(val)
            menuitem.set_data("val",index)
            menuitem.connect('activate',self.set_lds_seal)
            menuitem.show()
            menu.append(menuitem)
            index = index + 1
        self.lds_status.set_menu(menu)
        self.lds_status.set_history(self.seal_stat)

    def set_lds_seal(self,obj):
        self.seal_stat = obj.get_data("val")

    def lds_src_clicked(self,obj):
        import Sources
        ord = self.family.getLdsSeal()
        if ord == None:
            ord = RelLib.LdsOrd()
            self.family.setLdsSeal(ord)
        Sources.SourceSelector(ord.getSourceRefList(),self)

    def lds_note_clicked(self,obj):
        import NoteEdit
        ord = self.family.getLdsSeal()
        if ord == None:
            ord = RelLib.LdsOrd()
            self.family.setLdsSeal(ord)
        NoteEdit.NoteEditor(ord)

    def on_up_clicked(self,obj):
        model,iter = self.etree.get_selected()
        if not iter:
            return
        
        row = self.etree.get_row(iter)
        if row != 0:
            self.etree.select_row(row-1)

    def on_down_clicked(self,obj):
        model,iter = self.etree.get_selected()
        if not iter:
            return

        row = self.etree.get_row(iter)
        self.etree.select_row(row+1)

    def on_attr_up_clicked(self,obj):
        model,iter = self.atree.get_selected()
        if not iter:
            return
        
        row = self.atree.get_row(iter)
        if row != 0:
            self.atree.select_row(row-1)

    def on_attr_down_clicked(self,obj):
        model,iter = self.atree.get_selected()
        if not iter:
            return

        row = self.atree.get_row(iter)
        self.atree.select_row(row+1)

    def ev_dest_drag_data_received(self,widget,context,x,y,selection_data,info,time):
        row = self.etree.get_row_at(x,y)
        if selection_data and selection_data.data:
            exec 'data = %s' % selection_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'family = "%s"' % data[1]
            if mytype != 'fevent':
                return
            elif family == self.family.getId():
                self.move_element(self.elist,self.etree.get_selected_row(),row)
            else:
                foo = pickle.loads(data[2]);
                for src in foo.getSourceRefList():
                    base = src.getBase()
                    newbase = self.db.findSourceNoMap(base.getId())
                    src.setBase(newbase)
                place = foo.getPlace()
                if place:
                    foo.setPlace(self.db.findPlaceNoMap(place.getId()))
                self.elist.insert(row,foo)

            self.lists_changed = 1
            self.redraw_event_list()

    def ev_source_drag_data_get(self,widget, context, selection_data, info, time):
        ev = self.etree.get_selected_objects()
        
        bits_per = 8; # we're going to pass a string
        pickled = pickle.dumps(ev[0]);
        data = str(('fevent',self.family.getId(),pickled));
        selection_data.set(selection_data.target, bits_per, data)

    def at_dest_drag_data_received(self,widget,context,x,y,selection_data,info,time):
        row = self.atree.get_row_at(x,y)
        if selection_data and selection_data.data:
            exec 'data = %s' % selection_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'family = "%s"' % data[1]
            if mytype != 'fevent':
                return
            elif family == self.family.getId():
                self.move_element(self.elist,self.etree.get_selected_row(),row)
            else:
                foo = pickle.loads(data[2]);
                for src in foo.getSourceRefList():
                    base = src.getBase()
                    newbase = self.db.findSourceNoMap(base.getId())
                    src.setBase(newbase)
                self.alist.insert(row,foo)

            self.lists_changed = 1
            self.redraw_attr_list()

    def at_source_drag_data_get(self,widget, context, selection_data, info, time):
        ev = self.atree.get_selected_objects()

        bits_per = 8; # we're going to pass a string
        pickled = pickle.dumps(ev[0]);
        data = str(('fattr',self.family.getId(),pickled));
        selection_data.set(selection_data.target, bits_per, data)

    def update_lists(self):
        self.family.setEventList(self.elist)
        self.family.setAttributeList(self.alist)

    def redraw_attr_list(self):
        self.atree.clear()
        for attr in self.alist:
            d = [const.display_fattr(attr.getType()),attr.getValue()]
            self.atree.add(d,attr)
        if self.alist:
            self.atree.select_row(0)

    def redraw_event_list(self):
        self.etree.clear()
        for data in self.elist:
            self.etree.add([data.getName(),data.getQuoteDate(),data.getPlaceName()],data)
        if self.elist:
            self.etree.select_row(0)

    def get_widget(self,name):
        return self.top.get_widget(name)

    def did_data_change(self):
        changed = 0
        relation = self.type_field.entry.get_text()
        if const.save_frel(relation) != self.family.getRelationship():
            changed = 1

        text = self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                          self.notes_buffer.get_end_iter(),gtk.FALSE)
        if text != self.family.getNote():
            changed = 1
        
        if self.lists_changed:
            changed = 1

        idval = self.gid.get_text()
        if self.family.getId() != idval:
            changed = 1

        date = self.lds_date.get_text()
        temple = self.lds_temple.entry.get_text()
        if const.lds_temple_codes.has_key(temple):
            temple = const.lds_temple_codes[temple]
        else:
            temple = ""

        place = Utils.get_place_from_list(self.lds_place)
        
        ord = self.family.getLdsSeal()
        if not ord:
            if date or temple or place or self.seal_stat:
                changed = 1
        else:
            d = Date.Date()
            d.set(date)
            if Date.compare_dates(d,ord.getDateObj()) != 0 or \
               ord.getTemple() != temple or \
               ord.getPlace() != place or \
               ord.getStatus() != self.seal_stat:
                changed = 1

        return changed

    def cancel_callback(self):
        Utils.destroy_passed_object(self.quit)

    def on_cancel_edit(self,obj):

        if self.did_data_change():
            global quit
            self.quit = obj
            QuestionDialog(_('Abandon Changes'),
                           _("Data was modified. Are you sure you "
                             "want to abandon your changes?"),
                           self.cancel_callback)
        else:
            Utils.destroy_passed_object(obj)

    def on_delete_event(self,obj,b):
        self.on_cancel_edit(obj)

    def on_close_marriage_editor(self,obj):
        idval = self.gid.get_text()
        family = self.family
        if idval != family.getId():
            m = self.db.getFamilyMap() 
            if not m.has_key(idval):
                if m.has_key(family.getId()):
                    del m[family.getId()]
                    m[idval] = family
                family.setId(idval)
                Utils.modified()
            else:
                msg1 = _("GRAMPS ID value was not changed.")
                WarningDialog("%s" % msg1)

        relation = self.type_field.entry.get_text()
        father = self.family.getFather()
        mother = self.family.getMother()
        if father and mother:
            if const.save_frel(relation) != self.family.getRelationship():
                if father.getGender() == mother.getGender():
                    self.family.setRelationship("Partners")
                else:
                    val = const.save_frel(relation)
                    if val == "Partners":
                        val = "Unknown"
                    if father.getGender() == RelLib.Person.female or \
                       mother.getGender() == RelLib.Person.male:
                        self.family.setFather(mother)
                        self.family.setMother(father)
                    self.family.setRelationship(val)
                Utils.modified()

        text = self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                          self.notes_buffer.get_end_iter(),gtk.FALSE)
        if text != self.family.getNote():
            self.family.setNote(text)
            Utils.modified()

        date = self.lds_date.get_text()
        temple = self.lds_temple.entry.get_text()
        if const.lds_temple_codes.has_key(temple):
            temple = const.lds_temple_codes[temple]
        else:
            temple = ""
        place = Utils.get_place_from_list(self.lds_place)

        ord = self.family.getLdsSeal()
        if not ord:
            if date or temple or place or self.seal_stat:
                ord = RelLib.LdsOrd()
                ord.setDate(date)
                ord.setTemple(temple)
                ord.setStatus(self.seal_stat)
                ord.setPlace(place)
                self.family.setLdsSeal(ord)
                Utils.modified()
        else:
            d = Date.Date()
            d.set(date)
            if Date.compare_dates(d,ord.getDateObj()) != 0:
                ord.setDateObj(d)
                Utils.modified()
            if ord.getTemple() != temple:
                ord.setTemple(temple)
                Utils.modified()
            if ord.getStatus() != self.seal_stat:
                ord.setStatus(self.seal_stat)
                Utils.modified()
            if ord.getPlace() != place:
                ord.setPlace(place)
                Utils.modified()

        Utils.destroy_passed_object(self.get_widget("marriageEditor"))

        self.update_lists()
        if self.lists_changed:
            Utils.modified()

    def on_add_clicked(self,obj):
        import EventEdit
        name = Utils.family_name(self.family)
        EventEdit.EventEditor(self,name,const.marriageEvents,
                              const.save_pevent,None,None,0,self.cb)

    def on_update_clicked(self,obj):
        import EventEdit
        model,iter = self.etree.get_selected()
        if not iter:
            return
        event = self.etree.get_object(iter)
        name = Utils.family_name(self.family)
        EventEdit.EventEditor(self,name,const.marriageEvents,
                              const.save_pevent,event,None,0,self.cb)

    def on_delete_clicked(self,obj):
        if Utils.delete_selected(obj,self.elist):
            self.lists_changed = 1
            self.redraw_event_list()

    def on_select_row(self,obj):
        
        model,iter = self.etree.get_selected()
        if not iter:
            return
        event = self.etree.get_object(iter)
    
        self.date_field.set_text(event.getDate())
        self.place_field.set_text(event.getPlaceName())
        self.cause_field.set_text(event.getCause())
        self.name_field.set_label(const.display_fevent(event.getName()))
        if len(event.getSourceRefList()) > 0:
            psrc = event.getSourceRefList()[0]
            self.event_src_field.set_text(psrc.getBase().getTitle())
            self.event_conf_field.set_text(const.confidence[psrc.getConfidence()])
        else:
            self.event_src_field.set_text('')
            self.event_conf_field.set_text('')
        self.descr_field.set_text(event.getDescription())

    def on_attr_list_select_row(self,obj):
        model,iter = self.atree.get_selected()
        if not iter:
            return
        attr = self.atree.get_object(iter)

        self.attr_type.set_label(const.display_fattr(attr.getType()))
        self.attr_value.set_text(attr.getValue())
        if len(attr.getSourceRefList()) > 0:
            psrc = attr.getSourceRefList()[0]
            self.attr_src_field.set_text(psrc.getBase().getTitle())
            self.attr_conf_field.set_text(const.confidence[psrc.getConfidence()])
        else:
            self.attr_src_field.set_text('')
            self.attr_conf_field.set_text('')

    def on_update_attr_clicked(self,obj):
        import AttrEdit
        model,iter = self.atree.get_selected()
        if not iter:
            return

        attr = self.atree.get_object(iter)

        father = self.family.getFather()
        mother = self.family.getMother()
        if father and mother:
            name = _("%s and %s") % (father.getPrimaryName().getName(),
                                         mother.getPrimaryName().getName())
        elif father:
            name = father.getPrimaryName().getName()
        else:
            name = mother.getPrimaryName().getName()
        AttrEdit.AttributeEditor(self,attr,name,const.familyAttributes)

    def on_delete_attr_clicked(self,obj):
        if Utils.delete_selected(obj,self.alist):
            self.lists_changed = 1
            self.redraw_attr_list()

    def on_add_attr_clicked(self,obj):
        import AttrEdit
        father = self.family.getFather()
        mother = self.family.getMother()
        if father and mother:
            name = _("%s and %s") % (father.getPrimaryName().getName(),
                                     mother.getPrimaryName().getName())
        elif father:
            name = father.getPrimaryName().getName()
        else:
            name = mother.getPrimaryName().getName()
        AttrEdit.AttributeEditor(self,None,name,const.familyAttributes)

    def move_element(self,list,src,dest):
        if src == -1:
            return
        obj = list[src]
        list.remove(obj)
        list.insert(dest,obj)

