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
import GDK
import gtk
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import Sorter
from RelLib import *

#-------------------------------------------------------------------------
#
# SourceSelector
#
#-------------------------------------------------------------------------

class SourceSelector:
    def __init__(self,srclist,parent,update=None):
        self.db = parent.db
        self.parent = parent
        self.orig = srclist
        self.list = []
        for s in self.orig:
            self.list.append(SourceRef(s))
        self.update=update
        self.top = libglade.GladeXML(const.srcselFile,"sourcesel")
        self.top.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_add_src_clicked"    : self.on_add_src_clicked,
            "on_src_button_press"   : self.src_double_click,
            "on_del_src_clicked"    : self.on_del_src_clicked,
            "on_edit_src_clicked"   : self.on_edit_src_clicked,
            "on_src_ok_clicked"     : self.on_src_ok_clicked,
            })
        self.sourcesel = self.top.get_widget("sourcesel")
        self.slist = self.top.get_widget("slist")
        slist_map = [ (0, self.top.get_widget('arrow1')),
                      (1, self.top.get_widget('arrow2'))]
        
        self.srcsort = Sorter.Sorter(self.slist, slist_map, 'source')
        self.redraw()
        self.sourcesel.show()
        
    def src_double_click(self,obj,event):
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            self.on_edit_src_clicked(obj)

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

    def on_src_ok_clicked(self,obj):
        del self.orig[:]
        for s in self.list:
            self.orig.append(s)
        if self.update:
            self.update(self.orig)
        Utils.destroy_passed_object(self.sourcesel)
    
    def on_edit_src_clicked(self,obj):
        sel = obj.selection
        if len(sel) > 0:
            row = sel[0]
            src = obj.get_row_data(row)
            SourceEditor(src,self.db,self.update_clist,self)

    def update_clist(self,inst,ref):
        inst.redraw()

    def on_add_src_clicked(self,obj):
        src = SourceRef()
        SourceEditor(src,self.db,self.add_ref,self)

    def on_del_src_clicked(self,obj):
        sel = obj.selection
        if len(sel) > 0:
            row = sel[0]
            del self.list[row]
            self.redraw()

    def add_ref(self,inst,ref):
        self.parent.lists_changed = 1
        inst.list.append(ref)
        inst.redraw()

#-------------------------------------------------------------------------
#
# SourceTab
#
#-------------------------------------------------------------------------
class SourceTab:
    def __init__(self,srclist,parent,top,clist):
        self.db = parent.db
        self.parent = parent
        self.list = srclist
        self.top = top
        self.slist = clist
        self.top.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_add_src_clicked"    : self.on_add_src_clicked,
            "on_src_button_press"   : self.src_double_click,
            "on_del_src_clicked"    : self.on_del_src_clicked,
            "on_edit_src_clicked"   : self.on_edit_src_clicked,
            })
        slist_map = [ (0, self.top.get_widget('arrow1')),
                      (1, self.top.get_widget('arrow2'))]
        
        self.srcsort = Sorter.Sorter(self.slist, slist_map, 'source')
        self.redraw()

    def src_double_click(self,obj,event):
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            self.on_edit_src_clicked(obj)

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

    def update_clist(self,inst,ref):
        inst.redraw()
        self.parent.lists_changed = 1

    def on_edit_src_clicked(self,obj):
        sel = obj.selection
        if len(sel) > 0:
            row = sel[0]
            src = obj.get_row_data(row)
            SourceEditor(src,self.db,self.update_clist,self)

    def on_add_src_clicked(self,obj):
        src = SourceRef()
        SourceEditor(src,self.db,self.add_ref,self)

    def add_ref(self,inst,ref):
        self.parent.lists_changed = 1
        inst.list.append(ref)
        inst.redraw()

    def on_del_src_clicked(self,obj):
        sel = obj.selection
        if len(sel) > 0:
            row = sel[0]
            del self.list[row]
            self.redraw()

#-------------------------------------------------------------------------
#
# SourceEditor
#
#-------------------------------------------------------------------------
class SourceEditor:

    def __init__(self,srcref,database,update=None,parent=None):

        self.db = database
        self.parent = parent
        self.update = update
        self.source_ref = srcref
        self.showSource = libglade.GladeXML(const.srcselFile, "sourceDisplay")
        self.showSource.signal_autoconnect({
            "on_combo_insert_text"  : Utils.combo_insert_text,
            "on_sourceok_clicked"   : self.on_sourceok_clicked,
            "on_source_changed"     : self.on_source_changed,
            "destroy_passed_object" : Utils.destroy_passed_object
            })
        self.sourceDisplay = self.get_widget("sourceDisplay")
        self.source_field = self.get_widget("sourceList")
        self.title_menu = self.get_widget("source_title")
        self.title_menu.set_data("o",self)
        self.conf_menu = self.get_widget("conf")
        Utils.build_confidence_menu(self.conf_menu)
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
        self.sourceDisplay.show()

    def get_widget(self,name):
        """returns the widget associated with the specified name"""
        return self.showSource.get_widget(name)

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

        values = []
        for v in self.db.getSourceKeys():
            values.append(self.db.getSourceDisplay(v))
        values.sort()

        sel_child = None
        list = []
        for src in values:
            l = gtk.GtkLabel("%s [%s]" % (src[0],src[1]))
            l.show()
            l.set_alignment(0,0.5)
            c = gtk.GtkListItem()
            c.add(l)
            c.set_data("s",src[1])
            c.show()
            list.append(c)
            if self.active_source and self.active_source.getId() == src[1]:
                sel_child = c

        self.title_menu.list.append_items(list)
        
        if sel_child != None:
            self.title_menu.list.select_child(sel_child)

    def on_sourceok_clicked(self,obj):
        if self.active_source != self.source_ref.getBase():
            self.source_ref.setBase(self.active_source)
        
        page = self.get_widget("spage").get_text()
        date = self.get_widget("sdate").get_text()
        text = self.get_widget("stext").get_chars(0,-1)
        conf = self.get_widget("conf").get_menu().get_active().get_data('a')

        comments = self.get_widget("scomment").get_chars(0,-1)

        self.source_ref.setPage(page)
        self.source_ref.getDate().set(date)
        self.source_ref.setText(text)
        self.source_ref.setComments(comments)
        self.source_ref.setConfidence(conf)

        if self.update:
            self.update(self.parent,self.source_ref)
        
        Utils.modified()
        Utils.destroy_passed_object(obj)

    def on_source_changed(self,obj):
        id = obj.list.get_selection()[0].get_data("s")
        self.active_source = self.db.getSource(id)

        if self.active_source != None:
            self.author_field.set_text(self.active_source.getAuthor())
            self.pub_field.set_text(self.active_source.getPubInfo())

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_title(a,b):
    return cmp(a.getTitle(),b.getTitle())
               

        
