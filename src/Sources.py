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
from gtk import *
from gnome.ui import *
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------

import const
import utils
from RelLib import *

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------

SOURCEDISP = "s"
ACTIVESRC  = "a"
INDEX      = "i"

#-------------------------------------------------------------------------
#
# SourceEditor
#
#-------------------------------------------------------------------------
class SourceEditor:

    #---------------------------------------------------------------------
    #
    # __init__ - Creates a source editor window associated with an event
    #
    #---------------------------------------------------------------------
    def __init__(self,srcref,database,update=None):

        self.db = database
        self.update = update
        self.source_ref = srcref
        self.showSource = libglade.GladeXML(const.gladeFile, "sourceDisplay")
        self.showSource.signal_autoconnect({
            "on_sourceok_clicked" : on_sourceok_clicked,
            "destroy_passed_object" : utils.destroy_passed_object
            })
        self.sourceDisplay = self.get_widget("sourceDisplay")
        self.source_field = self.get_widget("sourceList")
        self.title_menu = self.get_widget("source_title")
        self.author_field = self.get_widget("sauthor")
        self.pub_field = self.get_widget("spubinfo")

        self.active_source = None
        self.draw()
        self.sourceDisplay.set_data(SOURCEDISP,self)
        self.sourceDisplay.show()

    #---------------------------------------------------------------------
    #
    # get_widget - returns the widget associated with the specified name
    #
    #---------------------------------------------------------------------
    def get_widget(self,name):
        return self.showSource.get_widget(name)

    def draw(self):

        typeMenu = GtkMenu()
        menuitem = GtkMenuItem('None')
        menuitem.set_data("s",None)
        menuitem.set_data("o",self)
        menuitem.connect("activate",on_source_changed)
        menuitem.show()
        typeMenu.append(menuitem)
        index = 1
        active = 0
        save = 0
        if self.source_ref:
            self.base = self.source_ref.getBase()
        else:
            self.base = None

        for src in self.db.getSourceMap().values():
            if src == self.base:
                active = 1
                save = index
            menuitem = GtkMenuItem(src.getTitle())
            menuitem.set_data("s",src)
            menuitem.set_data("o",self)
            menuitem.connect("activate",on_source_changed)
            menuitem.show()
            typeMenu.append(menuitem)
            index = index + 1
        typeMenu.set_active(save)
        self.title_menu.set_menu(typeMenu)

        self.get_widget("spage").set_sensitive(active)
        self.get_widget("sdate").set_sensitive(active)
        self.get_widget("stext").set_sensitive(active)
        self.get_widget("scomment").set_sensitive(active)

        if self.source_ref:
            self.get_widget("spage").set_text(self.source_ref.getPage())
            date = self.source_ref.getDate()
            if date:
                self.get_widget("sdate").set_text(date.getDate())

            text = self.get_widget("stext")
            text.set_point(0)
            text.insert_defaults(self.source_ref.getText())
            text.set_word_wrap(1)

            scom = self.get_widget("scomment")
            scom.set_point(0)
            scom.insert_defaults(self.source_ref.getComments())
            scom.set_word_wrap(1)

            src = self.source_ref.getBase()
            self.active_source = src
            if src:
                self.author_field.set_text(src.getAuthor())
                self.pub_field.set_text(src.getPubInfo())
        else:
            self.author_field.set_text("")
            self.pub_field.set_text("")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_sourceok_clicked(obj):

    src_edit = obj.get_data(SOURCEDISP)

    if src_edit.active_source != src_edit.source_ref.getBase():
        src_edit.source_ref.setBase(src_edit.active_source)

    page = src_edit.get_widget("spage").get_text()
    date = src_edit.get_widget("sdate").get_text()
    text = src_edit.get_widget("stext").get_chars(0,-1)
    comments = src_edit.get_widget("scomment").get_chars(0,-1)

    src_edit.source_ref.setPage(page)
    src_edit.source_ref.getDate().set(date)
    src_edit.source_ref.setText(text)
    src_edit.source_ref.setComments(comments)

    if src_edit.update:
        if src_edit.source_ref.getBase():
            val = src_edit.source_ref.getBase().getTitle()
        else:
            val = ""
        src_edit.update.set_text(val)
        
    utils.modified()
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_source_changed(obj):

    src_entry = obj.get_data("o")
    src_entry.active_source = obj.get_data("s")

    if src_entry.active_source == None:
        active = 0
        src_entry.author_field.set_text("")
        src_entry.pub_field.set_text("")
    else:
        active = 1
        src_entry.author_field.set_text(src_entry.active_source.getAuthor())
        src_entry.pub_field.set_text(src_entry.active_source.getPubInfo())

    src_entry.get_widget("spage").set_sensitive(active)
    src_entry.get_widget("sdate").set_sensitive(active)
    src_entry.get_widget("stext").set_sensitive(active)
    src_entry.get_widget("scomment").set_sensitive(active)
