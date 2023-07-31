#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2002       Gary Shao
# Copyright (C) 2007       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2009       Gary Burton
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# -------------------------------------------------------------------------
#
# standard python modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# set up logging
#
# -------------------------------------------------------------------------
import logging

log = logging.getLogger(".tablestyle")


# ------------------------------------------------------------------------
#
# TableStyle
#
# ------------------------------------------------------------------------
class TableStyle:
    """
    Specifies the style or format of a table. The TableStyle contains the
    characteristics of table width (in percentage of the full width), the
    number of columns, and the width of each column as a percentage of the
    width of the table.
    """

    def __init__(self, obj=None):
        """
        Create a new TableStyle object, with the values initialized to
        empty, with allocating space for up to 100 columns.

        :param obj: if not None, then the object created gets is attributes
                    from the passed object instead of being initialized to
                    empty.
        """
        if obj:
            self.width = obj.width
            self.columns = obj.columns
            self.colwid = obj.colwid[:]
            self.description = obj.description
        else:
            self.width = 0
            self.columns = 0
            self.colwid = [0] * 100
            self.description = ""

    def set_description(self, text):
        """
        Set the description of the table object
        """
        self.description = text

    def get_description(self):
        """
        Return the description of the table object
        """
        return self.description

    def set_width(self, width):
        """
        Set the width of the table in terms of percent of the available
        width
        """
        self.width = width

    def get_width(self):
        """
        Return the specified width as a percentage of the available space
        """
        return self.width

    def set_columns(self, columns):
        """
        Set the number of columns.

        :param columns: number of columns that should be used.
        """
        self.columns = columns

    def get_columns(self):
        """
        Return the number of columns
        """
        return self.columns

    def set_column_widths(self, clist):
        """
        Set the width of all the columns at once, taking the percentages
        from the passed list.
        """
        self.columns = len(clist)
        for i in range(self.columns):
            self.colwid[i] = clist[i]

    def set_column_width(self, index, width):
        """
        Set the width of a specified column to the specified width.

        :param index: column being set (index starts at 0)
        :param width: percentage of the table width assigned to the column
        """
        self.colwid[index] = width

    def get_column_width(self, index):
        """
        Return the column width of the specified column as a percentage of
        the entire table width.

        :param index: column to return (index starts at 0)
        """
        return self.colwid[index]


# ------------------------------------------------------------------------
#
# TableCellStyle
#
# ------------------------------------------------------------------------
class TableCellStyle:
    """
    Defines the style of a particular table cell. Characteristics are:
    right border, left border, top border, bottom border, and padding.
    """

    def __init__(self, obj=None):
        """
        Create a new TableCellStyle instance.

        :param obj: if not None, specifies that the values should be
                    copied from the passed object instead of being initialized
                    to empty.
        """
        if obj:
            self.rborder = obj.rborder
            self.lborder = obj.lborder
            self.tborder = obj.tborder
            self.bborder = obj.bborder
            self.padding = obj.padding
            self.longlist = obj.longlist
            self.description = obj.description
        else:
            self.rborder = 0
            self.lborder = 0
            self.tborder = 0
            self.bborder = 0
            self.padding = 0
            self.longlist = 0
            self.description = ""

    def set_description(self, text):
        """
        Set the description of the table cell object
        """
        self.description = text

    def get_description(self):
        """
        Return the description of the table cell object
        """
        return self.description

    def set_padding(self, val):
        "Return the cell padding in centimeters"
        self.padding = val

    def set_borders(self, val):
        """
        Defines if a border is used

        :param val: if True, a border is used, if False, it is not
        """
        self.rborder = val
        self.lborder = val
        self.tborder = val
        self.bborder = val

    def set_right_border(self, val):
        """
        Defines if a right border in used

        :param val: if True, a right border is used, if False, it is not
        """
        self.rborder = val

    def set_left_border(self, val):
        """
        Defines if a left border in used

        :param val: if True, a left border is used, if False, it is not
        """
        self.lborder = val

    def set_top_border(self, val):
        """
        Defines if a top border in used

        :param val: if True, a top border is used, if False, it is not
        """
        self.tborder = val

    def set_bottom_border(self, val):
        """
        Defines if a bottom border in used

        :param val: if 1, a bottom border is used, if 0, it is not
        """
        self.bborder = val

    def set_longlist(self, val):
        self.longlist = val

    def get_padding(self):
        "Return the cell padding in centimeters"
        return self.padding

    def get_right_border(self):
        "Return 1 if a right border is requested"
        return self.rborder

    def get_left_border(self):
        "Return 1 if a left border is requested"
        return self.lborder

    def get_top_border(self):
        "Return 1 if a top border is requested"
        return self.tborder

    def get_bottom_border(self):
        "Return 1 if a bottom border is requested"
        return self.bborder

    def get_longlist(self):
        return self.longlist
