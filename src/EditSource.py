#! /usr/bin/python -O
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
import const
import Utils
import GrampsCfg
from RelLib import *
import ImageSelect

from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

class EditSource:

    def __init__(self,source,db,func=None):
        self.source = source
        self.db = db
        self.callback = func
        self.path = db.getSavePath()
        self.not_loaded = 1
        self.ref_not_loaded = 1

        self.top_window = libglade.GladeXML(const.gladeFile,"sourceEditor")
        plwidget = self.top_window.get_widget("photolist")
        self.gallery = ImageSelect.Gallery(source, self.path, plwidget, db, self)
        self.title = self.top_window.get_widget("source_title")
        self.author = self.top_window.get_widget("author")
        self.pubinfo = self.top_window.get_widget("pubinfo")
        self.note = self.top_window.get_widget("source_note")
        self.refinfo = self.top_window.get_widget("refinfo")
        
        self.title.set_text(source.getTitle())
        self.author.set_text(source.getAuthor())
        self.pubinfo.set_text(source.getPubInfo())

        self.note.set_point(0)
        self.note.insert_defaults(source.getNote())
        self.note.set_word_wrap(1)

        self.top_window.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_photolist_select_icon" : self.gallery.on_photo_select_icon,
            "on_photolist_button_press_event" : self.gallery.on_button_press_event,
            "on_switch_page" : self.on_switch_page,
            "on_addphoto_clicked" : self.gallery.on_add_photo_clicked,
            "on_deletephoto_clicked" : self.gallery.on_delete_photo_clicked,
            "on_edit_properties_clicked": self.gallery.popup_change_description,
            "on_sourceapply_clicked" : self.on_source_apply_clicked
            })

        self.top = self.top_window.get_widget("sourceEditor")

        if self.source.getId() == "":
            self.top_window.get_widget("add_photo").set_sensitive(0)
            self.top_window.get_widget("delete_photo").set_sensitive(0)

        self.top.editable_enters(self.title)
        self.top.editable_enters(self.author)
        self.top.editable_enters(self.pubinfo)

    def display_references(self):
        p_event_list = []
        p_attr_list = []
        p_addr_list = []
        p_name_list = []
        m_list = []
        f_event_list = []
        f_attr_list = []
        p_list = []
        for key in self.db.getPlaceKeys():
            p = self.db.getPlace(key) 
            name = p.get_title()
            for sref in p.getSourceRefList():
                if sref.getBase() == self.source:
                    p_list.append(name)
        for key in self.db.getPersonKeys():
            p = self.db.getPerson(key)
            name = GrampsCfg.nameof(p)
            for v in p.getEventList() + [p.getBirth(), p.getDeath()]:
                for sref in v.getSourceRefList():
                    if sref.getBase() == self.source:
                        p_event_list.append((name,v.getName()))
            for v in p.getAttributeList():
                for sref in v.getSourceRefList():
                    if sref.getBase() == self.source:
                        p_attr_list.append((name,v.getType()))
            for v in p.getAlternateNames() + [p.getPrimaryName()]:
                for sref in v.getSourceRefList():
                    if sref.getBase() == self.source:
                        p_name_list.append((name,v.getName()))
            for v in p.getAddressList():
                for sref in v.getSourceRefList():
                    if sref.getBase() == self.source:
                        p_addr_list.append((name,v.getStreet()))
        for p in self.db.getObjectMap().values():
            name = p.getDescription()
            for sref in p.getSourceRefList():
                if sref.getBase() == self.source:
                    m_list.append(name)
        for p in self.db.getFamilyMap().values():
            f = p.getFather()
            m = p.getMother()
            if f and m:
                name = _("%(father)s and %(mother)s") % {
                    "father" : GrampsCfg.nameof(f),
                    "mother" : GrampsCfg.nameof(m)}
            elif f:
                name = GrampsCfg.nameof(f)
            else:
                name = GrampsCfg.nameof(m)
            for v in p.getEventList():
                for sref in v.getSourceRefList():
                    if sref.getBase() == self.source:
                        f_event_list.append((name,v.getName()))
            for v in p.getAttributeList():
                for sref in v.getSourceRefList():
                    if sref.getBase() == self.source:
                        f_attr_list.append((name,v.getType()))

        slist = self.top_window.get_widget('slist')
        if len(p_event_list) > 0:
            for p in p_event_list:
                slist.append([_("Individual Events"),p[0],
                              const.display_pevent(p[1])])
        if len(p_attr_list) > 0:
            for p in p_attr_list:
                slist.append([_("Individual Attributes"),p[0],
                              const.display_pattr(p[1])])
        if len(p_name_list) > 0:
            for p in p_name_list:
                slist.append([_("Individual Names"),p[0],p[1]])
        if len(p_addr_list) > 0:
            for p in p_addr_list:
                slist.append([_("Individual Addresses"),p[0],p[1]])
        if len(f_event_list) > 0:
            for p in f_event_list:
                slist.append([_("Family Events"),p[0],
                              const.display_fevent(p[1])])
        if len(f_attr_list) > 0:
            for p in f_event_list:
                slist.append([_("Family Attributes"),p[0],
                              const.display_fattr(p[1])])
        if len(m_list) > 0:
            for p in m_list:
                slist.append([_("Media Objects"),p,''])
        if len(p_list) > 0:
            for p in p_list:
                slist.append([_("Places"),p,''])

    def on_source_apply_clicked(self,obj):

        title = self.title.get_text()
        author = self.author.get_text()
        pubinfo = self.pubinfo.get_text()
        note = self.note.get_chars(0,-1)
    
        if author != self.source.getAuthor():
            self.source.setAuthor(author)
            Utils.modified()
        
        if title != self.source.getTitle():
            self.source.setTitle(title)
            Utils.modified()
        
        if pubinfo != self.source.getPubInfo():
            self.source.setPubInfo(pubinfo)
            Utils.modified()
        
        if note != self.source.getNote():
            self.source.setNote(note)
            Utils.modified()

        Utils.destroy_passed_object(self.top)
        if self.callback:
            self.callback(self.source)

    def on_switch_page(self,obj,a,page):
        if page == 2 and self.not_loaded:
            self.not_loaded = 0
            self.gallery.load_images()
        elif page == 3 and self.ref_not_loaded:
            self.ref_not_loaded = 0
            self.display_references()


class DelSrcQuery:
    def __init__(self,source,db,update):
        self.source = source
        self.db = db
        self.update = update

    def delete_source(self,object):
        m = 0
        l = []
        for sref in object.getSourceRefList():
            if sref.getBase() != self.source:
                l.append(sref)
            else:
                m = 1
        if m:
            object.setSourceRefList(l)

    def query_response(self):
        del self.db.getSourceMap()[self.source.getId()]
        Utils.modified()

        for key in self.db.getPersonKeys():
            p = self.db.getPerson(key)
            for v in p.getEventList() + [p.getBirth(), p.getDeath()]:
                self.delete_source(v)

            for v in p.getAttributeList():
                self.delete_source(v)

            for v in p.getAlternateNames() + [p.getPrimaryName()]:
                self.delete_source(v)

            for v in p.getAddressList():
                self.delete_source(v)

        for p in self.db.getFamilyMap().values():
            for v in p.getEventList():
                self.delete_source(v)

            for v in p.getAttributeList():
                self.delete_source(v)

        for p in self.db.getObjectMap().values():
            self.delete_source(p)

        for key in self.db.getPlaceKeys():
            self.delete_source(self.db.getPlace(key))

        self.update(0)



