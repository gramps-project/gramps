#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015 Gramps Development Team
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

from gramps.gen.lib.handle import HandleClass

class Struct(object):
    """
    Class for getting and setting parts of a struct by dotted path.

    >>> s = Struct({"gramps_id": "I0001", ...}, database)
    >>> s.primary_name.surname_list[0].surname
    Jones
    >>> s.primary_name.surname_list[0].surname = "Smith"
    >>> s.primary_name.surname_list[0]surname
    Smith
    """
    def __init__(self, struct, db=None):
        self.struct = struct
        self.db = db
        if self.db:
            self.transaction = db.get_transaction_class()
        else:
            self.transaction = None

    @classmethod
    def wrap(cls, instance, db=None):
        return Struct(instance.to_struct(), db)

    def __setitem__(self, item, value):
        self.struct[item] = value

    def __eq__(self, other):
        if isinstance(other, Struct):
            return self.struct == other.struct
        elif isinstance(self.struct, list):
            ## FIXME: self.struct can be a dict, list, etc
            for item in self.struct:
                if item == other:
                    return True
            return False
        else:
            return self.struct == other

    def __lt__(self, other):
        if isinstance(other, Struct):
            return self.struct < other.struct
        else:
            return self.struct < other

    def __gt__(self, other):
        if isinstance(other, Struct):
            return self.struct > other.struct
        else:
            return self.struct > other

    def __le__(self, other):
        if isinstance(other, Struct):
            return self.struct <= other.struct
        else:
            return self.struct <= other

    def __ge__(self, other):
        if isinstance(other, Struct):
            return self.struct >= other.struct
        else:
            return self.struct >= other

    def __ne__(self, other):
        if isinstance(other, Struct):
            return self.struct != other.struct
        else:
            return self.struct != other

    def __len__(self):
        return len(self.struct)

    def __contains__(self, item):
        return item in self.struct

    def __call__(self, *args, **kwargs):
        """
        You can use this to select and filter a list of structs.

        args are dotted strings of what componets of the structs to
        select, and kwargs is the selection criteria, double-under
        scores represent dots.

        If no args are given, all are provided.
        """
        selected = self.struct # better be dicts
        # First, find elements of the list that match any given
        # selection criteria:
        selected = self.struct # assume dicts
        # assume True
        to_delete = []
        for key in kwargs: # value="Social Security Number"
            parts = self.getitem_from_path(key.split("__")) # returns all
            # This will return a list; we keep the ones that match
            for p in range(len(parts)):
                # if it matches, keep it:
                if parts[p] != kwargs[key]:
                    to_delete.append(p)
        # delete from highest to lowest, to use pop:
        for p in reversed(to_delete):
            selected.pop(p)
        # now select which parts to show:
        if args: # just some of the parts, ["type.string", ...]
            results = []
            for select in selected: # dict in dicts
                parts = []
                for item in args: # ["type.string"]
                    items = item.split(".") # "type.string"
                    values = Struct(select, self.db).getitem_from_path(items)
                    if values:
                        parts.append((item, values))
                results.append(parts)  # return [["type.string", "Social Security Number"], ...]
        else: # return all
            results = selected
        # return them
        return results

    def select(self, thing1, thing2):
        if thing2 == "*":
            return thing1
        elif thing2 in thing1:
            return thing2
        elif thing1 == thing2:
            return thing1
        else:
            return None

    def __getattr__(self, attr):
        """
        Called when getattr fails. Lookup attr in struct; returns Struct
        if more struct.

        >>> Struct({}, db).primary_name
        returns: Struct([], db) or value

        struct can be list/tuple, dict with _class, or value (including dict).

        self.setitem_from_path(path, v) should be used to set value of
        item.
        """
        if isinstance(self.struct, dict) and "_class" in self.struct.keys():
            # this is representing an object
            if attr in self.struct.keys():
                return self.handle_join(self.struct[attr])
            else:
                raise AttributeError("attempt to access a property of an object: '%s', '%s'" % (self.struct, attr))
        elif isinstance(self.struct, HandleClass):
            struct = self.handle_join(self.struct)
            return getattr(struct, attr)
        elif isinstance(self.struct, (list, tuple)):
            # get first item in list that matches:
            sublist = [getattr(Struct(item, self.db), attr) for item in self.struct]
            return Struct(sublist, self.db)
        else:
            # better be a property of the list/tuple/dict/value:
            return getattr(self.struct, attr)

    def __getitem__(self, item):
        """
        Called when getitem fails. Lookup item in struct; returns Struct
        if more struct.

        >>> Struct({}, db)[12]
        returns: Struct([], db) or value

        struct can be list/tuple, dict with _class, or value (including dict).
        """
        if isinstance(item, str) and isinstance(self.struct, (list, tuple)):
            fields = [field.strip() for field in item.split(",")]
            results = []
            for item in self.struct:
                sublist = [getattr(Struct(item, self.db), field) for field in fields]
                if any(sublist):
                    results.append(tuple(sublist))
            return results if results else None
        else:
            return self.handle_join(self.struct[item])

    def getitem_from_path(self, items):
        """
        path is a list
        """
        current = self
        for item in items:
            current = getattr(current, item)
        return current

    def get_object_from_handle(self, handle):
        return self.db.get_from_name_and_handle(handle.classname, str(handle))

    def handle_join(self, item):
        """
        If the item is a handle, look up reference object.
        """
        if isinstance(item, HandleClass) and self.db:
            obj = self.get_object_from_handle(item)
            if obj:
                return Struct(obj.to_struct(), self.db)
            else:
                raise AttributeError("missing object: %s" % item)
        elif isinstance(item, (list, tuple)):
            return Struct(item, self.db)
        elif isinstance(item, dict) and "_class" in item.keys():
            return Struct(item, self.db)
        else:
            return item

    def setitem(self, path, value, trans=None):
        """
        Given a path to a struct part, set the last part to value.

        >>> Struct(struct).setitem("primary_name.surname_list.0.surname", "Smith")
        """
        return self.setitem_from_path(parse(path), value, trans)

    def primary_object_q(self, _class):
        return _class in ["Person", "Family", "Event", "Source", "Citation",
                          "Tag", "Repository", "Note", "Media"]

    def setitem_from_path(self, path, value, trans=None):
        """
        Given a path to a struct part, set the last part to value.

        >>> Struct(struct).setitem_from_path(["primary_name", "surname_list", "[0]", "surname"], "Smith", transaction)
        """
        path, item = path[:-1], path[-1]
        if item.startswith("["):
            item = item[1:-1]
        struct = self.struct
        primary_obj = struct
        for p in range(len(path)):
            part = path[p]
            if part.startswith("["): # getitem
                struct = struct[eval(part[1:-1])] # for int or string use
            else:                    # getattr
                struct = struct[part]
            if struct is None:       # invalid part to set, skip
                return
            if isinstance(struct, HandleClass):
                struct = self.get_object_from_handle(struct).to_struct()
            # keep track of primary object for update, below
            if isinstance(struct, dict) and "_class" in struct and self.primary_object_q(struct["_class"]):
                primary_obj = struct
        # struct is now set
        if item in struct and isinstance(struct[item], list): # assigning to a list
            if value is not None:
                struct[item].append(value)                    # we append the value
            else:
                struct[item] = []
        elif isinstance(struct, (list, tuple)):
            pos = int(item)
            if pos < len(struct):
                if value is not None:
                    struct[int(item)] = value
                else:
                    struct.pop(int(item))
        elif isinstance(struct, dict):
            if item in struct.keys():
                struct[item] = value
        elif hasattr(struct, item):
            setattr(struct, item, value)
        else:
            return
        self.update_db(primary_obj, trans)

    def update_db(self, struct, trans=None):
        if self.db:
            if trans is None:
                with self.transaction("Struct Update", self.db, batch=True) as trans:
                    new_obj = self.from_struct(struct)
                    name, handle = struct["_class"], struct["handle"]
                    old_obj = self.db.get_from_name_and_handle(name, handle)
                    if old_obj:
                        commit_func = self.db._tables[name]["commit_func"]
                        commit_func(new_obj, trans)
                    else:
                        add_func = self.db._tables[name]["add_func"]
                        add_func(new_obj, trans)
            else:
                new_obj = self.from_struct(struct)
                name, handle = struct["_class"], struct["handle"]
                old_obj = self.db.get_from_name_and_handle(name, handle)
                if old_obj:
                    commit_func = self.db._tables[name]["commit_func"]
                    commit_func(new_obj, trans)
                else:
                    add_func = self.db._tables[name]["add_func"]
                    add_func(new_obj, trans)

    def from_struct(self):
        """
        Given a struct with metadata, create a Gramps object.
        """
        from  gramps.gen.lib import (Person, Family, Event, Source, Place, Citation,
                                     Repository, MediaObject, Note, Tag, Date)
        struct = self.struct
        if isinstance(struct, dict):
            if "_class" in struct.keys():
                if struct["_class"] == "Person":
                    return Person.create(Person.from_struct(struct))
                elif struct["_class"] == "Family":
                    return Family.create(Family.from_struct(struct))
                elif struct["_class"] == "Event":
                    return Event.create(Event.from_struct(struct))
                elif struct["_class"] == "Source":
                    return Source.create(Source.from_struct(struct))
                elif struct["_class"] == "Place":
                    return Place.create(Place.from_struct(struct))
                elif struct["_class"] == "Citation":
                    return Citation.create(Citation.from_struct(struct))
                elif struct["_class"] == "Repository":
                    return Repository.create(Repository.from_struct(struct))
                elif struct["_class"] == "MediaObject":
                    return MediaObject.create(MediaObject.from_struct(struct))
                elif struct["_class"] == "Note":
                    return Note.create(Note.from_struct(struct))
                elif struct["_class"] == "Tag":
                    return Tag.create(Tag.from_struct(struct))
                elif struct["_class"] == "Date":
                    return Date().unserialize(Date.from_struct(struct, full=True))
        raise AttributeError("invalid struct: %s" % struct)

    def __str__(self):
        return str(self.struct)

    def __repr__(self):
        if "_class" in self.struct:
            return "<%s struct instance>" % self._class
        else:
            return repr(self.struct)
