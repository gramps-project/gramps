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
MENUVAL    = "a"

class SourceSelector:

    def __init__(self,srclist,parent,update=None):
        self.db = parent.db
        self.parent = parent
        self.orig = srclist
        self.list = []
        for s in self.orig:
            self.list.append(SourceRef(s))
        self.update=update
        self.top = libglade.GladeXML(const.gladeFile,"sourcesel")
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_add_src_clicked"    : on_add_src_clicked,
            "on_del_src_clicked"    : on_del_src_clicked,
            "on_edit_src_clicked"   : on_edit_src_clicked,
            "on_src_ok_clicked"     : on_src_ok_clicked,
            })
        self.sourcesel = self.top.get_widget("sourcesel")
        self.slist = self.top.get_widget("slist")
        self.slist.set_data("o",self)
        self.redraw()
        self.sourcesel.show()

    def redraw(self):
        index = 0
        self.slist.freeze()
        self.slist.clear()
        for s in self.list:
            base = s.getBase()
            self.slist.append([base.getId(),base.getTitle()])
            self.slist.set_row_data(index,s)
            index = index + 1
        self.slist.thaw()

def on_src_ok_clicked(obj):
    top = obj.get_data("o")
    del top.orig[:]
    for s in top.list:
        top.orig.append(s)
    top.update(top.parent)
    utils.destroy_passed_object(top.sourcesel)
    
def on_edit_src_clicked(obj):
    sel = obj.selection
    if len(sel) > 0:
        row = sel[0]
        src = obj.get_row_data(row)
        inst = obj.get_data("o")
        SourceEditor(src,inst.db,update_clist,inst)

def update_clist(inst,ref):
    inst.redraw()

def on_add_src_clicked(obj):
    inst = obj.get_data("o")
    src = SourceRef()
    SourceEditor(src,inst.db,add_ref,inst)

def add_ref(inst,ref):
    inst.list.append(ref)
    inst.redraw()

def on_del_src_clicked(obj):
    inst = obj.get_data("o")
    
    sel = obj.selection
    if len(sel) > 0:
        row = sel[0]
        del inst.list[row]
        inst.redraw()
        
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
    def __init__(self,srcref,database,update=None,parent=None):

        self.db = database
        self.parent = parent
        self.update = update
        self.source_ref = srcref
        self.showSource = libglade.GladeXML(const.gladeFile, "sourceDisplay")
        self.showSource.signal_autoconnect({
            "on_sourceok_clicked" : on_sourceok_clicked,
            "on_source_changed": on_source_changed,
            "destroy_passed_object" : utils.destroy_passed_object
            })
        self.sourceDisplay = self.get_widget("sourceDisplay")
        self.source_field = self.get_widget("sourceList")
        self.title_menu = self.get_widget("source_title")
        self.title_menu.set_data("o",self)
        self.conf_menu = self.get_widget("conf")
        utils.build_confidence_menu(self.conf_menu)
        self.conf_menu.set_history(srcref.getConfidence())

        self.author_field = self.get_widget("sauthor")
        self.pub_field = self.get_widget("spubinfo")

        # Typing CR selects OK button
        self.sourceDisplay.editable_enters(self.get_widget("spage"))
        self.sourceDisplay.editable_enters(self.get_widget("sdate"))

        if self.source_ref:
            self.active_source = self.source_ref.getBase()
        else:
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

    #---------------------------------------------------------------------
    #
    # draw
    #
    #---------------------------------------------------------------------
    def draw(self):

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

        values = self.db.getSourceMap().values()
        values.sort(by_title)

        sel_child = None
        list = []
        for src in values:
            l = GtkLabel("%s [%s]" % (src.getTitle(),src.getId()))
            l.show()
            l.set_alignment(0,0.5)
            c = GtkListItem()
            c.add(l)
            c.set_data("s",src)
            c.show()
            list.append(c)
            if self.active_source == None:
                self.active_source = src
                sel_child = c

        self.title_menu.list.append_items(list)
        if sel_child != None:
            self.title_menu.list.select_child(sel_child)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_title(a,b):
    return cmp(a.getTitle(),b.getTitle())
               
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
    conf = src_edit.get_widget("conf").get_menu().get_active().get_data(MENUVAL)
    comments = src_edit.get_widget("scomment").get_chars(0,-1)

    src_edit.source_ref.setPage(page)
    src_edit.source_ref.getDate().set(date)
    src_edit.source_ref.setText(text)
    src_edit.source_ref.setComments(comments)
    src_edit.source_ref.setConfidence(conf)

    if src_edit.update:
        src_edit.update(src_edit.parent,src_edit.source_ref)
        
    utils.modified()
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_source_changed(obj):

    src_entry = obj.get_data("o")
    src_entry.active_source = obj.list.get_selection()[0].get_data("s")

    if src_entry.active_source == None:
        src_entry.author_field.set_text(src_entry.active_source.getAuthor())
        src_entry.pub_field.set_text(src_entry.active_source.getPubInfo())
