#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

class GrampsCursor:
    """
    Provides a basic iterator that allows the user to cycle through
    the elements in a particular map. A cursor should never be
    directly instantiated. Instead, in should be created by the
    database class.

    A cursor should only be used for a single pass through the
    database. If multiple passes are needed, multiple cursors
    should be used.
    """

    def first(self):
        """
        Returns the first (index, data) pair in the database. This
        should be called before the first call to next(). Note that
        the data return is in the format of the serialized format
        stored in the database, not in the more usable class object.
        The data should be converted to a class using the class's
        unserialize method.

        If no data is available, None is returned.
        """
        return None

    def next(self):
        """
        Returns the next (index, data) pair in the database. Like
        the first() method, the data return is in the format of the
        serialized format stored in the database, not in the more
        usable class object. The data should be converted to a class
        using the class's unserialize method.

        None is returned when no more data is available.
        """
        return None

    def close(self):
        """
        Closes the cursor. This should be called when the user is
        finished using the cursor, freeing up the cursor's resources.
        """
        raise NotImplementedError
    
    def get_length(self):
        """
        Returns the number of records in the table referenced by the
        cursor
        """
        raise NotImplementedError

