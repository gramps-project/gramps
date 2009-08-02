#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Doug Blank <doug.blank@gmail.com>
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

# $Id$

import pickle
import socket
import sys

from gen.lib import *

class RemoteObject:
    """
    A wrapper to access underlying attributes by asking over a 
    socket. A server will pickle the result, and return.
    """
    def __init__(self, host, port, prefix = "self."):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.settimeout(5) # 5 second timeout
        self.prefix = prefix
    
    def __repr__(self):
        return self.remote("repr(self)")
    
    def person(self, handle):
        data = self.remote("self.dbstate.db.get_raw_person_data(%s)" % repr(handle))
        return Person(data)

    def family(self, handle):
        data = self.remote("self.dbstate.db.get_raw_family_data(%s)" % repr(handle))
        return Family(data)

    def object(self, handle):
        data = self.remote("self.dbstate.db.get_raw_object_data(%s)" % repr(handle))
        return MediaObject(data)

    def place(self, handle):
        data = self.remote("self.dbstate.db.get_raw_place_data(%s)" % repr(handle))
        return Place(data)

    def event(self, handle):
        data = self.remote("self.dbstate.db.get_raw_event_data(%s)" % repr(handle))
        return Event(data)

    def source(self, handle):
        data = self.remote("self.dbstate.db.get_raw_source_data(%s)" % repr(handle))
        return Source(data)

    def repository(self, handle):
        data = self.remote("self.dbstate.db.get_raw_repository_data(%s)" % repr(handle))
        return Repository(data)

    def note(self, handle):
        data = self.remote("self.dbstate.db.get_raw_note_data(%s)" % repr(handle))
        return Note(data)

    def remote(self, command):
        """
        Use this interface to directly talk to server.
        """
        retval = None
        self.socket.send(command)
        data = self.socket.recv(1024)
        if data != "":
            while True:
                try:
                    retval = pickle.loads(data)
                    break
                except:
                    data += self.socket.recv(1024)
        if isinstance(retval, Exception):
            raise retval
        return retval

    def _eval(self, item, *args, **kwargs):
        """
        The interface for calling prefix.item.item...(args, kwargs)
        """
        commandArgs = ""
        for a in args:
            if commandArgs != "":
                commandArgs += ", "
            commandArgs += repr(a)
        for a in kwargs.keys():
            if commandArgs != "":
                commandArgs += ", "
            commandArgs += a + "=" + repr(kwargs[a])
        self.socket.send(self.prefix + item + "(" + commandArgs + ")")
        retval = None
        data = self.socket.recv(1024)
        if data != "":
            while True:
                try:
                    retval =  pickle.loads(data)
                    break
                except:
                    data += self.socket.recv(1024)
        return retval

    def representation(self, item):
        return self.remote("repr(%s)" % (self.prefix + item))

    def __getattr__(self, item):
        return TempRemoteObject(self, item)

    def dir(self, item = ''):
        return self.remote("dir(%s)" % ((self.prefix + item)[:-1]))

class TempRemoteObject:
    """
    Temporary field/method access object.
    """
    def __init__(self, parent, item):
        self.parent = parent
        self.item = item
    def __call__(self, *args, **kwargs):
        return self.parent._eval(self.item, *args, **kwargs)
    def _eval(self, prefix, *args, **kwargs):
        return self.parent._eval(self.item + "." + prefix, *args, **kwargs)
    def __repr__(self):
        return self.parent.representation(self.item)
    def representation(self, item):
        return self.parent.representation(self.item + "." + item)
    def __getattr__(self, item):
        return TempRemoteObject(self, item)
    def dir(self, item = ''):
        return self.parent.dir(self.item + "." + item)

if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    self = RemoteObject(host, port)
    print "GRAMPS Remote interface; use 'self' to access GRAMPS"
