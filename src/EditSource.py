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
# Standard python modules
#
#-------------------------------------------------------------------------
import os

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gtk import *
from gnome.ui import *
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import intl
import const
import utils
from RelLib import *
import ImageSelect

_ = intl.gettext

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

class EditSource:

    def __init__(self,source,db,func):
        self.source = source
        self.db = db
        self.callback = func
        self.path = db.getSavePath()
        self.not_loaded = 1

        self.top_window = libglade.GladeXML(const.gladeFile,"sourceEditor")
        sid = "s%s" % source.getId()
        plwidget = self.top_window.get_widget("photolist")
        self.gallery = ImageSelect.Gallery(source, self.path, sid, plwidget, db)
        self.title = self.top_window.get_widget("source_title")
        self.author = self.top_window.get_widget("author")
        self.pubinfo = self.top_window.get_widget("pubinfo")
        self.note = self.top_window.get_widget("source_note")

        self.title.set_text(source.getTitle())
        self.author.set_text(source.getAuthor())
        self.pubinfo.set_text(source.getPubInfo())

        self.note.set_point(0)
        self.note.insert_defaults(source.getNote())
        self.note.set_word_wrap(1)

        self.top_window.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_photolist_select_icon" : self.gallery.on_photo_select_icon,
            "on_photolist_button_press_event" : self.gallery.on_photolist_button_press_event,
            "on_switch_page" : self.on_switch_page,
            "on_addphoto_clicked" : self.gallery.on_add_photo_clicked,
            "on_deletephoto_clicked" : self.gallery.on_delete_photo_clicked,
            "on_sourceapply_clicked" : self.on_source_apply_clicked
            })

        self.top = self.top_window.get_widget("sourceEditor")

        if self.source.getId() == "":
            self.top_window.get_widget("add_photo").set_sensitive(0)
            self.top_window.get_widget("delete_photo").set_sensitive(0)

        self.top.editable_enters(self.title);
        self.top.editable_enters(self.author);
        self.top.editable_enters(self.pubinfo);

    def on_source_apply_clicked(self,obj):

        title = self.title.get_text()
        author = self.author.get_text()
        pubinfo = self.pubinfo.get_text()
        note = self.note.get_chars(0,-1)
    
        if author != self.source.getAuthor():
            self.source.setAuthor(author)
            utils.modified()
        
        if title != self.source.getTitle():
            self.source.setTitle(title)
            utils.modified()
        
        if pubinfo != self.source.getPubInfo():
            self.source.setPubInfo(pubinfo)
            utils.modified()
        
        if note != self.source.getNote():
            self.source.setNote(note)
            utils.modified()

        utils.destroy_passed_object(self.top)
        self.callback(self.source)

    def on_switch_page(self,obj,a,page):
        if page == 2 and self.not_loaded:
            self.not_loaded = 0
            self.gallery.load_images()

