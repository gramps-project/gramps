#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002  Donald N. Allingham
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

"""
Provides a sorting interface to GtkCList widgets.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import GTK

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import GrampsCfg

class Sorter:

    """Provides a sorting interface to a GtkCList. Instead of
    providing a sorting function, the table should be built with ASCII
    sorting information loaded into the table. If the sorting data
    should not be visible, the column should be hidden.
    
    Each column should have a column header that contains a
    GtkArrow. The Sorter class with alter the GtkArrow based off
    whether the column is sorted in ascending or descending order."""
    
    def __init__(self, clist, column_map, key):
        """
        Creates a sorter instance associated with the GtkCList.

        clist      - GtkCList with which the Sorter is associated
        column_map - A list of tuples that assocates a column with its
                     sort column and the GtkArrow that should be altered
                     with the column.
        key        - text key used for storing the sort column and
                     direction in the configuration database.
        """
        self.clist = clist
        self.column_map = column_map
        self.key = key
        (self.col,self.sort) = GrampsCfg.get_sort_cols(self.key,0,GTK.SORT_ASCENDING)
        self.change_sort(self.col,0)
        self.clist.connect('click-column',self.click)

    def sort_col(self):
        """Returns the current column that is being sorted (not the acutal sort
        column, but the user visable column"""
        return self.col

    def sort_direction(self):
        """Returns the current sort direction, either GTK.SORT_ASCENDING or
        GTK.SORT_DESCENDING"""
        return self.sort

    def click(self,obj,column):
        """Callback function that is associated with the GtkCList, changing the
        sort column"""
        self.change_sort(column)

    def sort_list(self):
        """
        Sorts the GtkCList. If list colors have been enabled, set the foreground and
        background colors of each row. 
        """
        self.clist.freeze()
        self.clist.sort()
        self.clist.sort()
        if _enable:
            try:
                cmap = self.clist.get_colormap()
                loddbg  = cmap.alloc(to_signed(oddbg[0]),to_signed(oddbg[1]),
                                     to_signed(oddbg[2]))
                loddfg  = cmap.alloc(to_signed(oddfg[0]),to_signed(oddfg[1]),
                                     to_signed(oddfg[2]))
                levenbg = cmap.alloc(to_signed(evenbg[0]),to_signed(evenbg[1]),
                                     to_signed(evenbg[2]))
                levenfg = cmap.alloc(to_signed(evenfg[0]),to_signed(evenfg[1]),
                                     to_signed(evenfg[2]))
                rows = self.clist.rows
                for i in range(0,rows,2):
                    self.clist.set_background(i,loddbg)
                    self.clist.set_foreground(i,loddfg)
                    if i != rows:
                        self.clist.set_background(i+1,levenbg)
                        self.clist.set_foreground(i+1,levenfg)
            except OverflowError:
                pass
        self.clist.thaw()
        
    def change_sort(self,column,change=1):
        """
        Changes the sort column of the GtkList if the requested column
        is in the column map. If the column has changed, the sort direction
        is set to ascending, if the column has not changed, the sort direction
        is changed to the opposite sort direction

        column - visible column that should be sorted
        change - don't alter the direction
        """
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
    """
    Derived from the basic Sorter class to allow the GtkList to be
    manually reorderable by the user.
    """
    
    def change_sort(self,column,change=1):
        """
        If the column is the 0, set the list as reorderable.
        """
        Sorter.change_sort(self,column,change)
        self.clist.set_reorderable(self.col == 0)


#-------------------------------------------------------------------------
#
# Color management
#
#-------------------------------------------------------------------------
_enable   = 0
oddbg    = (0xffff,0xffff,0xffff)
evenbg   = (0xffff,0xffff,0xffff)
oddfg    = (0,0,0)
evenfg   = (0,0,0)
ancestorfg = (0,0,0)

def to_signed(a):
    if a & 0x8000:
        return a - 0x10000
    else:
        return a

def set_enable(val):
    global _enable
    _enable = val

def get_enable():
    return _enable
