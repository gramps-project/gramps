#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007 Richard Taylor
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

# $Id:iterator.py 9912 2008-01-22 09:17:46Z acraphae $

from gen.utils import LongOpStatus

class CursorIterator(object):
    
    def __init__(self, db, cursor, msg=""):
        self._db = db
        self._cursor = cursor
        self._status = LongOpStatus(total_steps=cursor.get_length(), 
                                    interval=10)
        #self._status = LongOpStatus(msg=msg)

    def __iter__(self):
        try:
            # Emit start signal
            self._db.emit('long-op-start', (self._status,))
            
            first = self._cursor.first()
            if first: 
                yield first
            
            next = self._cursor.next()
            while next:
                yield next
            
                # check for cancel
                #if self._status.should_cancel():
                #    raise DbUserCancel
            
                # emit heartbeat
                self._status.heartbeat()
                next = self._cursor.next()
            
            # emit stop signal
            self._status.end()
            self._cursor.close()
            raise StopIteration
        except:
            # Not allowed to use 'finally' because we 
            # yeild inside the try clause.
            self._cursor.close()
            self._status.end()
            raise
    
