#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010      Nick Hall
# Copyright (C) 2013      Doug Blank <doug.blank@gmail.com>
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
Table Object class for Gramps.
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import time

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .baseobj import BaseObject

#-------------------------------------------------------------------------
#
# Localized constants
#
#-------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
CODESET = glocale.encoding
#-------------------------------------------------------------------------
#
# Table Object class
#
#-------------------------------------------------------------------------
class TableObject(BaseObject):
    """
    The TableObject is the base class for all objects that are stored in a
    seperate database table.  Each object has a database handle and a last
    changed time.  The database handle is used as the unique key for a record
    in the database.  This is not the same as the Gramps ID, which is a user
    visible identifier for a record.

    It is the base class for the BasicPrimaryObject class and Tag class.
    """

    def __init__(self, source=None):
        """
        Initialize a TableObject.

        If source is None, the handle is assigned as an empty string.
        If source is not None, then the handle is initialized from the value in
        the source object.

        :param source: Object used to initialize the new object
        :type source: TableObject
        """
        if source:
            self.handle = source.handle
            self.change = source.change
        else:
            self.handle = None
            self.change = 0

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        raise NotImplementedError

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        raise NotImplementedError

    def to_struct(self):
        """
        Convert the data held in this object to a structure (eg,
        struct) that represents all the data elements.

        This method is used to recursively convert the object into a
        self-documenting form that can easily be used for various
        purposes, including diffs and queries.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns a struct containing the data of the object.
        """
        raise NotImplementedError

    def from_struct(self, struct):
        """
        Given a struct data representation, return an object of this type.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns an object of this type.
        """
        raise NotImplementedError

    def get_change_time(self):
        """
        Return the time that the data was last changed.

        The value in the format returned by the :meth:`time.time()` command.

        :returns: Time that the data was last changed. The value in the format
                  returned by the :meth:`time.time()` command.
        :rtype: int
        """
        return self.change

    def set_change_time(self, change):
        """
        Modify the time that the data was last changed.

        The value must be in the format returned by the :meth:`time.time()`
        command.

        :param change: new time
        :type change: int in format as :meth:`time.time()` command
        """
        self.change = change

    def get_change_display(self):
        """
        Return the string representation of the last change time.

        :returns: string representation of the last change time.
        :rtype: str

        """
        if self.change:
            return str(time.strftime('%x %X', time.localtime(self.change)),
                       CODESET)
        else:
            return ''

    def set_handle(self, handle):
        """
        Set the database handle for the primary object.

        :param handle: object database handle
        :type handle: str
        """
        self.handle = handle

    def get_handle(self):
        """
        Return the database handle for the primary object.

        :returns: database handle associated with the object
        :rtype: str
        """
        return self.handle

    @classmethod
    def get_labels(cls, _):
        """
        Return labels.
        """
        return {}

    @classmethod
    def field_aliases(cls):
        """
        Return dictionary of alias to full field names
        for this object class.
        """
        return {}

    @classmethod
    def get_field_alias(cls, alias):
        """
        Return full field name for an alias, if one.
        """
        return cls.field_aliases().get(alias, alias)

    @classmethod
    def get_schema(cls):
        """
        Return schema.
        """
        return {}

    @classmethod
    def get_extra_secondary_fields(cls):
        """
        Return a list of full field names and types for secondary
        fields that are not directly listed in the schema.
        """
        return []

    @classmethod
    def get_index_fields(cls):
        """
        Return a list of full field names for indices.
        """
        return []

    @classmethod
    def get_secondary_fields(cls):
        """
        Return all seconday fields and their types
        """
        from .handle import HandleClass
        return ([(key.lower(), value)
                 for (key, value) in cls.get_schema().items()
                 if value in [str, int, float, bool] or
                 isinstance(value, HandleClass)] +
                cls.get_extra_secondary_fields())

    @classmethod
    def get_label(cls, field, _):
        """
        Get the associated label given a field name of this object.
        No index positions allowed on lists.
        """
        chain = field.split(".")
        path = cls._follow_schema_path(chain[:-1])
        labels = path.get_labels(_)
        if chain[-1] in labels:
            return labels[chain[-1]]
        else:
            raise Exception("%s has no such label on %s: '%s'" %
                            (cls, path, field))

    @classmethod
    def get_field_type(cls, field):
        """
        Get the associated label given a field name of this object.
        No index positions allowed on lists.
        """
        field = cls.get_field_alias(field)
        chain = field.split(".")
        ftype = cls._follow_schema_path(chain)
        return ftype

    @classmethod
    def _follow_schema_path(cls, chain):
        """
        Follow a list of schema items. Return endpoint.
        """
        path = cls
        for part in chain:
            schema = path.get_schema()
            if part.isdigit():
                pass # skip over
            elif part in schema.keys():
                path = schema[part]
            else:
                raise Exception("No such field. Valid fields are: %s" % list(schema.keys()))
            if isinstance(path, (list, tuple)):
                path = path[0]
        return path

    def get_field(self, field, db=None, ignore_errors=False):
        """
        Get the value of a field.
        """
        field = self.__class__.get_field_alias(field)
        chain = field.split(".")
        path = self._follow_field_path(chain, db, ignore_errors)
        return path

    def _follow_field_path(self, chain, db=None, ignore_errors=False):
        """
        Follow a list of items. Return endpoint(s) only.
        With the db argument, can do joins across tables.
        self - current object
        returns - None, endpoint, of recursive list of endpoints
        """
        from .handle import HandleClass
        # start with [self, self, chain, path_to=[]]
        # results = []
        # expand when you reach multiple answers [obj, chain_left, []]
        # if you get to an endpoint, put results
        # go until nothing left to expand
        todo = [(self, self, [], chain)]
        results = []
        while todo:
            parent, current, path_to, chain = todo.pop()
            #print("expand:", parent.__class__.__name__,
            #      current.__class__.__name__,
            #      path_to,
            #      chain)
            keep_going = True
            p = 0
            while p < len(chain) and keep_going:
                #print("while:", path_to, chain[p:])
                part = chain[p]
                if hasattr(current, part): # attribute
                    current = getattr(current, part)
                    path_to.append(part)
                # need to consider current+part if current is list:
                elif isinstance(current, (list, tuple)):
                    if part.isdigit():
                        # followed by index, so continue here
                        if int(part) < len(current):
                            current = current[int(part)]
                            path_to.append(part)
                        elif ignore_errors:
                            current = None
                            keeping_going = False
                        else:
                            raise Exception("invalid index position")
                    else: # else branch! in middle, split paths
                        for i in range(len(current)):
                            #print("split list:", self.__class__.__name__,
                            #      current.__class__.__name__,
                            #      path_to[:],
                            #      [str(i)] + chain[p:])
                            todo.append([self, current, path_to[:], [str(i)] + chain[p:]])
                        current = None
                        keep_going = False
                else: # part not found on this self
                    # current is a handle
                    # part is something on joined object
                    if parent:
                        ptype = parent.__class__.get_field_type(".".join(path_to))
                        if isinstance(ptype, HandleClass):
                            if db:
                                # start over here:
                                obj = None
                                if current:
                                    obj = ptype.join(db, current)
                                if part == "self":
                                    current = obj
                                    path_to = []
                                    #print("split self:", obj.__class__.__name__,
                                    #      current.__class__.__name__,
                                    #      path_to,
                                    #      chain[p + 1:])
                                    todo.append([obj, current, path_to, chain[p + 1:]])
                                elif obj:
                                    current = getattr(obj, part)
                                    #print("split :", obj.__class__.__name__,
                                    #      current.__class__.__name__,
                                    #      [part],
                                    #      chain[p + 1:])
                                    todo.append([obj, current, [part], chain[p + 1:]])
                                current = None
                                keep_going = False
                            else:
                                raise Exception("Can't join without database")
                        elif part == "self":
                            pass
                        elif ignore_errors:
                            pass
                        else:
                            raise Exception("%s is not a valid field of %s; use %s" %
                                            (part, current, dir(current)))
                    current = None
                    keep_going = False
                p += 1
            if keep_going:
                results.append(current)
        if len(results) == 1:
            return results[0]
        elif len(results) == 0:
            return None
        else:
            return results

    def set_field(self, field, value, db=None, ignore_errors=False):
        """
        Set the value of a basic field (str, int, float, or bool).
        value can be a string or actual value.
        Returns number of items changed.
        """
        field = self.__class__.get_field_alias(field)
        chain = field.split(".")
        path = self._follow_field_path(chain[:-1], db, ignore_errors)
        ftype = self.get_field_type(field)
        # ftype is str, bool, float, or int
        value = (value in ['True', True]) if ftype is bool else value
        return self._set_fields(path, chain[-1], value, ftype)

    def _set_fields(self, path, attr, value, ftype):
        """
        Helper function to handle recursive lists of items.
        """
        from .handle import HandleClass
        if isinstance(path, (list, tuple)):
            count = 0
            for item in path:
                count += self._set_fields(item, attr, value, ftype)
        elif isinstance(ftype, HandleClass):
            setattr(path, attr, value)
            count = 1
        else:
            setattr(path, attr, ftype(value))
            count = 1
        return count

