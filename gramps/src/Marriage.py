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

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gnome.ui import *
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------

import const
import Config
import utils
from RelLib import *
import ImageSelect
from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# Marriage class
#
#-------------------------------------------------------------------------
class Marriage:

    #-------------------------------------------------------------------------
    #
    # Initializes the class, and displays the window
    #
    #-------------------------------------------------------------------------
    def __init__(self,family,db):
        self.family = family
        self.db = db
        self.path = db.getSavePath()

        self.top = libglade.GladeXML(const.marriageFile,"marriageEditor")
        top_window = self.get_widget("marriageEditor")
        fid = "f%s" % family.getId()
        plwidget = self.top.get_widget("photolist")
        self.gallery = ImageSelect.Gallery(family, self.path, fid, plwidget, db)
        self.top.signal_autoconnect({
            "destroy_passed_object" : self.on_cancel_edit,
            "on_add_attr_clicked" : self.on_add_attr_clicked,
            "on_addphoto_clicked" : self.gallery.on_add_photo_clicked,
            "on_attr_list_select_row" : self.on_attr_list_select_row,
            "on_combo_insert_text"  : utils.combo_insert_text,
            "on_close_marriage_editor" : self.on_close_marriage_editor,
            "on_delete_attr_clicked" : self.on_delete_attr_clicked,
            "on_delete_event" : self.on_delete_event,
            "on_deletephoto_clicked" : self.gallery.on_delete_photo_clicked,
            "on_edit_properties_clicked": self.gallery.popup_change_description,
            "on_marriageAddBtn_clicked" : self.on_add_clicked,
            "on_marriageDeleteBtn_clicked" : self.on_delete_clicked,
            "on_marriageEventList_select_row" : self.on_select_row,
            "on_marriageUpdateBtn_clicked" : self.on_update_clicked,
            "on_photolist_button_press_event" : self.gallery.on_photolist_button_press_event,
            "on_photolist_select_icon" : self.gallery.on_photo_select_icon,
            "on_update_attr_clicked" : self.on_update_attr_clicked,
            })

        text_win = self.get_widget("marriageTitle")
        title = _("%s and %s") % (Config.nameof(family.getFather()),
                                  Config.nameof(family.getMother()))
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
        self.event_details = self.get_widget("event_details")
        self.attr_details_field = self.get_widget("attr_details")

        self.event_list.set_column_visibility(3,Config.show_detail)
        self.attr_list.set_column_visibility(2,Config.show_detail)

        self.elist = family.getEventList()[:]
        self.alist = family.getAttributeList()[:]
        self.lists_changed = 0

        # set initial data
        self.gallery.load_images()

        self.type_field.set_popdown_strings(const.familyRelations)
        frel = const.display_frel(family.getRelationship())
        self.type_field.entry.set_text(frel)
        self.gid.set_text(family.getId())
        self.gid.set_editable(Config.id_edit)
        
        # set notes data
        self.notes_field.set_point(0)
        self.notes_field.insert_defaults(family.getNote())
        self.notes_field.set_word_wrap(1)

        # Typing CR selects OK button
        top_window.editable_enters(self.notes_field);
        top_window.editable_enters(self.get_widget("combo-entry1"));
        
        self.redraw_event_list()
        self.redraw_attr_list()
        top_window.show()

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def update_lists(self):
        self.family.setEventList(self.elist)
        self.family.setAttributeList(self.alist)

    def redraw_attr_list(self):
        utils.redraw_list(self.alist,self.attr_list,disp_attr)

    def redraw_event_list(self):
        utils.redraw_list(self.elist,self.event_list,disp_event)

    def get_widget(self,name):
        return self.top.get_widget(name)

    def did_data_change(self):
        changed = 0
        relation = self.type_field.entry.get_text()
        if const.save_frel(relation) != self.family.getRelationship():
            changed = 1

        text = self.notes_field.get_chars(0,-1)
        if text != self.family.getNote():
            changed = 1
        
        if self.lists_changed:
            changed = 1

        idval = self.gid.get_text()
        if self.family.getId() != idval:
            changed = 1

        return changed

    def on_cancel_edit(self,obj):

        if self.did_data_change():
            global quit
            q = _("Data was modified. Are you sure you want to abandon your changes?")
            quit = obj
            GnomeQuestionDialog(q,cancel_callback)
        else:
            utils.destroy_passed_object(obj)

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
                utils.modified()
            else:
                msg1 = _("GRAMPS ID value was not changed.")
                GnomeWarningDialog("%s" % msg1)

        relation = self.type_field.entry.get_text()
        if const.save_frel(relation) != self.family.getRelationship():
            father = self.family.getFather()
            mother = self.family.getMother()
            if father.getGender() == mother.getGender():
                self.family.setRelationship("Partners")
            else:
                val = const.save_frel(relation)
                if val == "Partners":
                    val = "Unknown"
                if father.getGender() == Person.female or \
                   mother.getGender() == Person.male:
                    self.family.setFather(mother)
                    self.family.setMother(father)
                self.family.setRelationship(val)
            utils.modified()

        text = self.notes_field.get_chars(0,-1)
        if text != self.family.getNote():
            self.family.setNote(text)
            utils.modified()

        utils.destroy_passed_object(self.get_widget("marriageEditor"))

        self.update_lists()
        if self.lists_changed:
            utils.modified()

    def on_add_clicked(self,obj):
        import EventEdit
        name = utils.family_name(self.family)
        EventEdit.EventEditor(self,name,const.marriageEvents,const.save_pevent,None,None,0)

    def on_update_clicked(self,obj):
        import EventEdit
        if len(obj.selection) <= 0:
            return

        event = obj.get_row_data(obj.selection[0])
        name = utils.family_name(self.family)
        EventEdit.EventEditor(self,name,const.marriageEvents,const.save_pevent,event,None,0)

    def on_delete_clicked(self,obj):
        if utils.delete_selected(obj,self.elist):
            self.lists_changed = 1
            self.redraw_event_list()

    def on_select_row(self,obj,row,b,c):
        event = obj.get_row_data(row)
    
        self.date_field.set_text(event.getDate())
        self.place_field.set_text(event.getPlaceName())
        self.cause_field.set_text(event.getCause())
        self.name_field.set_label(const.display_fevent(event.getName()))
        self.event_details.set_text(utils.get_detail_text(event))
        self.descr_field.set_text(event.getDescription())

    def on_attr_list_select_row(self,obj,row,b,c):
        attr = obj.get_row_data(row)

        self.attr_type.set_label(const.display_fattr(attr.getType()))
        self.attr_value.set_text(attr.getValue())
        self.attr_details_field.set_text(utils.get_detail_text(attr))

    def on_update_attr_clicked(self,obj):
        import AttrEdit
        if len(obj.selection) > 0:
            row = obj.selection[0]
            attr = obj.get_row_data(row)
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
        if utils.delete_selected(obj,self.alist):
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


#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def disp_attr(attr):
    detail = utils.get_detail_flags(attr)
    return [const.display_fattr(attr.getType()),attr.getValue(),detail]

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def disp_event(event):
    return [const.display_fevent(event.getName()), event.getQuoteDate(),
            event.getPlaceName(), utils.get_detail_flags(event)]

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def cancel_callback(a):
    if a==0:
        utils.destroy_passed_object(quit)

