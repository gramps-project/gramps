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

    def include_person(self, handle):
        obj = self.get_unfiltered_person(handle)
        return bool(obj and not obj.private)

    def include_family(self, handle):
        obj = self.get_unfiltered_family(handle)
        return bool(obj and not obj.private)

    def include_event(self, handle):
        obj = self.get_unfiltered_event(handle)
        return bool(obj and not obj.private)

    def include_source(self, handle):
        obj = self.get_unfiltered_source(handle)
        return bool(obj and not obj.private)

    def include_citation(self, handle):
        obj = self.get_unfiltered_citation(handle)
        return bool(obj and not obj.private)

    def include_place(self, handle):
        obj = self.get_unfiltered_place(handle)
        return bool(obj and not obj.private)

    def include_media(self, handle):
        obj = self.get_unfiltered_media(handle)
        return bool(obj and not obj.private)

    def include_repository(self, handle):
        obj = self.get_unfiltered_repository(handle)
        return bool(obj and not obj.private)

    def include_note(self, handle):
        obj = self.get_unfiltered_note(handle)
        return bool(obj and not obj.private)

    # -----------------------------------------------------------------------
    # sanitize_* methods — strip private sub-attributes from a DataDict.
    # Cross-reference filtering (note_list, citation_list, etc.) is already
    # handled by the base class get_raw_*_data() using include_* predicates.
    # These methods handle sub-object privacy flags.
    # -----------------------------------------------------------------------

    def sanitize_person(self, data):
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
        # Filter private attributes
        data.attribute_list = [a for a in data.attribute_list if not a.private]
        # Filter private addresses
        data.address_list = [a for a in data.address_list if not a.private]
        # Filter private LDS ordinances
        data.lds_ord_list = [o for o in data.lds_ord_list if not o.private]
        # Filter private event refs (event itself filtered by base; ref may be private)
        data.event_ref_list = [ref for ref in data.event_ref_list if not ref.private]
        # Filter private person refs (associations)
        data.person_ref_list = [ref for ref in data.person_ref_list if not ref.private]
        # Filter private media refs
        data.media_list = [ref for ref in data.media_list if not ref.private]
        return data

    def sanitize_family(self, data):
        # Filter private child refs
        data.child_ref_list = [ref for ref in data.child_ref_list if not ref.private]
        # Filter private event refs
        data.event_ref_list = [ref for ref in data.event_ref_list if not ref.private]
        # Filter private attributes
        data.attribute_list = [a for a in data.attribute_list if not a.private]
        # Filter private LDS ordinances
        data.lds_ord_list = [o for o in data.lds_ord_list if not o.private]
        # Filter private media refs
        data.media_list = [ref for ref in data.media_list if not ref.private]
        return data

    def sanitize_event(self, data):
        # Filter private attributes
        data.attribute_list = [a for a in data.attribute_list if not a.private]
        # Filter private media refs
        data.media_list = [ref for ref in data.media_list if not ref.private]
        return data

    def sanitize_source(self, data):
        # Filter private repo refs
        data.reporef_list = [ref for ref in data.reporef_list if not ref.private]
        # Filter private media refs
        data.media_list = [ref for ref in data.media_list if not ref.private]
        return data

    def sanitize_citation(self, data):
        # Filter private media refs
        data.media_list = [ref for ref in data.media_list if not ref.private]
        return data

    def sanitize_place(self, data):
        # Filter private media refs
        data.media_list = [ref for ref in data.media_list if not ref.private]
        # Filter private urls
        data.urls = [u for u in data.urls if not u.private]
        return data

    def sanitize_repository(self, data):
        # Filter private addresses
        data.address_list = [a for a in data.address_list if not a.private]
        # Filter private urls
        data.urls = [u for u in data.urls if not u.private]
        return data

    def sanitize_media(self, data):
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
