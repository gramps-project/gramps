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
import GTK
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import GrampsCfg
import ListColors

class Sorter:
    def __init__(self, clist, column_map, key, top_window):
        self.clist = clist
        self.column_map = column_map
        self.key = key
        self.top_window = top_window
        (self.col,self.sort) = GrampsCfg.get_sort_cols(self.key,0,GTK.SORT_ASCENDING)
        self.change_sort(self.col,0)
        self.clist.connect('click-column',self.click)

    def sort_col(self):
        return self.col

    def sort_direction(self):
        return self.sort

    def click(self,obj,column):
        self.change_sort(column)

    def sort_list(self):
        self.clist.freeze()
        self.clist.sort()
        self.clist.sort()
        if ListColors.get_enable():
            try:
                loddbg = ListColors.oddbg
                loddfg = ListColors.oddfg
                levenbg = ListColors.evenbg
                levenfg = ListColors.evenfg

                cmap = self.top_window.get_colormap()
                oddbg = cmap.alloc(loddbg[0],loddbg[1],loddbg[2])
                oddfg = cmap.alloc(loddfg[0],loddfg[1],loddfg[2])
                evenbg = cmap.alloc(levenbg[0],levenbg[1],levenbg[2])
                evenfg = cmap.alloc(levenfg[0],levenfg[1],levenfg[2])
                rows = self.clist.rows
                for i in range(0,rows,2):
                    self.clist.set_background(i,oddbg)
                    self.clist.set_foreground(i,oddfg)
                    if i != rows:
                        self.clist.set_background(i+1,evenbg)
                        self.clist.set_foreground(i+1,evenfg)
            except OverflowError:
                pass
        self.clist.thaw()
        
    def change_sort(self,column,change=1):
        try:
            (sort_col,arrow) = self.column_map[column]
        except:
            return

        for (i,a) in self.column_map:
            if arrow != a:
                a.hide()
        arrow.show()

        if change:
            if self.col == column:
                if self.sort == GTK.SORT_DESCENDING:
                    self.sort = GTK.SORT_ASCENDING
                    arrow.set(GTK.ARROW_DOWN,2)
                else:
                    self.sort = GTK.SORT_DESCENDING
                    arrow.set(GTK.ARROW_UP,2)
            else:
                self.sort = GTK.SORT_ASCENDING
                arrow.set(GTK.ARROW_DOWN,2)

        self.clist.set_sort_column(sort_col)
        self.clist.set_sort_type(self.sort)

        self.sort_list()

        self.col = column

        if len(self.clist.selection) > 1:
            row = self.clist.selection[0]
            self.clist.moveto(row)

        GrampsCfg.save_sort_cols(self.key,self.col,self.sort)
        
class ChildSorter(Sorter):

    def change_sort(self,column,change=1):
        Sorter.change_sort(self,column,change)
        self.clist.set_reorderable(self.col == 0)
