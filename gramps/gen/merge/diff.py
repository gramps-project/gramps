#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
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

"""
This package implements an object difference engine.
"""

import os

from gramps.cli.user import User
from ..dbstate import DbState
from gramps.cli.grampscli import CLIManager
from ..plug import BasePluginManager
from gramps.plugins.database.dictionarydb import DictionaryDb
from gramps.gen.lib.handle import HandleClass, Handle
from gramps.gen.lib import *
from gramps.gen.lib.personref import PersonRef
from gramps.gen.lib.eventref import EventRef
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

def get_schema(cls):
    """
    Given a gramps.gen.lib class, or class name, return a dictionary
    containing the schema. The schema is a dictionary of fieldname
    keys with type as value.

    Also, the schema includes the same metadata fields as does struct,
    including "_class", returned as real class of cls.
    """
    orig_cls = cls
    # Get type as a gramps.gen.lib string name
    if isinstance(cls, type):
        cls = cls().__class__.__name__
    elif isinstance(cls, object) and not isinstance(cls, str):
        cls = cls.__class__.__name__
    ### Is there a Path?
    if "." in cls:
        items = parse(cls) # "Person.alternate_names"
        cls, path = items[0], items[1:]
    else:
        path = []
    # Now get the schema
    if cls in ("str", "int", "bool", "float", "long", "list"):
        schema = orig_cls
    elif cls == "Person":
        schema = {
            "_class": Person,
            "handle":  Handle("Person", "PERSON-HANDLE"),
            "gramps_id": str,
            "gender": int,
            "primary_name": Name,
            "alternate_names": [Name],
            "death_ref_index": int,
            "birth_ref_index": int,
            "event_ref_list": [EventRef],
            "family_list": [Handle("Family", "FAMILY-HANDLE")],
            "parent_family_list": [Handle("Family", "FAMILY-HANDLE")],
            "media_list": [MediaRef],
            "address_list": [Address],
            "attribute_list": [Attribute],
            "urls": [Url],
            "lds_ord_list": [LdsOrd],
            "citation_list": [Handle("Citation", "CITATION-HANDLE")],
            "note_list": [Handle("Note", "NOTE-HANDLE")],
            "change": int,
            "tag_list": [Handle("Tag", "TAG-HANDLE")],
            "private": bool,
            "person_ref_list": [PersonRef]
        }
    elif cls == "Name":
        schema = {
            "_class": Name,
            "private": bool,
            "citation_list": [Handle("Citation", "CITATION-HANDLE")],
            "note_list": [Handle("Note", "NOTE-HANDLE")],
            "date": Date,
            "first_name": str,
            "surname_list": [Surname],
            "suffix": str,
            "title": str,
            "type": NameType,
            "group_as": str,
            "sort_as": int,
            "display_as": int,
            "call": str,
            "nick": str,
            "famnick": str,
        }
    else:
        raise AttributeError("unknown class '%s'" % cls)
    # walk down path, if given:
    for p in range(len(path)):
        # could be a list
        item = path[p]
        if isinstance(schema, (list, tuple)):
            schema = schema[int(item)]
        else:
            schema = schema[item]
        if isinstance(schema, type):
            schema = get_schema(schema)
    return schema

def parse(string):
    """
    Break a string up into a struct-path. Used by get_schema() and setitem().

    >>> parse("primary_name.first_name.startswith('Sarah')")
    ["primary_name", "first_name", "startswith", "('Sarah')"]
    >>> parse("primary_name.surname_list[0].surname.startswith('Smith')")
    ["primary_name", "surname_list", "[0]", "surname", "startswith", "('Smith')"]
    """
    # FIXME: handle nested same-structures, (len(list) + 1)
    retval = []
    stack = []
    current = ""
    for p in range(len(string)):
        c = string[p]
        if c == "]":
            if stack and stack[-1] == "[": # end
                stack.pop(-1)
            current += c
            retval.append(current)
            current = ""
        elif c == "[":
            stack.append(c)
            retval.append(current)
            current = ""
            current += c
        elif c in ["'", '"']:
            if stack and stack[-1] == c: # end
                stack.pop(-1)
                current += c
                if stack and stack[-1] in ["'", '"', '[']: # in quote or args
                    pass
                else:
                    current += c
                    retval.append(current)
                    current = ""
            else:                        # start
                stack.append(c)
                current += c
        elif c == ".":
            retval.append(current)
            current = ""
        elif stack and stack[-1] in ["'", '"', '[']: # in quote or args
            current += c
        else:
            current += c
    if current:
        retval.append(current)
    return retval

def import_as_dict(filename, user=None):
    """
    Import the filename into a DictionaryDb and return it.
    """
    if user is None:
        user = User()
    db = DictionaryDb()
    db.load(None)
    db.set_feature("skip-import-additions", True)
    dbstate = DbState()
    climanager = CLIManager(dbstate, setloader=False, user=user)
    climanager.do_reg_plugins(dbstate, None)
    pmgr = BasePluginManager.get_instance()
    (name, ext) = os.path.splitext(os.path.basename(filename))
    format = ext[1:].lower()
    import_list = pmgr.get_reg_importers()
    for pdata in import_list:
        if format == pdata.extension:
            mod = pmgr.load_plugin(pdata)
            if not mod:
                for item in pmgr.get_fail_list():
                    name, error_tuple, pdata = item
                    # (filename, (exception-type, exception, traceback), pdata)
                    etype, exception, traceback = error_tuple
                    #print("ERROR:", name, exception)
                return False
            import_function = getattr(mod, pdata.import_function)
            results = import_function(db, filename, user)
            if results is None:
                return None
            return db
    return None

