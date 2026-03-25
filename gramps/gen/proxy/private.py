#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Brian G. Matherly
# Copyright (C) 2010       Nick Hall
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Proxy class for the Gramps databases. Filter out all data marked private.
"""

# -------------------------------------------------------------------------
#
# Python libraries
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps libraries
#
# -------------------------------------------------------------------------
from .proxybase import ProxyDbBase


class PrivateProxyDb(ProxyDbBase):
    """
    A proxy to a Gramps database. This proxy will act like a Gramps database,
    but all data marked private will be hidden from the user.
    """

    def __init__(self, db):
        """
        Create a new PrivateProxyDb instance.
        """
        ProxyDbBase.__init__(self, db)

    # -----------------------------------------------------------------------
    # include_* predicates — exclude objects marked private
    # -----------------------------------------------------------------------

    def include_person(self, handle: str) -> bool:
        """
        Return False if the person is marked private, True otherwise.

        :param handle: database handle of the Person to test
        :type handle: str
        :returns: True if the person is not private and should be visible
        :rtype: bool
        """
        if not self.db.has_person_handle(handle):
            return False
        obj = self.get_unfiltered_person(handle)
        return bool(obj and not obj.private)

    def include_family(self, handle: str) -> bool:
        """
        Return False if the family is marked private, True otherwise.

        :param handle: database handle of the Family to test
        :type handle: str
        :returns: True if the family is not private and should be visible
        :rtype: bool
        """
        if not self.db.has_family_handle(handle):
            return False
        obj = self.get_unfiltered_family(handle)
        return bool(obj and not obj.private)

    def include_event(self, handle: str) -> bool:
        """
        Return False if the event is marked private, True otherwise.

        :param handle: database handle of the Event to test
        :type handle: str
        :returns: True if the event is not private and should be visible
        :rtype: bool
        """
        if not self.db.has_event_handle(handle):
            return False
        obj = self.get_unfiltered_event(handle)
        return bool(obj and not obj.private)

    def include_source(self, handle: str) -> bool:
        """
        Return False if the source is marked private, True otherwise.

        :param handle: database handle of the Source to test
        :type handle: str
        :returns: True if the source is not private and should be visible
        :rtype: bool
        """
        if not self.db.has_source_handle(handle):
            return False
        obj = self.get_unfiltered_source(handle)
        return bool(obj and not obj.private)

    def include_citation(self, handle: str) -> bool:
        """
        Return False if the citation is marked private or if its referenced
        source is private, True otherwise.

        :param handle: database handle of the Citation to test
        :type handle: str
        :returns: True if the citation and its source are not private
        :rtype: bool
        """
        if not self.db.has_citation_handle(handle):
            return False
        obj = self.get_unfiltered_citation(handle)
        if not obj or obj.private:
            return False
        # Also exclude citations whose referenced source is private
        source_handle = obj.get_reference_handle()
        if source_handle:
            source = self.get_unfiltered_source(source_handle)
            if source and source.private:
                return False
        return True

    def include_place(self, handle: str) -> bool:
        """
        Return False if the place is marked private, True otherwise.

        :param handle: database handle of the Place to test
        :type handle: str
        :returns: True if the place is not private and should be visible
        :rtype: bool
        """
        if not self.db.has_place_handle(handle):
            return False
        obj = self.get_unfiltered_place(handle)
        return bool(obj and not obj.private)

    def include_media(self, handle: str) -> bool:
        """
        Return False if the media object is marked private, True otherwise.

        :param handle: database handle of the Media to test
        :type handle: str
        :returns: True if the media is not private and should be visible
        :rtype: bool
        """
        if not self.db.has_media_handle(handle):
            return False
        obj = self.get_unfiltered_media(handle)
        return bool(obj and not obj.private)

    def include_repository(self, handle: str) -> bool:
        """
        Return False if the repository is marked private, True otherwise.

        :param handle: database handle of the Repository to test
        :type handle: str
        :returns: True if the repository is not private and should be visible
        :rtype: bool
        """
        if not self.db.has_repository_handle(handle):
            return False
        obj = self.get_unfiltered_repository(handle)
        return bool(obj and not obj.private)

    def include_note(self, handle: str) -> bool:
        """
        Return False if the note is marked private or if any embedded
        gramps:// link refers to a filtered-out object, True otherwise.

        :param handle: database handle of the Note to test
        :type handle: str
        :returns: True if the note is not private and all its links are visible
        :rtype: bool
        """
        if not self.db.has_note_handle(handle):
            return False
        obj = self.get_unfiltered_note(handle)
        if not (obj and not obj.private):
            return False
        return self._note_links_included(handle)

    # -----------------------------------------------------------------------
    # sanitize_* methods — strip private sub-attributes from a DataDict.
    # Cross-reference filtering (note_list, citation_list, etc.) is already
    # handled by the base class get_raw_*_data() using include_* predicates.
    # These methods handle sub-object privacy flags.
    # -----------------------------------------------------------------------

    def _clean_subrefs(self, item) -> None:
        """Strip private notes and citations from a sub-object DataDict."""
        if hasattr(item, "note_list"):
            item["note_list"] = [h for h in item.note_list if self.include_note(h)]
        if hasattr(item, "citation_list"):
            item["citation_list"] = [
                h for h in item.citation_list if self.include_citation(h)
            ]

    def sanitize_person(self, data: "DataDict") -> "DataDict":
        """
        Strip private sub-attributes from a person DataDict in place.

        Removes private alternate names, event refs, person refs, attributes,
        addresses, LDS ordinances, and media refs.  The primary name is
        replaced with a placeholder if it is marked private.

        :param data: raw DataDict for the Person, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        # Filter private alternate names
        data.alternate_names = [n for n in data.alternate_names if not n.private]
        # Filter private primary name — replace with placeholder if private
        if data.primary_name.private:
            from ..lib.json_utils import object_to_data
            from ..lib import Name, Surname

            placeholder = Name()
            surn = Surname()
            surn.set_surname(_("Private"))
            placeholder.set_surname_list([surn])
            placeholder.set_primary_surname()
            data.primary_name = object_to_data(placeholder)
        else:
            self._clean_subrefs(data.primary_name)
        # Clean sub-notes/citations from surviving alternate names
        for name in data["alternate_names"]:
            self._clean_subrefs(name)
        # Filter private attributes
        data["attribute_list"] = [a for a in data.attribute_list if not a.private]
        # Filter private addresses; clean sub-refs from survivors
        data["address_list"] = [a for a in data.address_list if not a.private]
        for addr in data["address_list"]:
            self._clean_subrefs(addr)
        # Filter private LDS ordinances; clean sub-refs and clear private handles
        data["lds_ord_list"] = [o for o in data.lds_ord_list if not o.private]
        for lds in data["lds_ord_list"]:
            self._clean_subrefs(lds)
            if lds.famc and not self.include_family(lds.famc):
                lds["famc"] = None
            if lds.place and not self.include_place(lds.place):
                lds["place"] = None
        # Filter private event refs (event itself filtered by base; ref may be private)
        data["event_ref_list"] = [ref for ref in data.event_ref_list if not ref.private]
        for ref in data["event_ref_list"]:
            self._clean_subrefs(ref)
        # Filter private person refs (associations); clean sub-refs from survivors
        data["person_ref_list"] = [
            ref for ref in data.person_ref_list if not ref.private
        ]
        for ref in data["person_ref_list"]:
            self._clean_subrefs(ref)
        # Filter private media refs; clean sub-refs from survivors
        data["media_list"] = [ref for ref in data.media_list if not ref.private]
        for ref in data["media_list"]:
            self._clean_subrefs(ref)
        return data

    def sanitize_family(self, data: "DataDict") -> "DataDict":
        """
        Strip private sub-attributes from a family DataDict in place.

        Removes private child refs, event refs, attributes, LDS ordinances,
        and media refs.

        :param data: raw DataDict for the Family, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        # Filter private child refs; clean sub-refs from survivors
        data["child_ref_list"] = [ref for ref in data.child_ref_list if not ref.private]
        for ref in data["child_ref_list"]:
            self._clean_subrefs(ref)
        # Filter private event refs; clean sub-refs from survivors
        data["event_ref_list"] = [ref for ref in data.event_ref_list if not ref.private]
        for ref in data["event_ref_list"]:
            self._clean_subrefs(ref)
        # Filter private attributes
        data["attribute_list"] = [a for a in data.attribute_list if not a.private]
        # Filter private LDS ordinances; clean sub-refs and clear private handles
        data["lds_ord_list"] = [o for o in data.lds_ord_list if not o.private]
        for lds in data["lds_ord_list"]:
            self._clean_subrefs(lds)
            if lds.famc and not self.include_family(lds.famc):
                lds["famc"] = None
            if lds.place and not self.include_place(lds.place):
                lds["place"] = None
        # Filter private media refs; clean sub-refs from survivors
        data["media_list"] = [ref for ref in data.media_list if not ref.private]
        for ref in data["media_list"]:
            self._clean_subrefs(ref)
        return data

    def sanitize_event(self, data: "DataDict") -> "DataDict":
        """
        Strip private sub-attributes from an event DataDict in place.

        Removes private attributes and media refs.

        :param data: raw DataDict for the Event, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        # Filter private attributes
        data.attribute_list = [a for a in data.attribute_list if not a.private]
        # Filter private media refs
        data.media_list = [ref for ref in data.media_list if not ref.private]
        return data

    def sanitize_source(self, data: "DataDict") -> "DataDict":
        """
        Strip private sub-attributes from a source DataDict in place.

        Removes private repository refs and media refs.

        :param data: raw DataDict for the Source, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        # Filter private repo refs
        data.reporef_list = [ref for ref in data.reporef_list if not ref.private]
        # Filter private media refs
        data.media_list = [ref for ref in data.media_list if not ref.private]
        return data

    def sanitize_citation(self, data: "DataDict") -> "DataDict":
        """
        Strip private sub-attributes from a citation DataDict in place.

        Removes private media refs.

        :param data: raw DataDict for the Citation, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        # Filter private media refs
        data.media_list = [ref for ref in data.media_list if not ref.private]
        return data

    def sanitize_place(self, data: "DataDict") -> "DataDict":
        """
        Strip private sub-attributes from a place DataDict in place.

        Removes private media refs and URLs.

        :param data: raw DataDict for the Place, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        # Filter private media refs
        data.media_list = [ref for ref in data.media_list if not ref.private]
        # Filter private urls
        data.urls = [u for u in data.urls if not u.private]
        return data

    def sanitize_repository(self, data: "DataDict") -> "DataDict":
        """
        Strip private sub-attributes from a repository DataDict in place.

        Removes private addresses and URLs.

        :param data: raw DataDict for the Repository, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        # Filter private addresses
        data.address_list = [a for a in data.address_list if not a.private]
        # Filter private urls
        data.urls = [u for u in data.urls if not u.private]
        return data

    def sanitize_media(self, data: "DataDict") -> "DataDict":
        """
        Strip private sub-attributes from a media DataDict in place.

        Removes private attributes.

        :param data: raw DataDict for the Media, already cross-ref-filtered
        :type data: DataDict
        :returns: the sanitized DataDict
        :rtype: DataDict
        """
        # Filter private attributes
        data.attribute_list = [a for a in data.attribute_list if not a.private]
        return data

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.
        Returns an iterator over a list of (class_name, handle) tuples.
        """
        objects = {
            "Person": self.get_unfiltered_person,
            "Family": self.get_unfiltered_family,
            "Event": self.get_unfiltered_event,
            "Source": self.get_unfiltered_source,
            "Citation": self.get_unfiltered_citation,
            "Place": self.get_unfiltered_place,
            "Media": self.get_unfiltered_media,
            "Note": self.get_unfiltered_note,
            "Repository": self.get_unfiltered_repository,
        }

        handle_itr = self.db.find_backlink_handles(handle, include_classes)
        for class_name, handle in handle_itr:
            if class_name in objects:
                obj = objects[class_name](handle)
                if obj and not obj.private:
                    yield (class_name, handle)
            else:
                raise NotImplementedError
