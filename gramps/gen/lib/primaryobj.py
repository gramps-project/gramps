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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Basic Primary Object class for Gramps.
"""
from collections.abc import Collection

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
from typing_extensions import override, Self

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .citationbase import CitationBase
from .mediabase import MediaBase
from .notebase import NoteBase
from .privacybase import PrivacyBase
from .tableobj import TableObject
from .tagbase import TagBase


# -------------------------------------------------------------------------
#
# BasicPrimaryObject
#
# -------------------------------------------------------------------------
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

    def __init__(self, source: Self | None = None):
        """
        Initialize a PrimaryObject.

        If source is None, both the ID and handle are assigned as empty
        strings. If source is not None, then object is initialized from values
        of the source object.

        :param source: Object used to initialize the new object
        """
        TableObject.__init__(self, source)
        PrivacyBase.__init__(self, source)
        TagBase.__init__(self)
        self.gramps_id = source.get_gramps_id() if source else ""

    def set_gramps_id(self, gramps_id: str) -> None:
        """
        Set the Gramps ID for the primary object.

        :param gramps_id: Gramps ID
        """
        self.gramps_id = gramps_id

    def get_gramps_id(self) -> str:
        """
        Return the Gramps ID for the primary object.

        :returns: Gramps ID associated with the object
        """
        return self.gramps_id

    def has_handle_reference(self, classname: str, handle: str) -> bool:
        """
        Return True if the object has reference to a given handle of given
        primary object type.

        :param classname: The name of the primary object class.
        :param handle: The handle to be checked.

        :returns:
          Returns whether the object has reference to this handle of
          this object type.
        """
        return False

    def remove_handle_references(
        self, classname: str, handle_list: Collection[str]
    ) -> None:
        """
        Remove all references in this object to object handles in the list.

        :param classname: The name of the primary object class.
        :param handle_list: The list of handles to be removed.
        """

    def replace_handle_reference(
        self, classname: str, old_handle: str, new_handle: str
    ) -> None:
        """
        Replace all references to old handle with those to the new handle.

        :param classname: The name of the primary object class.
        :param old_handle: The handle to be replaced.
        :param new_handle: The handle to replace the old one with.
        """

    def has_citation_reference(self, handle: str) -> bool:
        """
        Indicate if the object has a citation references.

        In the base class, no such references exist. Derived classes should
        override this if they provide citation references.
        """
        return False

    def has_media_reference(self, handle: str) -> bool:
        """
        Indicate if the object has a media references.

        In the base class, no such references exist. Derived classes should
        override this if they provide media references.
        """
        return False

    def remove_citation_references(self, handle_list: Collection[str]) -> None:
        """
        Remove the specified citation references from the object.

        In the base class no such references exist. Derived classes should
        override this if they provide citation references.
        """

    def remove_media_references(self, handle_list: Collection[str]) -> None:
        """
        Remove the specified media references from the object.

        In the base class no such references exist. Derived classes should
        override this if they provide media references.
        """

    def remove_note_references(self, handle_list: Collection[str]) -> None:
        """
        Remove the specified note references from the object.

        In the base class no such references exist. Derived classes should
        override this if they provide note references.
        """

    def replace_citation_references(self, old_handle: str, new_handle: str) -> None:
        """
        Replace all references to the old citation handle with those to the new
        citation handle.
        """

    def replace_media_references(self, old_handle: str, new_handle: str) -> None:
        """
        Replace all references to the old media handle with those to the new
        media handle.
        """


# -------------------------------------------------------------------------
#
# Primary Object class
#
# -------------------------------------------------------------------------
class PrimaryObject(BasicPrimaryObject):
    """
    The PrimaryObject is the base class for all primary objects in the
    database.

    Primary objects are the core objects in the database.
    Each object has a database handle and a Gramps ID value. The database
    handle is used as the record number for the database, and the Gramps
    ID is the user visible version.
    """

    def __init__(self, source: Self | None = None):
        """
        Initialize a PrimaryObject.

        If source is None, both the ID and handle are assigned as empty
        strings. If source is not None, then object is initialized from values
        of the source object.

        :param source: Object used to initialize the new object
        """
        BasicPrimaryObject.__init__(self, source)

    @override
    def has_handle_reference(self, classname: str, handle: str) -> bool:
        if classname == "Citation" and isinstance(self, CitationBase):
            return self.has_citation_reference(handle)
        if classname == "Media" and isinstance(self, MediaBase):
            return self.has_media_reference(handle)
        return self._has_handle_reference(classname, handle)

    @override
    def remove_handle_references(
        self, classname: str, handle_list: Collection[str]
    ) -> None:
        if classname == "Citation" and isinstance(self, CitationBase):
            self.remove_citation_references(handle_list)
        elif classname == "Media" and isinstance(self, MediaBase):
            self.remove_media_references(handle_list)
        elif classname == "Note" and isinstance(self, NoteBase):
            self.remove_note_references(handle_list)
        else:
            self._remove_handle_references(classname, handle_list)

    @override
    def replace_handle_reference(
        self, classname: str, old_handle: str, new_handle: str
    ) -> None:
        if classname == "Citation" and isinstance(self, CitationBase):
            self.replace_citation_references(old_handle, new_handle)
        elif classname == "Media" and isinstance(self, MediaBase):
            self.replace_media_references(old_handle, new_handle)
        else:
            self._replace_handle_reference(classname, old_handle, new_handle)

    def _has_handle_reference(self, classname: str, handle: str) -> bool:
        """
        Return True if the handle is referenced by the object.
        """
        return False

    def _remove_handle_references(
        self, classname: str, handle_list: Collection[str]
    ) -> None:
        """
        Remove the handle references from the object.
        """
        pass

    def _replace_handle_reference(
        self, classname: str, old_handle: str, new_handle: str
    ) -> None:
        """
        Replace the handle reference with the new reference.
        """
        pass