def diff_dates(json1, json2):
    """
    Compare two json date objects. Returns True if different.
    """
    if json1 == json2: # if same, then Not Different
        return False   # else, they still might be Not Different
    elif isinstance(json1, dict) and isinstance(json2, dict):
        if json1["dateval"] == json2["dateval"] and json2["dateval"] != 0:
            return False
        elif json1["text"] == json2["text"]:
            return False
        else:
            return True
    else:
        return True

def diff_items(path, json1, json2):
    """
    Compare two json objects. Returns True if different.
    """
    if json1 == json2:
        return False
    elif isinstance(json1, list) and isinstance(json2, list):
        if len(json1) != len(json2):
            return True
        else:
            pos = 0
            for v1, v2 in zip(json1, json2):
                result = diff_items(path + ("[%d]" % pos), v1, v2)
                if result:
                    return True
                pos += 1
            return False
    elif isinstance(json1, dict) and isinstance(json2, dict):
        for key in json1.keys():
            if key == "change":
                continue # don't care about time differences, only data changes
            elif key == "date":
                result = diff_dates(json1["date"], json2["date"])
                if result:
                    #print("different dates", path)
                    #print("   old:", json1["date"])
                    #print("   new:", json2["date"])
                    return True
            else:
                result = diff_items(path + "." + key, json1[key], json2[key])
                if result:
                    return True
        return False
    else:
        #print("different values", path)
        #print("   old:", json1)
        #print("   new:", json2)
        return True

def diff_dbs(db1, db2, user=None):
    """
    1. new objects => mark for insert
    2. deleted objects, no change locally after delete date => mark
       for deletion
    3. deleted objects, change locally => mark for user confirm for
       deletion
    4. updated objects => do a diff on differences, mark origin
       values as new data
    """
    if user is None:
        user = User()
    missing_from_old = []
    missing_from_new = []
    diffs = []
    with user.progress(_('Family Tree Differences'),
            _('Searching...'), 10) as step:
        for item in ['Person', 'Family', 'Source', 'Citation', 'Event', 'Media',
                     'Place', 'Repository', 'Note', 'Tag']:
            step()
            handles1 = sorted([handle.decode('utf-8') for handle in db1._tables[item]["handles_func"]()])
            handles2 = sorted([handle.decode('utf-8') for handle in db2._tables[item]["handles_func"]()])
            p1 = 0
            p2 = 0
            while p1 < len(handles1) and p2 < len(handles2):
                if handles1[p1] == handles2[p2]: # in both
                    item1 = db1._tables[item]["handle_func"](handles1[p1])
                    item2 = db2._tables[item]["handle_func"](handles2[p2])
                    diff = diff_items(item, item1.to_struct(), item2.to_struct())
                    if diff:
                        diffs += [(item, item1, item2)]
                    # else same!
                    p1 += 1
                    p2 += 1
                elif handles1[p1] < handles2[p2]: # p1 is mssing in p2
                    item1 = db1._tables[item]["handle_func"](handles1[p1])
                    missing_from_new += [(item, item1)]
                    p1 += 1
                elif handles1[p1] > handles2[p2]: # p2 is mssing in p1
                    item2 = db2._tables[item]["handle_func"](handles2[p2])
                    missing_from_old += [(item, item2)]
                    p2 += 1
            while p1 < len(handles1):
                item1 = db1._tables[item]["handle_func"](handles1[p1])
                missing_from_new += [(item, item1)]
                p1 += 1
            while p2 < len(handles2):
                item2 = db2._tables[item]["handle_func"](handles2[p2])
                missing_from_old += [(item, item2)]
                p2 += 1
    return diffs, missing_from_old, missing_from_new

def diff_db_to_file(old_db, filename, user=None):
    if user is None:
        user = User()
    # First, get data as a DictionaryDb
    new_db = import_as_dict(filename, user, user)
    if new_db is not None:
        # Next get differences:
        diffs, m_old, m_new = diff_dbs(old_db, new_db, user)
        return diffs, m_old, m_new

def from_struct(struct):
    """
    Given a struct with metadata, create a Gramps object.
    """
    from  gramps.gen.lib import (Person, Family, Event, Source, Place, Citation,
                                 Repository, MediaObject, Note, Tag)
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
    raise AttributeError("invalid struct: %s" % struct)

def get_dependencies(struct):
    """
    Walk the struct recursively, getting all dependencies on other
    objects.
    """
    if isinstance(struct, HandleClass):
        return set([(struct.classname, str(struct))])
    elif isinstance(struct, (tuple, list)):
        retval = set([])
        for item in struct:
            retval.update(get_dependencies(item))
        return retval
    elif isinstance(struct, dict):
        retval = set([])
        for key in struct.keys():
            retval.update(get_dependencies(struct[key]))
        return retval
    else:
        return set([])

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
                    new_obj = from_struct(struct)
                    name, handle = struct["_class"], struct["handle"]
                    old_obj = self.db.get_from_name_and_handle(name, handle)
                    if old_obj:
                        commit_func = self.db._tables[name]["commit_func"]
                        commit_func(new_obj, trans)
                    else:
                        add_func = self.db._tables[name]["add_func"]
                        add_func(new_obj, trans)
            else:
                new_obj = from_struct(struct)
                name, handle = struct["_class"], struct["handle"]
                old_obj = self.db.get_from_name_and_handle(name, handle)
                if old_obj:
                    commit_func = self.db._tables[name]["commit_func"]
                    commit_func(new_obj, trans)
                else:
                    add_func = self.db._tables[name]["add_func"]
                    add_func(new_obj, trans)

    def __str__(self):
        return str(self.struct)

