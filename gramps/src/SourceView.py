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

import GTK
import GDK
import gnome.ui
import gtk
import string

from RelLib import *
import intl
import EditSource
import utils

_ = intl.gettext

class SourceView:
    def __init__(self,db,source_list,update):
        self.source_list = source_list
        self.db = db
        self.update = update

    def load_sources(self):
        self.source_list.clear()
        self.source_list.freeze()

        if len(self.source_list.selection) > 0:
            current_row = self.source_list.selection[0]
        else:
            current_row = 0

        index = 0
        for src in self.db.getSourceMap().values():
            self.source_list.append([src.getTitle(),src.getAuthor()])
            self.source_list.set_row_data(index,src)
            index = index + 1

        if index > 0:
            self.source_list.select_row(current_row,0)
            self.source_list.moveto(current_row)

        self.source_list.thaw()
    
    def on_button_press_event(self,obj,event):
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            if len(obj.selection) > 0:
                index = obj.selection[0]
                source = obj.get_row_data(index)
                EditSource.EditSource(source,self.db,update_display_after_edit)

    def on_add_source_clicked(self,obj):
        EditSource.EditSource(Source(),self.db,self.new_source_after_edit)

    def on_delete_source_clicked(self,obj):
        import EditSource
    
        if len(obj.selection) == 0:
            return
        else:
            index = obj.selection[0]
            
        source = obj.get_row_data(index)

        if self.is_source_used(source):
            msg = _("This source is currently being used. Delete anyway?")
            ans = EditSource.DelSrcQuery(source,database,update_display)
            GnomeQuestionDialog(msg,ans.query_response)
        else:
            map = self.db.getSourceMap()
            del map[source.getId()]
            utils.modified()
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

