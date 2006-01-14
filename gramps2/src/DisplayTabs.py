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

import gtk
import DateHandler
import NameDisplay
import RelLib
import Utils
import ToolTips
import GrampsLocale

_GENDER = [ _(u'female'), _(u'male'), _(u'unknown') ]

#-------------------------------------------------------------------------
#
# EmbeddedList
#
#-------------------------------------------------------------------------
class EmbeddedList(gtk.HBox):

    _HANDLE_COL = -1
    
    def __init__(self, dbstate, uistate, track, build_model):
        gtk.HBox.__init__(self)
        self.build_model = build_model

        self.dbstate = dbstate
        self.uistate = uistate
        self.track = track
        
        self.tree = gtk.TreeView()
        self.tree.set_rules_hint(True)
        self.selection = self.tree.get_selection()
        self.selection.connect('changed',self.selection_changed)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(self.tree)
        self.pack_start(scroll,True)
        self.columns = []
        self.build_columns()
        self.create_buttons()
        self.rebuild()
        self.show_all()

    def get_selected(self):
        (model,node) = self.selection.get_selected()
        if node:
            return model.get_value(node,self._HANDLE_COL)
        else:
            return None

    def selection_changed(self,obj=None):
        if self.get_selected():
            self.edit_btn.set_sensitive(True)
            self.del_btn.set_sensitive(True)
        else:
            self.edit_btn.set_sensitive(False)
            self.del_btn.set_sensitive(False)

    def create_buttons(self):
        self.add_btn = gtk.Button()
        self.add_btn.set_relief(gtk.RELIEF_NONE)
        self.add_btn.add(gtk.image_new_from_stock(gtk.STOCK_ADD,
                                                  gtk.ICON_SIZE_BUTTON))
        self.edit_btn = gtk.Button()
        self.edit_btn.set_relief(gtk.RELIEF_NONE)
        self.edit_btn.add(gtk.image_new_from_stock(gtk.STOCK_EDIT,
                                                   gtk.ICON_SIZE_BUTTON))
        self.del_btn = gtk.Button()
        self.del_btn.set_relief(gtk.RELIEF_NONE)
        self.del_btn.add(gtk.image_new_from_stock(gtk.STOCK_REMOVE,
                                                  gtk.ICON_SIZE_BUTTON))
        vbox = gtk.VBox()
        vbox.set_spacing(6)
        vbox.pack_start(self.add_btn,False)
        vbox.pack_start(self.edit_btn,False)
        vbox.pack_start(self.del_btn,False)
        vbox.show_all()
        self.pack_start(vbox,False)

        self.add_btn.connect('clicked',self.add_button_clicked)
        self.del_btn.connect('clicked',self.del_button_clicked)
        self.edit_btn.connect('clicked',self.edit_button_clicked)

    def add_button_clicked(self,obj):
        pass

    def del_button_clicked(self,obj):
        pass

    def edit_button_clicked(self,obj):
        pass

    def set_label(self):
        return

    def get_data(self):
        return []

    def column_order(self):
        return []

    def build_columns(self):
        for column in self.columns:
            self.tree.remove_column(column)
        self.columns = []

        for pair in self.column_order():
            if not pair[0]:
                continue
            name = self.column_names[pair[1]][0]
            column = gtk.TreeViewColumn(name, gtk.CellRendererText(),
                                        text=pair[1])
            column.set_resizable(True)
            column.set_min_width(40)
            column.set_sort_column_id(self.column_names[pair[1]][1])
            self.columns.append(column)
            self.tree.append_column(column)

    def rebuild(self):
        self.model = self.build_model(self.get_data(),self.dbstate.db)
        self.tree.set_model(self.model)
        self.set_label()
        self.selection_changed()

    def get_tab_widget(self):
        return gtk.Label('UNDEFINED')

#-------------------------------------------------------------------------
#
# EventEmbedList
#
#-------------------------------------------------------------------------
class EventEmbedList(EmbeddedList):

    column_names = [
        (_('Description'),0),
        (_('ID'),1),
        (_('Type'),2),
        (_('Date'),3),
        (_('Place'),4),
        (_('Cause'),5),
        ]
    
    def __init__(self,dbstate,uistate,track,obj):
        self.obj = obj
        self.hbox = gtk.HBox()
        self.label = gtk.Label(_('Events'))
        self.hbox.show_all()
        
        EmbeddedList.__init__(self, dbstate, uistate, track, EventRefModel)

    def get_data(self):
        return self.obj.get_event_ref_list()

    def column_order(self):
        return ((1,0),(1,1),(1,2),(1,3),(1,4),(1,5))

    def set_label(self):
        if len(self.get_data()):
            self.label.set_text("<b>%s</b>" % _('Events'))
            self.label.set_use_markup(True)
        else:
            self.label.set_text(_('Events'))
        
    def get_tab_widget(self):
        return self.label

#-------------------------------------------------------------------------
#
# NoteTab
#
#-------------------------------------------------------------------------
class NoteTab(gtk.HBox):

    def __init__(self, note_obj):
        gtk.HBox.__init__(self)
        self.note_obj = note_obj

        self.text = gtk.TextView()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(self.text)
        self.pack_start(scroll,True)
        if note_obj:
            self.text.get_buffer().insert_at_cursor(note_obj.get())
        
        self.show_all()

    def rebuild(self):
        pass

    def get_tab_widget(self):
        return gtk.Label(_('Note'))

