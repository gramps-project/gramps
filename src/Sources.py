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
    def __init__(self,active_event,database):

        self.db = database
        self.active_event = active_event
        self.showSource = libglade.GladeXML(const.gladeFile, "sourceDisplay")
        self.showSource.signal_autoconnect({
            "on_sourceok_clicked" : on_sourceok_clicked,
            "on_selectsource_clicked" : on_selectsource_clicked,
            "destroy_passed_object" : utils.destroy_passed_object
            })
        self.sourceDisplay = self.get_widget("sourceDisplay")
        self.source_field = self.get_widget("sourceList")
        self.title_field = self.get_widget("stitle")
        self.author_field = self.get_widget("sauthor")
        self.pub_field = self.get_widget("spubinfo")
        self.callno_field = self.get_widget("scallno")

        self.source = active_event.getSource()
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
        if self.source:
            self.get_widget("spage").set_text(self.source.getPage())
            date = self.source.getDate()
            if date:
                self.get_widget("sdate").set_text(date.getDate())

            text = self.get_widget("stext")
            text.set_point(0)
            text.insert_defaults(self.source.getText())
            text.set_word_wrap(1)

            scom = self.get_widget("scomment")
            scom.set_point(0)
            scom.insert_defaults(self.source.getComments())
            scom.set_word_wrap(1)

            srcRef = self.source.getBase()
            self.active_source = srcRef
            if srcRef:
                self.title_field.set_text(srcRef.getTitle())
                self.author_field.set_text(srcRef.getAuthor())
                self.pub_field.set_text(srcRef.getPubInfo())
                self.callno_field.set_text(srcRef.getCallNumber())
        else:
            self.title_field.set_text("")
            self.author_field.set_text("")
            self.pub_field.set_text("")
            self.callno_field.set_text("")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_sourceok_clicked(obj):

    src_edit = obj.get_data(SOURCEDISP)
    
    if src_edit.active_event:
        current_source = src_edit.active_event.getSource()
        if current_source == None:
            if src_edit.active_source:
                current_source = Source()
                src_edit.active_event.setSource(current_source)
            else:
                return
        if src_edit.active_source != current_source.getBase():
            src_edit.active_event.getSource().setBase(src_edit.active_source)
            utils.modified()
        if current_source.getBase() != src_edit.active_source:
            current_source.setBase(src_edit.active_source)
            utils.modified()
        page = src_edit.get_widget("spage").get_text()
        date = src_edit.get_widget("sdate").get_text()
        text = src_edit.get_widget("stext").get_chars(0,-1)
        comments = src_edit.get_widget("scomment").get_chars(0,-1)

        current_source.setPage(page)
        current_source.getDate().set(date)
        current_source.setText(text)
        current_source.setComments(comments)
        utils.modified()
        
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_selectsource_clicked(obj):

    src_edit = obj.get_data(SOURCEDISP)
    SourceChoose(src_edit)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class SourceChoose:
    
    def __init__(self,source_info):
        self.db = source_info.db
        self.source_info = source_info
        
        self.active_source = source_info.active_source
        self.selSrc = libglade.GladeXML(const.gladeFile, "sourceEditor")
        self.selSrc.signal_autoconnect({
            "on_addsource_clicked" : on_addsource_clicked,
            "on_updatesource_clicked" : on_updatesource_clicked,
            "on_deletesource_clicked" : on_deletesource_clicked,
            "on_sourceapply_clicked" : on_sourceapply_clicked,
            "on_sourceList_select_row" : on_sourceList_select_row,
            "destroy_passed_object" : utils.destroy_passed_object
            })

        self.title_field = self.selSrc.get_widget("source_title")
        self.author_field = self.selSrc.get_widget("author")
        self.pub_field = self.selSrc.get_widget("pubinfo")
        self.callno_field = self.selSrc.get_widget("callno")
        self.src_list = self.selSrc.get_widget("sourceList")
        
        if source_info.active_source:
            actsrc = source_info.active_source
            self.title_field.set_text(actsrc.getTitle())
            self.author_field.set_text(actsrc.getAuthor())
            self.pub_field.set_text(actsrc.getPubInfo())
            self.callno_field.set_text(actsrc.getCallNumber())
        self.active_source = source_info.active_source

        self.src_list.set_data(ACTIVESRC,self)
        self.src_list.set_data(INDEX,-1)
        self.redraw_sources()
        
    #---------------------------------------------------------------------
    #
    #
    #
    #---------------------------------------------------------------------
    def redraw_sources(self):
    
        self.src_list.clear()
        self.src_list.freeze()
        current_row = -1
        self.index = 0
        for src in self.db.getSourceMap().values():
            self.src_list.append([src.getTitle(),src.getAuthor()])
            self.src_list.set_row_data(self.index,src)
            if self.active_source == src:
                current_row = self.index
            self.index = self.index + 1

        self.src_list.select_row(current_row,0)
        self.src_list.moveto(current_row,0)

        self.src_list.set_data(INDEX,current_row)
        self.src_list.thaw()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_addsource_clicked(obj):
    src_obj = obj.get_data(ACTIVESRC)

    src_obj.active_source = SourceBase()
    title = src_obj.title_field.get_text()
    author = src_obj.author_field.get_text()
    src_obj.src_list.append([title,author])
    src_obj.db.addSource(src_obj.active_source)

    src_obj.active_source.setTitle(title)
    src_obj.active_source.setAuthor(author)
    src_obj.active_source.setCallNumber(src_obj.callno_field.get_text())
    src_obj.active_source.setPubInfo(src_obj.pub_field.get_text())
    src_obj.redraw_sources()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_deletesource_clicked(obj):
    src_obj = obj.get_data(ACTIVESRC)
    src_obj.active_source = None
    obj.set_data(INDEX,-1)
    src_obj.redraw_sources()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_updatesource_clicked(obj):

    src_obj = obj.get_data(ACTIVESRC)
    if src_obj.active_source:
        src_obj.active_source.setTitle(src_obj.title_field.get_text())
        src_obj.active_source.setAuthor(src_obj.author_field.get_text())
        src_obj.active_source.setCallNumber(src_obj.callno_field.get_text())
        src_obj.active_source.setPubInfo(src_obj.pub_field.get_text())
    src_obj.redraw_sources()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_sourceList_select_row(obj,row,b,c):
    obj.set_data(INDEX,row)
    src_obj = obj.get_data(ACTIVESRC)

    src_obj.active_source = obj.get_row_data(row)
    select_source = src_obj.active_source

    if select_source:
        src_obj.title_field.set_text(select_source.getTitle())
        src_obj.author_field.set_text(select_source.getAuthor())
        src_obj.pub_field.set_text(select_source.getPubInfo())
        src_obj.callno_field.set_text(select_source.getCallNumber())
    else:
        src_obj.title_field.set_text("")
        src_obj.author_field.set_text("")
        src_obj.pub_field.set_text("")
        src_obj.callno_field.set_text("")
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_sourceapply_clicked(obj):

    row = obj.get_data(INDEX)
    src_obj = obj.get_data(ACTIVESRC)

    src_obj.active_source = obj.get_row_data(row)
    if row == -1:
        src_obj.active_source = None
    elif not src_obj.active_source:
        src_obj.active_source = Source()

    if not src_obj.source_info.source:
        src_obj.source_info.source = Source()
    src_obj.source_info.source.setBase(src_obj.active_source)
    src_obj.source_info.draw()
    
    utils.destroy_passed_object(src_obj.selSrc.get_widget("sourceEditor"))

