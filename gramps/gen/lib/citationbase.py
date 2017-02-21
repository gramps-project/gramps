#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2011       Tim G L Lyons
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
CitationBase class for Gramps.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import logging

LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# CitationBase class
#
#-------------------------------------------------------------------------
class CitationBase:
    """
    Base class for storing citations.

    Starting in 3.4, the objects may have multiple citations.
    Internally, this class maintains a list of Citation handles,
    as a citation_list attribute of the CitationBase object.
    This class is analogous to the notebase class.
    Both these have no attributes of their own; in this respect, they differ
    from classes like MediaRef, which does have attributes (in that case,
    privacy, sources, notes and attributes).

    This class, together with the Citation class, replaces the old SourceRef
    class. I.e. SourceRef = CitationBase + Citation
    """
    def __init__(self, source=None):
        """
        Create a new CitationBase, copying from source if not None.

        :param source: Object used to initialize the new object
        :type source: CitationBase
        """
        self.citation_list = list(source.citation_list) if source else []

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return self.citation_list

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        self.citation_list = list(data)

    def add_citation(self, handle):
        """
        Add the :class:`~.citation.Citation` handle to the list of citation
        handles.

        :param handle: :class:`~.citation.Citation` handle to add the list of
                       citations
        :type handle: str

        :returns: True if handle was added, False if it already was in the list
        :rtype: bool
        """
        if handle in self.citation_list:
            return False
        else:
            self.citation_list.append(handle)
            return True

    def remove_citation_references(self, citation_handle_list):
        """
        Remove the specified handles from the list of citation handles, and all
        secondary child objects.

        :param citation_handle_list: The list of citation handles to be removed
        :type handle: list
        """
        LOG.debug('enter remove_citation handle: %s self: %s citation_list: %s',
                  citation_handle_list, self, self.citation_list)
        for handle in citation_handle_list:
            if handle in self.citation_list:
                LOG.debug('remove handle %s from citation_list %s',
                          handle, self.citation_list)
                self.citation_list.remove(handle)
        LOG.debug('get_citation_child_list %s', self.get_citation_child_list())
        for item in self.get_citation_child_list():
            item.remove_citation_references(citation_handle_list)

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer citations.

        All methods which inherit from CitationBase and have other child objects
        with citations, should return here a list of child objects which are
        CitationBase

        :returns: Returns the list of child secondary child objects that may
                  refer citations.
        :rtype: list
        """
        return []

    def get_citation_list(self):
        """
        Return the list of :class:`~.citation.Citation` handles associated with
        the object.

        :returns: The list of :class:`~.citation.Citation` handles
        :rtype: list
        """
        return self.citation_list

    def get_all_citation_lists(self):
        """
        Return the list of :class:`~.citation.Citation` handles associated with
        the object or with child objects.

        :returns: The list of :class:`~.citation.Citation` handles
        :rtype: list
        """
        all_citations = self.citation_list

        for item in self.get_citation_child_list():
            all_citations += item.get_citation_list()
            for subitem in item.get_citation_child_list():
                all_citations += subitem.get_citation_list()
        return all_citations

    def has_citation_reference(self, citation_handle):
        """
        Return True if the object or any of its child objects has reference
        to this citation handle.

        :param citation_handle: The citation handle to be checked.
        :type citation_handle: str
        :returns: Returns whether the object or any of its child objects has
                  reference to this citation handle.
        :rtype: bool
        """
        for citation_ref in self.citation_list:
            if citation_ref == citation_handle:
                return True

        LOG.debug("citation child list %s", self.get_citation_child_list())
        for item in self.get_citation_child_list():
            if item.has_citation_reference(citation_handle):
                return True

        return False

    def set_citation_list(self, citation_list):
        """
        Assign the passed list to be object's list of
        :class:`~.citation.Citation` handles.

        :param citation_list: List of :class:`~.citation.Citation` handles to
                              be set on the object
        :type citation_list: list
        """
        self.citation_list = citation_list

    def _merge_citation_list(self, acquisition):
        """
        Merge the list of citations from acquisition with our own.

        :param acquisition: The citation list of this object will be merged
                            with the current citation list.
        :type acquisition: CitationBase
        """
        for addendum in acquisition.citation_list:
            self.add_citation(addendum)

    def get_referenced_citation_handles(self):
        """
        Return the list of (classname, handle) tuples for all referenced
        citations.

        This method should be used to get the :class:`~.citation.Citation`
        portion of the list by objects that store citation lists.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return [('Citation', handle) for handle in self.citation_list]

    def replace_citation_references(self, old_handle, new_handle):
        """
        Replace references to citation handles in the list of this object and
        all child objects and merge equivalent entries.

        :param old_handle: The citation handle to be replaced.
        :type old_handle: str
        :param new_handle: The citation handle to replace the old one with.
        :type new_handle: str
        """
        refs_list = self.citation_list[:]
        new_ref = None
        if new_handle in self.citation_list:
            new_ref = new_handle
        n_replace = refs_list.count(old_handle)
        for ix_replace in range(n_replace):
            idx = refs_list.index(old_handle)
            if new_ref:
                self.citation_list.pop(idx)
                refs_list.pop(idx)
            else:
                self.citation_list[idx] = new_handle

        for item in self.get_citation_child_list():
            item.replace_citation_references(old_handle, new_handle)

class IndirectCitationBase:
    """
    Citation management logic for objects that don't have citations
    for the primary objects, but only for the child (secondary) ones.

    The derived class must implement the
    :meth:`~CitationBase.get_citation_child_list` method to return the list of
    child secondary objects that may refer citations.

    .. note:: for most objects, this functionality is inherited from
              :class:`CitationBase`, which checks both the object and the child
              objects.
    """
    def has_citation_reference(self, citation_handle):
        """
        Return True if any of the child objects has reference to this citation
        handle.

        :param citation_handle: The citation handle to be checked.
        :type citation_handle: str
        :returns: Returns whether any of it's child objects has reference to
                  this citation handle.
        :rtype: bool
        """
        for item in self.get_citation_child_list():
            if item.has_citation_reference(citation_handle):
                return True

        return False

    def replace_citation_references(self, old_handle, new_handle):
        """
        Replace references to citation handles in all child objects and merge
        equivalent entries.

        :param old_handle: The citation handle to be replaced.
        :type old_handle: str
        :param new_handle: The citation handle to replace the old one with.
        :type new_handle: str
        """
        for item in self.get_citation_child_list():
            item.replace_citation_references(old_handle, new_handle)

    def remove_citation_references(self, citation_handle_list):
        """
        Remove references to all citation handles in the list in all child
        objects.

        :param citation_handle_list: The list of citation handles to be removed.
        :type citation_handle_list: list
        """
        for item in self.get_citation_child_list():
            item.remove_citation_references(citation_handle_list)

    def get_citation_list(self):
        """
        Return the list of :class:`~gen.lib.citation.Citation` handles
        associated with the object. For an IndirectCitationBase this is always
        the empty list
        :returns: The list of :class:`~gen.lib.citation.Citation` handles
        :rtype: list
        """
        return []

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer citations.

        All methods which inherit from CitationBase and have other child objects
        with citations, should return here a list of child objects which are
        CitationBase

        :returns: Returns the list of child secondary child objects that may
                  refer citations.
        :rtype: list
        """
        return []
