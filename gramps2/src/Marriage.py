#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

# $Id$

import pickle
import string

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.gdk
import gtk.glade
import gnome

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
import DateHandler
import Sources

from QuestionDialog import QuestionDialog, WarningDialog, SaveDialog
from gettext import gettext as _

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

    def __init__(self,parent,family,db,callback,update):
        """Initializes the Marriage class, and displays the window"""
        self.family = family
        self.parent = parent
        if self.parent.child_windows.has_key(family.get_handle()):
            self.parent.child_windows[family.get_handle()].present(None)
            return
        self.child_windows = {}
        self.db = db
        self.path = db.get_save_path()
        self.cb = callback
        self.update_fv = update
        self.pmap = {}
        self.dp = DateHandler.create_parser()

        if family:
            self.srcreflist = family.get_source_references()
        else:
            self.srcreflist = []

        for key in db.get_place_handles():
            p = db.get_place_from_handle(key).get_display_info()
            self.pmap[p[0]] = key

        self.top = gtk.glade.XML(const.marriageFile,"marriageEditor","gramps")
        self.window = self.get_widget("marriageEditor")

        Utils.set_titles(self.window, self.top.get_widget('title'),
                         _('Marriage/Relationship Editor'))
        
        self.icon_list = self.get_widget('iconlist')
        self.gallery = ImageSelect.Gallery(family, self.db.commit_family,
                                           self.path, self.icon_list, db, self)

        self.top.signal_autoconnect({
            "destroy_passed_object" : self.on_cancel_edit,
            "on_help_marriage_editor" : self.on_help_clicked,
            "on_up_clicked" : self.on_up_clicked,
            "on_down_clicked" : self.on_down_clicked,
            "on_attr_up_clicked" : self.on_attr_up_clicked,
            "on_attr_down_clicked" : self.on_attr_down_clicked,
            "on_add_attr_clicked" : self.on_add_attr_clicked,
            "on_delete_attr_clicked" : self.on_delete_attr_clicked,
            "on_addphoto_clicked" : self.gallery.on_add_media_clicked,
            "on_selectphoto_clicked" : self.gallery.on_select_media_clicked,
            "on_close_marriage_editor" : self.on_close_marriage_editor,
            "on_delete_event" : self.on_delete_event,
            "on_lds_src_clicked" : self.lds_src_clicked,
            "on_lds_note_clicked" : self.lds_note_clicked,
            "on_deletephoto_clicked" : self.gallery.on_delete_media_clicked,
            "on_edit_photo_clicked" : self.gallery.on_edit_media_clicked,
            "on_edit_properties_clicked": self.gallery.popup_change_description,
            "on_marriageAddBtn_clicked" : self.on_add_clicked,
            "on_event_update_clicked" : self.on_event_update_clicked,
            "on_attr_update_clicked" : self.on_update_attr_clicked,
            "on_marriageDeleteBtn_clicked" : self.on_delete_clicked,
            "on_switch_page" : self.on_switch_page
            })


        fid = family.get_father_handle()
        mid = family.get_mother_handle()

        father = self.db.get_person_from_handle(fid)
        mother = self.db.get_person_from_handle(mid)
        
        self.title = _("%s and %s") % (GrampsCfg.get_nameof()(father),
                                  GrampsCfg.get_nameof()(mother))

        Utils.set_title_label(self.top,self.title)
        
        self.event_list = self.get_widget("marriageEventList")

        if gtk.gdk.screen_height() > 700:
            self.event_list.set_size_request(500,250)
        else:
            self.event_list.set_size_request(500,-1)


        # widgets
        self.complete = self.get_widget('complete')
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
        self.slist = self.get_widget("slist")
        self.sources_label = self.get_widget("sourcesMarriage")
        self.gallery_label = self.get_widget("galleryMarriage")
        self.sources_label = self.get_widget("sourcesMarriage")
        self.events_label = self.get_widget("eventsMarriage")
        self.attr_label = self.get_widget("attrMarriage")
        self.notes_label = self.get_widget("notesMarriage")
        self.lds_label = self.get_widget("ldsMarriage")

        self.flowed = self.get_widget("mar_flowed")
        self.preform = self.get_widget("mar_preform")

        self.elist = family.get_event_list()[:]
        self.alist = family.get_attribute_list()[:]
        self.lists_changed = 0

        self.get_widget('changed').set_text(family.get_change_display())

        # set initial data
        self.gallery.load_images()

        etitles = [(_('Event'),-1,100),(_('Date'),-1,125),(_('Place'),-1,150)]
        atitles = [(_('Attribute'),-1,150),(_('Value'),-1,150)]

        self.etree = ListModel.ListModel(self.event_list, etitles,
                                         self.on_select_row,
                                         self.on_event_update_clicked)
        self.atree = ListModel.ListModel(self.attr_list, atitles,
                                         self.on_attr_list_select_row,
                                         self.on_update_attr_clicked)

        rel_list = []
        for (val,junk) in const.family_relations:
            rel_list.append(val)
        AutoComp.fill_option_text(self.type_field,rel_list)

        frel = family.get_relationship()
        self.type_field.set_active(frel)
        self.gid.set_text(family.get_gramps_id())
        self.gid.set_editable(1)

        AutoComp.fill_combo(self.lds_temple,_temple_names)

        place_list = self.pmap.keys()
        place_list.sort()
        AutoComp.fill_combo(self.lds_place, place_list)

        lds_ord = self.family.get_lds_sealing()
        if lds_ord:
            if lds_ord.get_place_handle():
                self.lds_place.child.set_text(lds_ord.get_place_handle().get_title())
            self.lds_date.set_text(lds_ord.get_date())
            if lds_ord.get_temple() != "":
                name = const.lds_temple_to_abrev[lds_ord.get_temple()]
            else:
                name = ""
            self.lds_temple.child.set_text(name)
            self.seal_stat = lds_ord.get_status()
        else:
            self.lds_temple.child.set_text("")
            self.lds_place.child.set_text("")
            self.seal_stat = 0

        if self.family.get_complete_flag():
            self.complete.set_active(1)

        self.build_seal_menu()

        if lds_ord:
            Utils.bold_label(self.lds_label)
        else:
            Utils.unbold_label(self.lds_label)
        
        self.event_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                      pycode_tgts,gtk.gdk.ACTION_COPY)
        self.event_list.drag_source_set(gtk.gdk.BUTTON1_MASK,
                                        pycode_tgts, gtk.gdk.ACTION_COPY)
        self.event_list.connect('drag_data_get',
                                self.ev_source_drag_data_get)
        self.event_list.connect('drag_data_received',
                                self.ev_dest_drag_data_received)
        self.event_list.connect('drag_begin', self.ev_drag_begin)

        self.attr_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                     pycode_tgts,gtk.gdk.ACTION_COPY)
        self.attr_list.drag_source_set(gtk.gdk.BUTTON1_MASK,
                                       pycode_tgts,gtk.gdk.ACTION_COPY)
        self.attr_list.connect('drag_data_get',
                               self.at_source_drag_data_get)
        self.attr_list.connect('drag_data_received',
                               self.at_dest_drag_data_received)
        self.attr_list.connect('drag_begin', self.at_drag_begin)

        # set notes data
        self.notes_buffer = self.notes_field.get_buffer()
        if family.get_note():
            self.notes_buffer.set_text(family.get_note())
            Utils.bold_label(self.notes_label)
    	    if family.get_note_format() == 1:
    	    	self.preform.set_active(1)
            else:
                self.flowed.set_active(1)

        self.sourcetab = Sources.SourceTab(self.srcreflist,self,
                                           self.top,self.window,self.slist,
                                           self.top.get_widget('add_src'),
                                           self.top.get_widget('edit_src'),
                                           self.top.get_widget('del_src'))

        self.redraw_event_list()
        self.redraw_attr_list()
        self.add_itself_to_winsmenu()
        self.window.show()

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def close(self,ok=0):
        self.gallery.close()
        self.close_child_windows()
        self.remove_itself_from_winsmenu()
        self.window.destroy()

    def add_itself_to_winsmenu(self):
        self.parent.child_windows[self.family.get_handle()] = self
        win_menu_label = self.title
        if not win_menu_label.strip():
            win_menu_label = _("New Relationship")
        self.win_menu_item = gtk.MenuItem(win_menu_label)
        self.win_menu_item.set_submenu(gtk.Menu())
        self.win_menu_item.show()
        self.parent.winsmenu.append(self.win_menu_item)
        self.winsmenu = self.win_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Marriage/Relationship Editor'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_winsmenu(self):
        del self.parent.child_windows[self.family.get_handle()]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.win_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-complete')

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
        lds_ord = self.family.get_lds_sealing()
        if lds_ord == None:
            lds_ord = RelLib.LdsOrd()
            self.family.set_lds_sealing(lds_ord)
        Sources.SourceSelector(lds_ord.get_source_references(),self,self.window)

    def lds_note_clicked(self,obj):
        import NoteEdit
        lds_ord = self.family.get_lds_sealing()
        if lds_ord == None:
            lds_ord = RelLib.LdsOrd()
            self.family.set_lds_sealing(lds_ord)
        NoteEdit.NoteEditor(lds_ord,self,self.window)

    def on_up_clicked(self,obj):
        model,node = self.etree.get_selected()
        if not node:
            return
        
        row = self.etree.get_row(node)
        if row != 0:
            self.etree.select_row(row-1)

    def on_down_clicked(self,obj):
        model,node = self.etree.get_selected()
        if not node:
            return

        row = self.etree.get_row(node)
        self.etree.select_row(row+1)

    def on_attr_up_clicked(self,obj):
        model,node = self.atree.get_selected()
        if not node:
            return
        
        row = self.atree.get_row(node)
        if row != 0:
            self.atree.select_row(row-1)

    def on_attr_down_clicked(self,obj):
        model,node = self.atree.get_selected()
        if not node:
            return

        row = self.atree.get_row(node)
        self.atree.select_row(row+1)

    def ev_dest_drag_data_received(self,widget,context,x,y,selection_data,info,time):
        row = self.etree.get_row_at(x,y)
        if selection_data and selection_data.data:
            exec 'data = %s' % selection_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'family = "%s"' % data[1]
            if mytype != 'fevent':
                return
            elif family == self.family.get_handle():
                self.move_element(self.elist,self.etree.get_selected_row(),
                                  row)
            else:
                foo = pickle.loads(data[2]);
                for src in foo.get_source_references():
                    base_handle = src.get_base_handle()
                    newbase = self.db.get_source_from_handle(base_handle)
                    src.set_base_handle(newbase)
                place = foo.get_place_handle()
                if place:
                    foo.set_place_handle(self.db.get_place_from_handle(place.get_handle()))
                self.elist.insert(row,foo)

            self.lists_changed = 1
            self.redraw_event_list()

    def ev_source_drag_data_get(self,widget, context, selection_data, info, time):
        ev = self.etree.get_selected_objects()
        
        bits_per = 8; # we're going to pass a string
        pickled = pickle.dumps(ev[0]);
        data = str(('fevent',self.family.get_handle(),pickled));
        selection_data.set(selection_data.target, bits_per, data)

    def at_dest_drag_data_received(self,widget,context,x,y,selection_data,info,time):
        row = self.atree.get_row_at(x,y)
        if selection_data and selection_data.data:
            exec 'data = %s' % selection_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'family = "%s"' % data[1]
            if mytype != 'fevent':
                return
            elif family == self.family.get_handle():
                self.move_element(self.elist,self.etree.get_selected_row(),row)
            else:
                foo = pickle.loads(data[2]);
                for src in foo.get_source_references():
                    base_handle = src.get_base_handle()
                    newbase = self.db.get_source_from_handle(base_handle)
                    src.set_base_handle(newbase)
                self.alist.insert(row,foo)

            self.lists_changed = 1
            self.redraw_attr_list()

    def at_source_drag_data_get(self,widget, context, selection_data, info, time):
        ev = self.atree.get_selected_objects()

        bits_per = 8; # we're going to pass a string
        pickled = pickle.dumps(ev[0]);
        data = str(('fattr',self.family.get_handle(),pickled));
        selection_data.set(selection_data.target, bits_per, data)

    def update_lists(self):
        self.family.set_event_list(self.elist)
        self.family.set_attribute_list(self.alist)

    def attr_edit_callback(self,attr):
        self.redraw_attr_list()
        self.atree.select_iter(self.amap[str(attr)])

    def redraw_attr_list(self):
        self.atree.clear()
        self.amap = {}
        for attr in self.alist:
            d = [const.display_fattr(attr.get_type()),attr.get_value()]
            node = self.atree.add(d,attr)
            self.amap[str(attr)] = node
        if self.alist:
            self.atree.select_row(0)
            Utils.bold_label(self.attr_label)
        else:
            Utils.unbold_label(self.attr_label)

    def redraw_event_list(self):
        self.etree.clear()
        self.emap = {}
        for event_handle in self.elist:
            event = self.db.get_event_from_handle(event_handle)
            if not event:
                continue
            place_handle = event.get_place_handle()
            
            if place_handle:
                place_name = self.db.get_place_from_handle(place_handle).get_title()
            else:
                place_name = ""
            node = self.etree.add([const.display_fevent(event.get_name()),
                                   event.get_quote_date(),place_name],event)
            self.emap[str(event)] = node
        if self.elist:
            self.etree.select_row(0)
            Utils.bold_label(self.events_label)
        else:
            Utils.unbold_label(self.events_label)

    def get_widget(self,name):
        return self.top.get_widget(name)

    def did_data_change(self):
        changed = 0
        if self.type_field.get_active() != self.family.get_relationship():
            changed = 1

        if self.complete.get_active() != self.family.get_complete_flag():
            changed = 1

        text = unicode(self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                  self.notes_buffer.get_end_iter(),gtk.FALSE))
        format = self.preform.get_active()

        if text != self.family.get_note():
            changed = 1
        if format != self.family.get_note_format():
            changed = 1
        
        if self.lists_changed:
            changed = 1

        idval = unicode(self.gid.get_text())
        if idval == "":
            idval = None
        if self.family.get_handle() != idval:
            changed = 1

        date = unicode(self.lds_date.get_text())
        temple = unicode(self.lds_temple.child.get_text())
        if const.lds_temple_codes.has_key(temple):
            temple = const.lds_temple_codes[temple]
        else:
            temple = ""

        place = self.get_place(0)
        
        lds_ord = self.family.get_lds_sealing()
        if not lds_ord:
            if date or temple or place or self.seal_stat:
                changed = 1
        else:
            d = self.dp.parse(date)
            if d.is_equal(lds_ord.get_date_object()) or \
               lds_ord.get_temple() != temple or \
               (place and lds_ord.get_place_handle() != place.get_handle()) or \
               lds_ord.get_status() != self.seal_stat:
                changed = 1

        return changed

    def cancel_callback(self):
        self.close(0)

    def on_cancel_edit(self,obj):
        if self.did_data_change():
            global quit
            self.quit = obj
            SaveDialog(_('Save Changes?'),
                       _('If you close without saving, the changes you '
                         'have made will be lost'),
                       self.cancel_callback,
                       self.save)
        else:
            self.close(0)

    def save(self):
        self.on_close_marriage_editor(None)

    def on_delete_event(self,obj,b):
        self.on_cancel_edit(obj)

    def on_close_marriage_editor(self,*obj):

        trans = self.db.transaction_begin()

        idval = unicode(self.gid.get_text())
        family = self.family
        if idval != family.get_gramps_id():
            if not self.db.get_family_from_gramps_id(idval):
                family.set_gramps_id(idval)
            else:
                WarningDialog(_("GRAMPS ID value was not changed."),
                              _('The GRAMPS ID that you chose for this '
                                'relationship is already being used.'))

        relation = self.type_field.get_active()
        father = self.family.get_father_handle()
        mother = self.family.get_mother_handle()
        if father and mother:
            if relation != self.family.get_relationship():
                self.family.set_relationship(relation)

        text = unicode(self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                  self.notes_buffer.get_end_iter(),gtk.FALSE))
        if text != self.family.get_note():
            self.family.set_note(text)

        format = self.preform.get_active()
        if format != self.family.get_note_format():
            self.family.set_note_format(format)

        if self.complete.get_active() != self.family.get_complete_flag():
            self.family.set_complete_flag(self.complete.get_active())

        date = unicode(self.lds_date.get_text())
        temple = unicode(self.lds_temple.child.get_text())
        if const.lds_temple_codes.has_key(temple):
            temple = const.lds_temple_codes[temple]
        else:
            temple = ""
        place = self.get_place(1,trans)

        lds_ord = self.family.get_lds_sealing()
        if not lds_ord:
            if date or temple or place or self.seal_stat:
                lds_ord = RelLib.LdsOrd()
                lds_ord.set_date(date)
                lds_ord.set_temple(temple)
                lds_ord.set_status(self.seal_stat)
                lds_ord.set_place_handle(place)
                self.family.set_lds_sealing(lds_ord)
        else:
            d = self.dp.parse(date)
            if d.is_equal(lds_ord.get_date_object()):
                lds_ord.set_date_object(d)
            if lds_ord.get_temple() != temple:
                lds_ord.set_temple(temple)
            if lds_ord.get_status() != self.seal_stat:
                lds_ord.set_status(self.seal_stat)
            if lds_ord.get_place_handle() != place.get_handle():
                lds_ord.set_place_handle(place.get_handle())

        if self.lists_changed:
            self.family.set_source_reference_list(self.srcreflist)

        self.update_lists()
        self.db.commit_family(self.family,trans)
        self.db.transaction_commit(trans,_("Edit Marriage"))
        self.update_fv(self.family)

        self.close(1)

    def event_edit_callback(self,event):
        """Birth and death events may not be in the map"""
        self.redraw_event_list()
        try:
            self.etree.select_iter(self.emap[str(event)])
        except:
            pass

    def on_add_clicked(self,*obj):
        import EventEdit
        name = Utils.family_name(self.family,self.db)
        EventEdit.EventEditor(self,name,const.marriageEvents,
                              const.family_events,None,None,
                              0,self.event_edit_callback,
                              const.defaultMarriageEvent)

    def on_event_update_clicked(self,obj):
        import EventEdit
        model,node = self.etree.get_selected()
        if not node:
            return
        event = self.etree.get_object(node)
        name = Utils.family_name(self.family,self.db)
        EventEdit.EventEditor(self,name,const.marriageEvents,
                              const.family_events,event,
                              None,0,self.event_edit_callback)

    def on_delete_clicked(self,obj):
        if Utils.delete_selected(obj,self.elist):
            self.lists_changed = 1
            self.redraw_event_list()

    def on_select_row(self,obj):
        
        model,node = self.etree.get_selected()
        if not node:
            return
        event = self.etree.get_object(node)
    
        self.date_field.set_text(event.get_date())
        place_handle = event.get_place_handle()
        if place_handle:
            place_name = self.db.get_place_from_handle(place_handle).get_title()
        else:
            place_name = u""
        self.place_field.set_text(place_name)
        self.cause_field.set_text(event.get_cause())
        self.name_field.set_label(const.display_fevent(event.get_name()))
        if len(event.get_source_references()) > 0:
            psrc_ref = event.get_source_references()[0]
            psrc_id = psrc_ref.get_base_handle()
            psrc = self.db.get_source_from_handle(psrc_id)
            self.event_src_field.set_text(psrc.get_title())
            self.event_conf_field.set_text(const.confidence[psrc_ref.get_confidence_level()])
        else:
            self.event_src_field.set_text('')
            self.event_conf_field.set_text('')
        self.descr_field.set_text(event.get_description())

    def on_attr_list_select_row(self,obj):
        model,node = self.atree.get_selected()
        if not node:
            return
        attr = self.atree.get_object(node)

        self.attr_type.set_label(const.display_fattr(attr.get_type()))
        self.attr_value.set_text(attr.get_value())
        if len(attr.get_source_references()) > 0:
            psrc_ref = attr.get_source_references()[0]
            psrc_id = psrc_ref.get_base_handle()
            psrc = self.db.get_source_from_handle(psrc_id)
            self.attr_src_field.set_text(psrc.get_title())
            self.attr_conf_field.set_text(const.confidence[psrc_ref.get_confidence_level()])
        else:
            self.attr_src_field.set_text('')
            self.attr_conf_field.set_text('')

    def on_update_attr_clicked(self,obj):
        import AttrEdit
        model,node = self.atree.get_selected()
        if not node:
            return

        attr = self.atree.get_object(node)

        father_handle = self.family.get_father_handle()
        mother_handle = self.family.get_mother_handle()
        father = self.db.get_person_from_handle(father_handle)
        mother = self.db.get_person_from_handle(mother_handle)
        if father and mother:
            name = _("%s and %s") % (father.get_primary_name().get_name(),
                                         mother.get_primary_name().get_name())
        elif father:
            name = father.get_primary_name().get_name()
        else:
            name = mother.get_primary_name().get_name()
        AttrEdit.AttributeEditor(self,attr,name,const.familyAttributes,
                                 self.attr_edit_callback)

    def on_delete_attr_clicked(self,obj):
        if Utils.delete_selected(obj,self.alist):
            self.lists_changed = 1
            self.redraw_attr_list()

    def on_add_attr_clicked(self,obj):
        import AttrEdit
        father_handle = self.family.get_father_handle()
        mother_handle = self.family.get_mother_handle()
        father = self.db.get_person_from_handle(father_handle)
        mother = self.db.get_person_from_handle(mother_handle)
        if father and mother:
            name = _("%s and %s") % (father.get_primary_name().get_name(),
                                     mother.get_primary_name().get_name())
        elif father:
            name = father.get_primary_name().get_name()
        else:
            name = mother.get_primary_name().get_name()
        AttrEdit.AttributeEditor(self,None,name,const.familyAttributes,
                                 self.attr_edit_callback)

    def move_element(self,list,src,dest):
        if src == -1:
            return
        obj = list[src]
        list.remove(obj)
        list.insert(dest,obj)

    def on_switch_page(self,obj,a,page):
        text = unicode(self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                self.notes_buffer.get_end_iter(),gtk.FALSE))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)

        date = unicode(self.lds_date.get_text())
        temple = unicode(self.lds_temple.child.get_text())
        if const.lds_temple_codes.has_key(temple):
            temple = const.lds_temple_codes[temple]
        else:
            temple = ""
        
        if date or temple:
            Utils.bold_label(self.lds_label)
        else:
            Utils.unbold_label(self.lds_label)

    def get_place(self,makenew,trans=None):
        field = self.lds_place.child
        text = string.strip(unicode(field.get_text()))
        if text:
            if self.pmap.has_key(text):
                return self.db.get_place_from_handle(self.pmap[text])
            elif makenew:
                place = RelLib.Place()
                place.set_title(text)
                self.db.add_place(place,trans)
                self.pmap[text] = place.get_handle()
                return place
            else:
                return None
        else:
            return None
