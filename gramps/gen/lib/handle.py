#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013    Doug Blank <doug.blank@gmail.com>
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

class HandleClass(str):
    def __init__(self, handle):
        super(HandleClass, self).__init__()

    def join(self, database, handle):
        return database.get_table_func(self.classname,"handle_func")(handle)

    @classmethod
    def get_schema(cls):
        from gramps.gen.lib import (Person, Family, Event, Place, Source,
                                    Media, Repository, Note, Citation, Tag)
        tables = {
            "Person": Person,
            "Family": Family,
            "Event": Event,
            "Place": Place,
            "Source": Source,
            "Media": Media,
            "Repository": Repository,
            "Note": Note,
            "Citation": Citation,
            "Tag": Tag,
        }
        return tables[cls.classname].get_schema()

def Handle(_classname, handle):
    if handle is None:
        return None
    class MyHandleClass(HandleClass):
        """
        Class created to have classname attribute.
        """
        classname = _classname
    h = MyHandleClass(handle)
    return h

def __from_struct(struct):
    return struct
Handle.from_struct = __from_struct
