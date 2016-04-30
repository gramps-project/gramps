#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007 Donald N. Allingham
# Copyright (C) 2011      Tim G L Lyons
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
Basic Primary Object class for Gramps.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .tableobj import TableObject
from .privacybase import PrivacyBase
from .citationbase import CitationBase
from .mediabase import MediaBase
from .tagbase import TagBase

#-------------------------------------------------------------------------
#
# Basic Primary Object class
#
#-------------------------------------------------------------------------
class BasicPrimaryObject(TableObject, PrivacyBase, TagBase):
    """
    The BasicPrimaryObject is the base class for :class:`~.note.Note` objects.

    It is also the base class for the :class:`PrimaryObject` class.

    The :class:`PrimaryObject` is the base class for all other primary objects
    in the database. Primary objects are the core objects in the database.
    Each object has a database handle and a Gramps ID value. The database
    handle is used as the record number for the database, and the Gramps
    ID is the user visible version.
    """

    def __init__(self, source=None):
        """
        Initialize a PrimaryObject.

        If source is None, both the ID and handle are assigned as empty
        strings. If source is not None, then object is initialized from values
        of the source object.

        :param source: Object used to initialize the new object
        :type source: PrimaryObject
        """
        TableObject.__init__(self, source)
        PrivacyBase.__init__(self, source)
        TagBase.__init__(self)
        if source:
            self.gramps_id = source.gramps_id
        else:
            self.gramps_id = None

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

    def set_gramps_id(self, gramps_id):
        """
        Set the Gramps ID for the primary object.

        :param gramps_id: Gramps ID
        :type gramps_id: str
        """
        self.gramps_id = gramps_id

    def get_gramps_id(self):
        """
        Return the Gramps ID for the primary object.

        :returns: Gramps ID associated with the object
        :rtype: str
        """
        return self.gramps_id

    def has_handle_reference(self, classname, handle):
        """
        Return True if the object has reference to a given handle of given
        primary object type.

        :param classname: The name of the primary object class.
        :type classname: str
        :param handle: The handle to be checked.
        :type handle: str

        :returns:
          Returns whether the object has reference to this handle of
          this object type.

        :rtype: bool
        """
        return False

    def remove_handle_references(self, classname, handle_list):
        """
        Remove all references in this object to object handles in the list.

        :param classname: The name of the primary object class.
        :type classname: str
        :param handle_list: The list of handles to be removed.
        :type handle_list: str
        """
        pass

    def replace_handle_reference(self, classname, old_handle, new_handle):
        """
        Replace all references to old handle with those to the new handle.

        :param classname: The name of the primary object class.
        :type classname: str
        :param old_handle: The handle to be replaced.
        :type old_handle: str
        :param new_handle: The handle to replace the old one with.
        :type new_handle: str
        """
        pass

    def has_citation_reference(self, handle):
        """
        Indicate if the object has a citation references.

        In the base class, no such references exist. Derived classes should
        override this if they provide citation references.
        """
        return False

    def has_media_reference(self, handle):
        """
        Indicate if the object has a media references.

        In the base class, no such references exist. Derived classes should
        override this if they provide media references.
        """
        return False

    def remove_citation_references(self, handle_list):
        """
        Remove the specified citation references from the object.

        In the base class no such references exist. Derived classes should
        override this if they provide citation references.
        """
        pass

    def remove_media_references(self, handle_list):
        """
        Remove the specified media references from the object.

        In the base class no such references exist. Derived classes should
        override this if they provide media references.
        """
        pass

    def replace_citation_references(self, old_handle, new_handle):
        """
        Replace all references to the old citation handle with those to the new
        citation handle.
        """
        pass

    def replace_media_references(self, old_handle, new_handle):
        """
        Replace all references to the old media handle with those to the new
        media handle.
        """
        pass

#-------------------------------------------------------------------------
#
# Primary Object class
#
#-------------------------------------------------------------------------
class PrimaryObject(BasicPrimaryObject):
    """
    The PrimaryObject is the base class for all primary objects in the
    database.

    Primary objects are the core objects in the database.
    Each object has a database handle and a Gramps ID value. The database
    handle is used as the record number for the database, and the Gramps
    ID is the user visible version.
    """

    def __init__(self, source=None):
        """
        Initialize a PrimaryObject.

        If source is None, both the ID and handle are assigned as empty
        strings. If source is not None, then object is initialized from values
        of the source object.

        :param source: Object used to initialize the new object
        :type source: PrimaryObject
        """
        BasicPrimaryObject.__init__(self, source)

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

    def has_handle_reference(self, classname, handle):
        """
        Return True if the object has reference to a given handle of given
        primary object type.

        :param classname: The name of the primary object class.
        :type classname: str
        :param handle: The handle to be checked.
        :type handle: str
        :returns: Returns whether the object has reference to this handle
                  of this object type.
        :rtype: bool
        """
        if classname == 'Citation' and isinstance(self, CitationBase):
            return self.has_citation_reference(handle)
        elif classname == 'Media' and isinstance(self, MediaBase):
            return self.has_media_reference(handle)
        else:
            return self._has_handle_reference(classname, handle)

    def remove_handle_references(self, classname, handle_list):
        """
        Remove all references in this object to object handles in the list.

        :param classname: The name of the primary object class.
        :type classname: str
        :param handle_list: The list of handles to be removed.
        :type handle_list: str
        """
        if classname == 'Citation' and isinstance(self, CitationBase):
            self.remove_citation_references(handle_list)
        elif classname == 'Media' and isinstance(self, MediaBase):
            self.remove_media_references(handle_list)
        else:
            self._remove_handle_references(classname, handle_list)

    def replace_handle_reference(self, classname, old_handle, new_handle):
        """
        Replace all references to old handle with those to the new handle.

        :param classname: The name of the primary object class.
        :type classname: str
        :param old_handle: The handle to be replaced.
        :type old_handle: str
        :param new_handle: The handle to replace the old one with.
        :type new_handle: str
        """
        if classname == 'Citation' and isinstance(self, CitationBase):
            self.replace_citation_references(old_handle, new_handle)
        elif classname == 'Media' and isinstance(self, MediaBase):
            self.replace_media_references(old_handle, new_handle)
        else:
            self._replace_handle_reference(classname, old_handle, new_handle)

    def _has_handle_reference(self, classname, handle):
        """
        Return True if the handle is referenced by the object.
        """
        return False

    def _remove_handle_references(self, classname, handle_list):
        """
        Remove the handle references from the object.
        """
        pass

    def _replace_handle_reference(self, classname, old_handle, new_handle):
        """
        Replace the handle reference with the new reference.
        """
        pass
