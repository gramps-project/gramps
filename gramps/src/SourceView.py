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
import Sorter

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

        arrow_map = [(3, glade.get_widget("title_arrow")),
                     (1, glade.get_widget("src_id_arrow")),
                     (4, glade.get_widget("author_arrow"))]
        self.source_list = glade.get_widget("source_list")
        self.source_list.set_column_visibility(3,0)
        self.source_list.set_column_visibility(4,0)
        self.source_sort = Sorter.Sorter(self.source_list,arrow_map,'source')

    def change_db(self,db):
        self.db = db

    def moveto(self,row):
        self.source_list.unselect_all()
        self.source_list.select_row(row,0)
        self.source_list.moveto(row)
        
    def load_sources(self):

        if len(self.source_list.selection) > 0:
            current_row = self.source_list.selection[0]
        else:
            current_row = 0

        self.source_list.clear()
        self.source_list.freeze()
        self.source_list.set_column_visibility(1,GrampsCfg.id_visible)

        index = 0
        for key in self.db.getSourceKeys():
            self.source_list.append(self.db.getSourceDisplay(key))
            self.source_list.set_row_data(index,key)
            index = index + 1

        if index > 0:
            self.source_list.select_row(current_row,0)
            self.source_list.moveto(current_row)

        self.source_sort.sort_list()
        self.source_list.thaw()
    
    def button_press(self,obj,event):
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            if len(obj.selection) > 0:
                index = obj.selection[0]
                source = self.db.getSourceMap()[obj.get_row_data(index)]
                EditSource.EditSource(source,self.db,
                                      self.update_display_after_edit)

    def on_add_source_clicked(self,obj):
        EditSource.EditSource(Source(),self.db,self.new_source_after_edit)

    def on_delete_clicked(self,obj):
        if len(obj.selection) == 0:
            return
        else:
            index = obj.selection[0]
            
        source = self.db.getSourceMap()[obj.get_row_data(index)]

        if self.is_source_used(source):
            ans = EditSource.DelSrcQuery(source,self.db,self.update)

            QuestionDialog(_('Delete Source'),
                           _("This source is currently being used. Delete anyway?"),
                           _('Delete Source'),ans.query_response,
                           _('Keep Source'))
        else:
            self.db.removeSource(source.getId())
            Utils.modified()
            self.update(0)

    def is_source_used(self,source):
        for key in self.db.getPlaceKeys():
            p = self.db.getPlace(key)
            for sref in p.getSourceRefList():
                if sref.getBase() == source:
                    return 1
        for key in self.db.getPersonKeys():
            p = self.db.getPerson(key)
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
            source = self.db.getSourceMap()[obj.get_row_data(index)]
            EditSource.EditSource(source,self.db,
                                  self.update_display_after_edit)

    def new_source_after_edit(self,source):
        self.db.addSource(source)
        self.update(0)

    def update_display_after_edit(self,place):
        self.db.buildSourceDisplay(place.getId())
        self.update(0)