#-------------------------------------------------------------------------
#
# GalleryTab
#
#-------------------------------------------------------------------------
class GalleryTab(gtk.HBox):

    def __init__(self,db,  media_list):
        gtk.HBox.__init__(self)
        self.db = db
        self.media_list = media_list

        self.hbox = gtk.HBox()
        self.label = gtk.Label(_('Children'))

        self.iconmodel= gtk.ListStore(gtk.gdk.Pixbuf,str)
        self.iconlist = gtk.IconView()
        self.iconlist.set_pixbuf_column(0)
        self.iconlist.set_text_column(1)
        self.iconlist.set_model(self.iconmodel)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(self.iconlist)
        self.pack_start(scroll,True)

        self.rebuild()
        self.show_all()

    def get_data(self):
        return self.media_list

    def rebuild(self):
        for ref in self.media_list:
            obj = self.dbstate.db.get_object_from_handle(ref.get_reference_handle())
            pixbuf = self.get_image(obj)
            self.iconmodel.append(row=[pixbuf,obj.get_description()])
        self.set_label()

    def get_image(self,obj):
        import ImgManip
        
        mtype = obj.get_mime_type()
        if mtype[0:5] == "image":
            image = ImgManip.get_thumbnail_image(obj.get_path())
        else:
            image = GrampsMime.find_mime_type_pixbuf(mtype)
        if not image:
            image = gtk.gdk.pixbuf_new_from_file(const.icon)
        return image

    def get_tab_widget(self):
        return self.label

    def set_label(self):
        if len(self.get_data()):
            self.label.set_text("<b>%s</b>" % _('Gallery'))
            self.label.set_use_markup(True)
        else:
            self.label.set_text(_('Gallery'))

#-------------------------------------------------------------------------
#
# ChildModel
#
#-------------------------------------------------------------------------
class ChildModel(gtk.ListStore):

    _HANDLE_COL = -8

    def __init__(self, child_list,db):
        gtk.ListStore.__init__(self,int,str,str,str,str,str,str,str,str,str,int,int)
        self.db = db
        index = 1
        for child_handle in child_list:
            child = db.get_person_from_handle(child_handle)
            self.append(row=[index,
                             child.get_gramps_id(),
                             NameDisplay.displayer.display(child),
                             _GENDER[child.get_gender()],
                             self.column_birth_day(child),
                             self.column_death_day(child),
                             self.column_birth_place(child),
                             self.column_death_place(child),
                             child.get_handle(),
                             child.get_primary_name().get_sort_name(),
                             self.column_birth_sort(child),
                             self.column_death_sort(child),
                             ])
            index += 1

    def column_birth_day(self,data):
        event_ref = data.get_birth_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return DateHandler.get_date(event)
        else:
            return u""

    def column_birth_sort(self,data):
        event_ref = data.get_birth_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return event.get_date_object().get_sort_value()
        else:
            return 0

    def column_death_day(self,data):
        event_ref = data.get_death_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return DateHandler.get_date(event)
        else:
            return u""

    def column_death_sort(self,data):
        event_ref = data.get_death_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return event.get_date_object().get_sort_value()
        else:
            return 0
        
    def column_birth_place(self,data):
        event_ref = data.get_birth_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

    def column_death_place(self,data):
        event_ref = data.get_death_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

#-------------------------------------------------------------------------
#
# EventRefModel
#
#-------------------------------------------------------------------------
class EventRefModel(gtk.ListStore):

    def __init__(self,event_list,db):
        gtk.ListStore.__init__(self,str,str,str,str,str,str)
        self.db = db
        for event_ref in event_list:
            event = db.get_event_from_handle(event_ref.ref)
            self.append(row=[
                event.get_description(),
                event.get_gramps_id(),
                self.column_type(event),
                self.column_date(event_ref),
                self.column_place(event_ref),
                event.get_cause(),
                ])

    def column_type(self,event):
        t = event.get_type()
        if t[0] == RelLib.Event.CUSTOM:
            return t[1]
        else:
            return Utils.family_events[t[0]]

    def column_date(self,event_ref):
        event = self.db.get_event_from_handle(event_ref.ref)
        return DateHandler.get_date(event)

    def column_place(self,event_ref):
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

#-------------------------------------------------------------------------
#
# AttrModel
#
#-------------------------------------------------------------------------
class AttrModel(gtk.ListStore):

    def __init__(self,attr_list,db):
        gtk.ListStore.__init__(self,str,str)
        self.db = db
        for attr in attr_list:
            self.append(row=[
                self.type_name(attr),
                attr.get_value(),
                ])

    def type_name(self, attr):
        t = attr.get_type()
        if t[0] == RelLib.Attribute.CUSTOM:
            return t[1]
        else:
            return Utils.personal_attributes[t[0]]

#-------------------------------------------------------------------------
#
# FamilyAttrModel
#
#-------------------------------------------------------------------------
class FamilyAttrModel(AttrModel):

    def __init__(self,attr_list,db):
        AttrModel.__init__(self,attr_list,db)

    def type_name(self, attr):
        t = attr.get_type()
        if t[0] == RelLib.Attribute.CUSTOM:
            return t[1]
        else:
            return Utils.family_attributes[t[0]]

    

