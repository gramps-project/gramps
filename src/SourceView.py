#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001  Donald N. Allingham
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
# standard python modules
#
#-------------------------------------------------------------------------
import string

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import GDK
import GTK
import gnome.ui

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from RelLib import *
from QuestionDialog import QuestionDialog

import EditSource
import Utils
import GrampsCfg

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from intl import gettext
_ = gettext

class SourceView:
    def __init__(self,db,glade,update):
        self.glade = glade
        self.db = db
        self.update = update
        self.source_list = glade.get_widget("source_list")
        self.title_arrow = glade.get_widget("title_arrow")
        self.id_arrow    = glade.get_widget("src_id_arrow")
        self.author_arrow= glade.get_widget("author_arrow")
        self.source_list.set_column_visibility(3,0)
        self.source_list.set_column_visibility(4,0)
        self.id_arrow.hide()
        self.author_arrow.hide()
        self.sort_map = [3,1,4,-1]
        self.sort_arrow = [self.title_arrow, self.id_arrow, self.author_arrow]
        self.source_list.connect('click-column',self.click_column)

        self.sort_col,self.sort_dir = GrampsCfg.get_sort_cols("source",3,GTK.SORT_ASCENDING)
        if self.sort_col >= len(self.sort_arrow):
            self.sort_col = 0
            
        self.source_list.set_sort_type(self.sort_dir)
        self.source_list.set_sort_column(self.sort_map[self.sort_col])
        self.set_arrow(self.sort_col)

    def moveto(self,row):
        self.source_list.unselect_all()
        self.source_list.select_row(row,0)
        self.source_list.moveto(row)

    def set_arrow(self,column):

        for a in self.sort_arrow:
            a.hide()

        a = self.sort_arrow[column]
        a.show()
        if self.sort_dir == GTK.SORT_ASCENDING:
            a.set(GTK.ARROW_DOWN,2)
        else:
            a.set(GTK.ARROW_UP,2)
        
    def click_column(self,obj,column):

        new_col = self.sort_map[column]
        if new_col == -1:
            return

        data = None
        if len(obj.selection) == 1:
            data = obj.get_row_data(obj.selection[0])
        
        obj.freeze()
        if new_col == self.sort_col:
            if self.sort_dir == GTK.SORT_ASCENDING:
                self.sort_dir = GTK.SORT_DESCENDING
            else:
                self.sort_dir = GTK.SORT_ASCENDING
        else:
            self.sort_dir = GTK.SORT_ASCENDING

        self.set_arrow(column)
            
        obj.set_sort_type(self.sort_dir)
        obj.set_sort_column(new_col)
        self.sort_col = new_col
        GrampsCfg.save_sort_cols("source",self.sort_col,self.sort_dir)
        obj.sort()
        if data:
            row = obj.find_row_from_data(data)
            obj.moveto(row)
        obj.thaw()
        
    def load_sources(self):

        if len(self.source_list.selection) > 0:
            current_row = self.source_list.selection[0]
        else:
            current_row = 0

        self.source_list.clear()
        self.source_list.freeze()
        self.source_list.set_column_visibility(1,GrampsCfg.id_visible)

        index = 0
        for src in self.db.getSourceMap().values():
            id = src.getId()
            title = src.getTitle()
            author = src.getAuthor()
            stitle = string.upper(title)
            sauthor = string.upper(author)
            self.source_list.append([title,id,author,stitle,sauthor])
            self.source_list.set_row_data(index,src)
            index = index + 1

        if index > 0:
            self.source_list.select_row(current_row,0)
            self.source_list.moveto(current_row)

        self.source_list.sort()
        self.source_list.thaw()
    
    def on_button_press_event(self,obj,event):
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            if len(obj.selection) > 0:
                index = obj.selection[0]
                source = obj.get_row_data(index)
                EditSource.EditSource(source,self.db,self.update_display_after_edit)

    def on_add_source_clicked(self,obj):
        EditSource.EditSource(Source(),self.db,self.new_source_after_edit)

    def on_delete_source_clicked(self,obj):
        if len(obj.selection) == 0:
            return
        else:
            index = obj.selection[0]
            
        source = obj.get_row_data(index)

        if self.is_source_used(source):
            ans = EditSource.DelSrcQuery(source,self.db,self.update)

            QuestionDialog(_('Delete Source'),
                           _("This source is currently being used. Delete anyway?"),
                           _('Delete Source'),ans.query_response,
                           _('Keep Source'))
        else:
            map = self.db.getSourceMap()
            del map[source.getId()]
            Utils.modified()
            self.update(0)

    def is_source_used(self,source):
        for p in self.db.getPlaceMap().values():
            for sref in p.getSourceRefList():
                if sref.getBase() == source:
                    return 1
        for p in self.db.getPersonMap().values():
            for v in p.getEventList() + [p.getBirth(), p.getDeath()]:
                for sref in v.getSourceRefList():
                    if sref.getBase() == source:
                        return 1
            for v in p.getAttributeList():
                for sref in v.getSourceRefList():
                    if sref.getBase() == source:
                        return 1
            for v in p.getAlternateNames() + [p.getPrimaryName()]:
                for sref in v.getSourceRefList():
                    if sref.getBase() == source:
                        return 1
            for v in p.getAddressList():
                for sref in v.getSourceRefList():
                    if sref.getBase() == source:
                        return 1
        for p in self.db.getObjectMap().values():
            for sref in p.getSourceRefList():
                if sref.getBase() == source:
                    return 1
        for p in self.db.getFamilyMap().values():
            for v in p.getEventList():
                for sref in v.getSourceRefList():
                    if sref.getBase() == source:
                        return 1
            for v in p.getAttributeList():
                for sref in v.getSourceRefList():
                    if sref.getBase() == source:
                        return 1
        return 0

    def on_edit_source_clicked(self,obj):
        if len(obj.selection) > 0:
            index = obj.selection[0]
            source = obj.get_row_data(index)
            EditSource.EditSource(source,self.db,self.update_display_after_edit)

    def new_source_after_edit(self,source):
        self.db.addSource(source)
        self.update(0)

    def update_display_after_edit(self,place):
        self.update(0)

