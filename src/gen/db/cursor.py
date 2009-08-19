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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import cPickle as pickle

#-------------------------------------------------------------------------
#
# GrampsCursor class
#
#-------------------------------------------------------------------------

class GrampsCursor(object):
    """
    Provide a basic iterator that allows the user to cycle through
    the elements in a particular map. 
    
    A cursor should never be directly instantiated. Instead, in should be 
    created by the database class.

    A cursor should only be used for a single pass through the
    database. If multiple passes are needed, multiple cursors
    should be used.
    """
    
    def __init__(self):
        """
        Instantiate the object. Note, this method should be overridden in
        derived classes that properly set self.cursor and self.source
        """
        self.cursor = self.source = None

    def __getattr__(self, name):
        """
        Return a method from the underlying cursor object, if it exists
        """
        return getattr(self.cursor, name)

    def __enter__(self):
        """
        Context manager enter method
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit method
        """
        self.close()
        return exc_type is None
        
    def __iter__(self):
        """
        Iterator
        """
        
        data = self.first()
        while data:
            yield data
            data = self.next()

    def first(self, *args, **kwargs):
        """
        Return the first (index, data) pair in the database. 
        
        This should be called before the first call to next(). Note that the 
        data return is in the format of the serialized format stored in the 
        database, not in the more usable class object. The data should be 
        converted to a class using the class's unserialize method.

        If no data is available, None is returned.
        """
        
        data = self.cursor.first(*args, **kwargs)
        if data:
            return (data[0], pickle.loads(data[1]))
        return None

    def next(self, *args, **kwargs):
        """
        Return the next (index, data) pair in the database. 
        
        Like the first() method, the data return is in the format of the 
        serialized format stored in the database, not in the more usable class 
        object. The data should be converted to a class using the class's 
        unserialize method.

        None is returned when no more data is available.
        """
        
        data = self.cursor.next(*args, **kwargs)
        if data:
            return (data[0], pickle.loads(data[1]))
        return None

    def prev(self, *args, **kwargs):
        """
        Return the previous (index, data) pair in the database. 
        
        Like the first() method, the data return is in the format of the 
        serialized format stored in the database, not in the more usable class 
        object. The data should be converted to a class using the class's 
        unserialize method.

        If no data is available, None is returned.
        """
        
        data = self.cursor.prev(*args, **kwargs)
        if data:
            return (data[0], pickle.loads(data[1]))
        return None

    def last(self, *args, **kwargs):
        """
        Return the last (index, data) pair in the database. 
        
        Like the first() method, the data return is in the format of the 
        serialized format stored in the database, not in the more usable class 
        object. The data should be converted to a class using the class's 
        unserialize method.

        None is returned when no more data is available.
        """
        
        data = self.cursor.last(*args, **kwargs)
        if data:
            return (data[0], pickle.loads(data[1]))
        return None
