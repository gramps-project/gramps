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
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk.glade
import gnome

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import GrampsCfg
import ImageSelect
import ListModel

from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

class EditSource:

    def __init__(self,source,db,parent_window=None,func=None):
        self.source = source
        self.db = db
        self.callback = func
        self.path = db.getSavePath()
        self.not_loaded = 1
        self.ref_not_loaded = 1
        self.lists_changed = 0
	self.gallery_ok = 0

        self.top_window = gtk.glade.XML(const.gladeFile,"sourceEditor","gramps")
        self.top = self.top_window.get_widget("sourceEditor")

        Utils.set_titles(self.top,self.top_window.get_widget('title'),
                         _('Source Editor'))
        
        plwidget = self.top_window.get_widget("iconlist")
        self.gallery = ImageSelect.Gallery(source, self.path, plwidget, db, self, self.top)
        self.author = self.top_window.get_widget("author")
        self.pubinfo = self.top_window.get_widget("pubinfo")
        self.abbrev = self.top_window.get_widget("abbrev")
        self.note = self.top_window.get_widget("source_note")
        self.notes_buffer = self.note.get_buffer()
        self.gallery_label = self.top_window.get_widget("gallerySourceEditor")
        self.refs_label = self.top_window.get_widget("refsSourceEditor")
        self.notes_label = self.top_window.get_widget("notesSourceEditor")
        self.flowed = self.top_window.get_widget("source_flowed")
        self.preform = self.top_window.get_widget("source_preform")
        
        self.refinfo = self.top_window.get_widget("refinfo")
        
        self.title = self.top_window.get_widget("source_title")
        self.title.set_text(source.getTitle())
        self.author.set_text(source.getAuthor())
        self.pubinfo.set_text(source.getPubInfo())
        self.abbrev.set_text(source.getAbbrev())

        if source.getNote():
            self.notes_buffer.set_text(source.getNote())
            Utils.bold_label(self.notes_label)
            if source.getNoteFormat() == 1:
            	self.preform.set_active(1)
            else:
                self.flowed.set_active(1)

        if self.source.getPhotoList():
            Utils.bold_label(self.gallery_label)

        self.top_window.signal_autoconnect({
            "on_switch_page" : self.on_switch_page,
            "on_addphoto_clicked" : self.gallery.on_add_photo_clicked,
            "on_selectphoto_clicked"    : self.gallery.on_select_photo_clicked,
            "on_deletephoto_clicked" : self.gallery.on_delete_photo_clicked,
            "on_editphoto_clicked"     : self.gallery.on_edit_photo_clicked,
            "on_edit_properties_clicked": self.gallery.popup_change_description,
            "on_sourceEditor_help_clicked" : self.on_help_clicked,
            })

        if self.source.getId() == "":
            self.top_window.get_widget("edit_photo").set_sensitive(0)
            self.top_window.get_widget("delete_photo").set_sensitive(0)

        if parent_window:
            self.top.set_transient_for(parent_window)

        self.display_references()
        self.top.show()
        self.val = self.top.run()
        if self.val == gtk.RESPONSE_OK:
            self.on_source_apply_clicked()
        self.top.destroy()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-complete')
        self.val = self.top.run()

    def close(self,obj):
        self.gallery.close(self.gallery_ok)
        self.top.destroy()
        
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

        titles = [(_('Source Type'),0,150),(_('Object'),1,150),(_('Value'),2,150)]
        
        self.model = ListModel.ListModel(slist,titles)
        any = 0
        if len(p_event_list) > 0:
            any = 1
            for p in p_event_list:
                self.model.add([_("Individual Events"),p[0],
                                const.display_pevent(p[1])])
        if len(p_attr_list) > 0:
            any = 1
            for p in p_attr_list:
                self.model.add([_("Individual Attributes"),p[0],
                               const.display_pattr(p[1])])
        if len(p_name_list) > 0:
            any = 1
            for p in p_name_list:
                self.model.add([_("Individual Names"),p[0],p[1]])
        if len(f_event_list) > 0:
            any = 1
            for p in f_event_list:
                self.model.add([_("Family Events"),p[0],
                                const.display_fevent(p[1])])
        if len(f_attr_list) > 0:
            any = 1
            for p in f_event_list:
                self.model.add([_("Family Attributes"),p[0],
                                const.display_fattr(p[1])])
        if len(m_list) > 0:
            any = 1
            for p in m_list:
                self.model.add([_("Media Objects"),p,''])
        if len(p_list) > 0:
            any = 1
            for p in p_list:
                self.model.add([_("Places"),p,''])
        
        if any:
            Utils.bold_label(self.refs_label)
        else:
            Utils.unbold_label(self.refs_label)
            
        self.ref_not_loaded = 0

    def on_source_apply_clicked(self):

        title = unicode(self.title.get_text())
        author = unicode(self.author.get_text())
        pubinfo = unicode(self.pubinfo.get_text())
        abbrev = unicode(self.abbrev.get_text())
        note = unicode(self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                  self.notes_buffer.get_end_iter(),gtk.FALSE))
        format = self.preform.get_active()

        if author != self.source.getAuthor():
            self.source.setAuthor(author)
            Utils.modified()
        
        if title != self.source.getTitle():
            self.source.setTitle(title)
            Utils.modified()
        
        if pubinfo != self.source.getPubInfo():
            self.source.setPubInfo(pubinfo)
            Utils.modified()
        
        if abbrev != self.source.getAbbrev():
            self.source.setAbbrev(abbrev)
            Utils.modified()
        
        if note != self.source.getNote():
            self.source.setNote(note)
            Utils.modified()

        if format != self.source.getNoteFormat():
            self.source.setNoteFormat(format)
            Utils.modified()

	if self.lists_changed:
            Utils.modified()
        
	self.gallery_ok = 1
        self.close(None)

        if self.callback:
            self.callback(self.source)

    def on_switch_page(self,obj,a,page):
        if page == 2 and self.not_loaded:
            self.not_loaded = 0
            self.gallery.load_images()
        elif page == 3 and self.ref_not_loaded:
            self.ref_not_loaded = 0
            self.display_references()
        text = unicode(self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                self.notes_buffer.get_end_iter(),gtk.FALSE))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)


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
        self.db.removeSource(self.source.getId())
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
