#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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


from _Constants import ObjectTypes

class ObjectSelectorResult(object):

    def __init__(self):
        self._gramps_id = None
        self._object_type = None

    def __str__(self):
        return "Object Type = %s\n"\
               "Gramps ID = %s" % (str(self._object_type),
                                   str(self._gramps_id))    
        
    def set_gramps_id(self,id):
        self._gramps_id = id

    def get_gramps_id(self):
        return self._gramps_id

    def set_object_type(self,object_type):
        self._object_type = object_type

    def get_object_type(self,object_type):
        return self._object_type

    def is_person(self):
        return self._object_type == ObjectTypes.PERSON

    def is_family(self):
        return self._object_type == ObjectTypes.FAMILY
    
    def is_event(self):
        return self._object_type == ObjectTypes.EVENT
    
    def is_source(self):
        return self._object_type == ObjectTypes.SOURCE
    
    def is_repository(self):
        return self._object_type == ObjectTypes.REPOSITORY
    
    def is_media(self):
        return self._object_type == ObjectTypes.MEDIA

    def is_place(self):
        return self._object_type == ObjectTypes.PLACE
