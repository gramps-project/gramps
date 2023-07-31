#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2016       Tim G L Lyons
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
Dummy database. This database is always empty and is read only.

It is provided for the initial database on loading Gramps, and also as a
database when a normal database is closed.

Most of the code in Gramps uses dbstate.db.is_open() to determine whether data
can be fetched from a database (essentially to determine whether there is a
database to fetch data from). Thus, dbstate.db cannot be left as 'None' because
None has no 'is_open' attribute. Therefore this database class is provided so
that it can be instantiated for dbstate.db.

FIXME: Ideally, only is_open() needs to be implemented here, because that is the
only method that should really be called, but the Gramps code is not perfect,
and many other methods are called. Calls of other methods could be considered
bugs, so when these are fixed, this class could be reduced.

FIXME: Errors in calling these methods (e.g. accessing data when the database is
closed) should result in exceptions. However, at present (mid-2016) there are so
many cases where these methods are called in error that raising exceptions would
be too disruptive. Hence such errors only result in a warning log message and a
'meaningful' result is returned. When the rest of Gramps code is fixed, these
methods should be changed to generate exceptions. Possibly by globally changing
'LOG.debug' to 'raise DbException'.
"""

# -------------------------------------------------------------------------
#
# Python libraries
#
# -------------------------------------------------------------------------
import logging
import inspect
from abc import ABCMeta
from types import FunctionType
from functools import wraps

# -------------------------------------------------------------------------
#
# Gramps libraries
#
# -------------------------------------------------------------------------
from .base import DbReadBase
from .bookmarks import DbBookmarks
from .dbconst import DBLOGNAME
from ..errors import HandleError
from ..utils.callback import Callback
from ..lib import Researcher
from ..const import GRAMPS_LOCALE as glocale

LOG = logging.getLogger(DBLOGNAME)


# -------------------------------------------------------------------------
#
# some magic, see http://stackoverflow.com/questions/11349183/how-to-wrap-every-
# method-of-a-class
#
# This processes the DummyDb class for diagnostic purposes to wrap each method
# with code to log the method name and where it was called from.
# -------------------------------------------------------------------------
def wrapper(method):
    """
    wrapper method that returns a 'wrapped' method which can be wrapped round
    every function in a class. The 'wrapped' method logs the original function
    that was called, and where it was called from.
    """

    @wraps(method)
    def wrapped(*args, **keywargs):
        """
        This 'wrapped' method logs the original function that was called, and
        where it was called from.
        """
        if __debug__ and LOG.isEnabledFor(logging.DEBUG):
            class_name = args[0].__class__.__name__
            func_name = method.__name__
            frame = inspect.currentframe()
            c_frame = frame.f_back
            c_code = c_frame.f_code
            LOG.debug(
                "calling %s.%s()... from file %s, line %s in %s",
                class_name,
                func_name,
                c_code.co_filename,
                c_frame.f_lineno,
                c_code.co_name,
            )
        return method(*args, **keywargs)

    return wrapped


class MetaClass(type):
    """
    transform class by wrapping it with a diagnostic wrapper (if __debig__ is
    not set
    """

    def __new__(mcs, class_name, bases, classdict):
        """
        When the class this is applied to (DummyDb) is instantiated, each method
        in the class is wrapped with a diagnostic routine.
        """
        newclassdict = {}
        for attributename, attribute in classdict.items():
            if isinstance(attribute, FunctionType):
                # replace with a wrapped version
                attribute = wrapper(attribute)
            newclassdict[attributename] = attribute
        return type.__new__(mcs, class_name, bases, newclassdict)


class M_A_M_B(ABCMeta, MetaClass):
    """
    Metaclass that inherits from two different metaclasses, so as to avoid
    error: "metaclass conflict: the metaclass of a derived class must be a (non-
    strict) subclass of the metaclasses of all its bases"

    See recipe: http://code.activestate.com/recipes/204197-solving-the-
    metaclass-conflict/
    """

    pass


# -------------------------------------------------------------------------
#
# class DummyDb
#
# -------------------------------------------------------------------------
class DummyDb(
    M_A_M_B(
        "NewBaseClass",
        (
            DbReadBase,
            Callback,
            object,
        ),
        {},
    )
):
    """
    Gramps database object. This object is a dummy database class that is always
    empty and is read-only.
    """

    __signals__ = {}

    def __init__(self):
        """
        Create a new DummyDb instance.
        """
        Callback.__init__(self)
        self.basedb = None
        self.__feature = {}  # {"feature": VALUE, ...}
        self.db_is_open = False
        self.readonly = True
        self.name_formats = []
        self.bookmarks = DbBookmarks()
        self.family_bookmarks = DbBookmarks()
        self.event_bookmarks = DbBookmarks()
        self.place_bookmarks = DbBookmarks()
        self.citation_bookmarks = DbBookmarks()
        self.source_bookmarks = DbBookmarks()
        self.repo_bookmarks = DbBookmarks()
        self.media_bookmarks = DbBookmarks()
        self.note_bookmarks = DbBookmarks()
        self.owner = Researcher()

    def get_feature(self, feature):
        """
        Databases can implement certain features or not. The default is
        None, unless otherwise explicitly stated.
        """
        return self.__feature.get(feature, None)  # can also be explicitly None

    def set_feature(self, feature, value):
        """
        Databases can implement certain features.
        """
        self.__feature[feature] = value

    def close(self, update=True, user=None):
        """
        Close the specified database.
        """
        if not self.db_is_open:
            LOG.warning("database is already closed")
        else:
            self.db_is_open = False

    def db_has_bm_changes(self):
        """
        Return whether there were bookmark changes during the session.
        """
        if not self.db_is_open:
            LOG.warning("database is already closed")
        LOG.warning("database is readonly")
        return False

    def find_backlink_handles(self, handle, include_classes=None):
        """
        Find all objects that hold a reference to the object handle.

        Returns an iterator over a list of (class_name, handle) tuples.

        :param handle: handle of the object to search for.
        :type handle: database handle
        :param include_classes: list of class names to include in the results.
            Default is None which includes all classes.
        :type include_classes: list of class names

        This default implementation does a sequential scan through all
        the primary object databases and is very slow. Backends can
        override this method to provide much faster implementations that
        make use of additional capabilities of the backend.

        Note that this is a generator function, it returns a iterator for
        use in loops. If you want a list of the results use::

            result_list = list(find_backlink_handles(handle))
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        return []

    def find_initial_person(self):
        """
        Returns first person in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return None

    def find_next_event_gramps_id(self):
        """
        Return the next available Gramps ID for a Event object based off the
        event ID prefix.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return ""

    def find_next_family_gramps_id(self):
        """
        Return the next available Gramps ID for a Family object based off the
        family ID prefix.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return ""

    def find_next_note_gramps_id(self):
        """
        Return the next available Gramps ID for a Note object based off the
        note ID prefix.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return ""

    def find_next_media_gramps_id(self):
        """
        Return the next available Gramps ID for a Media object based
        off the media object ID prefix.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return ""

    def find_next_person_gramps_id(self):
        """
        Return the next available Gramps ID for a Person object based off the
        person ID prefix.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return ""

    def find_next_place_gramps_id(self):
        """
        Return the next available Gramps ID for a Place object based off the
        place ID prefix.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return ""

    def find_next_repository_gramps_id(self):
        """
        Return the next available Gramps ID for a Repository object based
        off the repository ID prefix.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return ""

    def find_next_source_gramps_id(self):
        """
        Return the next available Gramps ID for a Source object based off the
        source ID prefix.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return ""

    def get_bookmarks(self):
        """
        Return the list of Person handles in the bookmarks.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return self.bookmarks

    def get_child_reference_types(self):
        """
        Return a list of all child reference types associated with Family
        instances in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_default_handle(self):
        """
        Return the default Person of the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return None

    def get_default_person(self):
        """
        Return the default Person of the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return None

    def get_event_bookmarks(self):
        """
        Return the list of Event handles in the bookmarks.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return self.event_bookmarks

    def get_event_cursor(self):
        """
        Return a reference to a cursor over event objects
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_event_from_gramps_id(self, val):
        """
        Find an Event in the database from the passed Gramps ID.

        If no such Event exists, None is returned.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("gramps_id %s does not exist in the dummy database", val)
        return None

    def get_event_from_handle(self, handle):
        """
        Find a Event in the database from the passed Gramps ID.

        If no such Event exists, a HandleError is raised.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        return None

    def get_event_handles(self):
        """
        Return a list of database handles, one handle for each Event in the
        database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_event_roles(self):
        """
        Return a list of all custom event role names associated with Event
        instances in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_event_attribute_types(self):
        """
        Return a list of all Attribute types assocated with Event instances
        in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_event_types(self):
        """
        Return a list of all event types in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_family_attribute_types(self):
        """
        Return a list of all Attribute types associated with Family instances
        in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_family_bookmarks(self):
        """
        Return the list of Family handles in the bookmarks.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return self.family_bookmarks

    def get_family_cursor(self):
        """
        Return a reference to a cursor over Family objects
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_family_event_types(self):
        """
        Deprecated:  Use get_event_types
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_family_from_gramps_id(self, val):
        """
        Find a Family in the database from the passed Gramps ID.

        If no such Family exists, None is returned.
        Need to be overridden by the derived class.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("gramps_id %s does not exist in the dummy database", val)
        return None

    def get_family_from_handle(self, handle):
        """
        Find a Family in the database from the passed Gramps ID.

        If no such Family exists, a HandleError is raised.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_family_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Family in
        the database.

        :param sort_handles: If True, the list is sorted by surnames.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_family_relation_types(self):
        """
        Return a list of all relationship types associated with Family
        instances in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_media_attribute_types(self):
        """
        Return a list of all Attribute types associated with Media and MediaRef
        instances in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_media_bookmarks(self):
        """
        Return the list of Media handles in the bookmarks.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return self.media_bookmarks

    def get_media_cursor(self):
        """
        Return a reference to a cursor over Media objects
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_media_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Media in
        the database.

        :param sort_handles: If True, the list is sorted by title.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_mediapath(self):
        """
        Return the default media path of the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return ""

    def get_name_group_keys(self):
        """
        Return the defined names that have been assigned to a default grouping.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_name_group_mapping(self, surname):
        """
        Return the default grouping name for a surname.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return ""

    def get_name_types(self):
        """
        Return a list of all custom names types associated with Person
        instances in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_origin_types(self):
        """
        Return a list of all custom origin types associated with Person/Surname
        instances in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_note_bookmarks(self):
        """
        Return the list of Note handles in the bookmarks.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return self.media_bookmarks

    def get_note_cursor(self):
        """
        Return a reference to a cursor over Note objects
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_note_from_gramps_id(self, val):
        """
        Find a Note in the database from the passed Gramps ID.

        If no such Note exists, None is returned.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("gramps_id %s does not exist in the dummy database", val)
        return None

    def get_note_from_handle(self, handle):
        """
        Find a Note in the database from the passed Gramps ID.

        If no such Note exists, a HandleError is raised.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_note_handles(self):
        """
        Return a list of database handles, one handle for each Note in the
        database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_note_types(self):
        """
        Return a list of all custom note types associated with Note instances
        in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_number_of_events(self):
        """
        Return the number of events currently in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return 0

    def get_number_of_families(self):
        """
        Return the number of families currently in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return 0

    def get_number_of_media(self):
        """
        Return the number of media objects currently in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return 0

    def get_number_of_notes(self):
        """
        Return the number of notes currently in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return 0

    def get_number_of_people(self):
        """
        Return the number of people currently in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return 0

    def get_number_of_places(self):
        """
        Return the number of places currently in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return 0

    def get_number_of_repositories(self):
        """
        Return the number of source repositories currently in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return 0

    def get_number_of_sources(self):
        """
        Return the number of sources currently in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return 0

    def get_number_of_citations(self):
        """
        Return the number of citations currently in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return 0

    def get_number_of_tags(self):
        """
        Return the number of tags currently in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return 0

    def get_media_from_gramps_id(self, val):
        """
        Find a Media in the database from the passed Gramps ID.

        If no such Media exists, None is returned.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("gramps_id %s does not exist in the dummy database", val)
        return None

    def get_media_from_handle(self, handle):
        """
        Find an Object in the database from the passed Gramps ID.

        If no such Object exists, a HandleError is raised.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_person_attribute_types(self):
        """
        Return a list of all Attribute types associated with Person instances
        in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_person_cursor(self):
        """
        Return a reference to a cursor over Person objects
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_person_event_types(self):
        """
        Deprecated:  Use get_event_types
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_person_from_gramps_id(self, val):
        """
        Find a Person in the database from the passed Gramps ID.

        If no such Person exists, None is returned.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("gramps_id %s does not exist in the dummy database", val)
        return None

    def get_person_from_handle(self, handle):
        """
        Find a Person in the database from the passed Gramps ID.

        If no such Person exists, a HandleError is raised.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_person_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Person in
        the database.

        :param sort_handles: If True, the list is sorted by surnames.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_source_attribute_types(self):
        """
        Return a list of all Attribute types associated with Source/Citation
        instances in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_place_bookmarks(self):
        """
        Return the list of Place handles in the bookmarks.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return self.place_bookmarks

    def get_place_cursor(self):
        """
        Return a reference to a cursor over Place objects
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_place_from_gramps_id(self, val):
        """
        Find a Place in the database from the passed Gramps ID.

        If no such Place exists, None is returned.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("gramps_id %s does not exist in the dummy database", val)
        return None

    def get_place_from_handle(self, handle):
        """
        Find a Place in the database from the passed Gramps ID.

        If no such Place exists, a HandleError is raised.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_place_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Place in
        the database.

        :param sort_handles: If True, the list is sorted by Place title.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_raw_event_data(self, handle):
        """
        Return raw (serialized and pickled) Event object from handle
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_raw_family_data(self, handle):
        """
        Return raw (serialized and pickled) Family object from handle
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_raw_note_data(self, handle):
        """
        Return raw (serialized and pickled) Note object from handle
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_raw_media_data(self, handle):
        """
        Return raw (serialized and pickled) Family object from handle
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_raw_person_data(self, handle):
        """
        Return raw (serialized and pickled) Person object from handle
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_raw_place_data(self, handle):
        """
        Return raw (serialized and pickled) Place object from handle
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_raw_repository_data(self, handle):
        """
        Return raw (serialized and pickled) Repository object from handle
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_raw_source_data(self, handle):
        """
        Return raw (serialized and pickled) Source object from handle
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_raw_citation_data(self, handle):
        """
        Return raw (serialized and pickled) Citation object from handle
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_raw_tag_data(self, handle):
        """
        Return raw (serialized and pickled) Tag object from handle
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_repo_bookmarks(self):
        """
        Return the list of Repository handles in the bookmarks.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return self.repo_bookmarks

    def get_repository_cursor(self):
        """
        Return a reference to a cursor over Repository objects
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_repository_from_gramps_id(self, val):
        """
        Find a Repository in the database from the passed Gramps ID.

        If no such Repository exists, None is returned.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("gramps_id %s does not exist in the dummy database", val)
        return None

    def get_repository_from_handle(self, handle):
        """
        Find a Repository in the database from the passed Gramps ID.

        If no such Repository exists, a HandleError is raised.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_repository_handles(self):
        """
        Return a list of database handles, one handle for each Repository in
        the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_repository_types(self):
        """
        Return a list of all custom repository types associated with Repository
        instances in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_researcher(self):
        """
        Return the Researcher instance, providing information about the owner
        of the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return self.owner

    def get_save_path(self):
        """
        Return the save path of the file, or "" if one does not exist.
        """
        return ""

    def get_source_bookmarks(self):
        """
        Return the list of Source handles in the bookmarks.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return self.source_bookmarks

    def get_source_cursor(self):
        """
        Return a reference to a cursor over Source objects
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_source_from_gramps_id(self, val):
        """
        Find a Source in the database from the passed Gramps ID.

        If no such Source exists, None is returned.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("gramps_id %s does not exist in the dummy database", val)
        return None

    def get_source_from_handle(self, handle):
        """
        Find a Source in the database from the passed Gramps ID.

        If no such Source exists, a HandleError is raised.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_source_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Source in
        the database.

        :param sort_handles: If True, the list is sorted by Source title.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_source_media_types(self):
        """
        Return a list of all custom source media types associated with Source
        instances in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_citation_bookmarks(self):
        """
        Return the list of Citation handles in the bookmarks.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return self.citation_bookmarks

    def get_citation_cursor(self):
        """
        Return a reference to a cursor over Citation objects
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_citation_from_gramps_id(self, val):
        """
        Find a Citation in the database from the passed Gramps ID.

        If no such Citation exists, None is returned.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("gramps_id %s does not exist in the dummy database", val)
        return None

    def get_citation_from_handle(self, handle):
        """
        Find a Citation in the database from the passed Gramps ID.

        If no such Citation exists, a HandleError is raised.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_citation_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Citation in
        the database.

        :param sort_handles: If True, the list is sorted by Citation title.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_surname_list(self):
        """
        Return the list of locale-sorted surnames contained in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_tag_cursor(self):
        """
        Return a reference to a cursor over Tag objects
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_tag_from_handle(self, handle):
        """
        Find a Tag in the database from the passed handle.

        If no such Tag exists, a HandleError is raised.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("handle %s does not exist in the dummy database", handle)
        raise HandleError("Handle %s not found" % handle)

    def get_tag_from_name(self, val):
        """
        Find a Tag in the database from the passed Tag name.

        If no such Tag exists, None is returned.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("tag name %s does not exist in the dummy database", val)
        return None

    def get_tag_handles(self, sort_handles=False, locale=glocale):
        """
        Return a list of database handles, one handle for each Tag in
        the database.

        :param sort_handles: If True, the list is sorted by Tag name.
        :type sort_handles: bool
        :param locale: The locale to use for collation.
        :type locale: A GrampsLocale object.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_url_types(self):
        """
        Return a list of all custom names types associated with Url instances
        in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def get_place_types(self):
        """
        Return a list of all custom place types associated with Place instances
        in the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def has_event_handle(self, handle):
        """
        Return True if the handle exists in the current Event database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return False

    def has_family_handle(self, handle):
        """
        Return True if the handle exists in the current Family database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return False

    def has_name_group_key(self, name):
        """
        Return if a key exists in the name_group table.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return False

    def has_note_handle(self, handle):
        """
        Return True if the handle exists in the current Note database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return False

    def has_media_handle(self, handle):
        """
        Return True if the handle exists in the current Mediadatabase.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return False

    def has_person_handle(self, handle):
        """
        Return True if the handle exists in the current Person database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return False

    def has_place_handle(self, handle):
        """
        Return True if the handle exists in the current Place database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return False

    def has_repository_handle(self, handle):
        """
        Return True if the handle exists in the current Repository database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return False

    def has_source_handle(self, handle):
        """
        Return True if the handle exists in the current Source database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return False

    def has_tag_handle(self, handle):
        """
        Return True if the handle exists in the current Tag database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return False

    def is_open(self):
        """
        Return True if the database has been opened.
        """
        return self.db_is_open

    def iter_citations(self):
        """
        Return an iterator over objects for Citations in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_event_handles(self):
        """
        Return an iterator over handles for Events in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_events(self):
        """
        Return an iterator over objects for Events in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_families(self):
        """
        Return an iterator over objects for Families in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_family_handles(self):
        """
        Return an iterator over handles for Families in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_media_handles(self):
        """
        Return an iterator over handles for Media in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_media(self):
        """
        Return an iterator over objects for Medias in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_note_handles(self):
        """
        Return an iterator over handles for Notes in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_notes(self):
        """
        Return an iterator over objects for Notes in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_people(self):
        """
        Return an iterator over objects for Persons in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_person_handles(self):
        """
        Return an iterator over handles for Persons in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_place_handles(self):
        """
        Return an iterator over handles for Places in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_places(self):
        """
        Return an iterator over objects for Places in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_repositories(self):
        """
        Return an iterator over objects for Repositories in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_repository_handles(self):
        """
        Return an iterator over handles for Repositories in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_source_handles(self):
        """
        Return an iterator over handles for Sources in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_sources(self):
        """
        Return an iterator over objects for Sources in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_tag_handles(self):
        """
        Return an iterator over handles for Tags in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def iter_tags(self):
        """
        Return an iterator over objects for Tags in the database
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return []

    def load(
        self,
        name,
        callback=None,
        mode=None,
        force_schema_upgrade=False,
        force_bsddb_upgrade=False,
        force_bsddb_downgrade=False,
        force_python_upgrade=False,
        update=True,
    ):
        """
        Open the specified database.
        """
        self.db_is_open = True

    def report_bm_change(self):
        """
        Add 1 to the number of bookmark changes during this session.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("database is readonly")

    def request_rebuild(self):
        """
        Notify clients that the data has changed significantly, and that all
        internal data dependent on the database should be rebuilt.
        Note that all rebuild signals on all objects are emitted at the same
        time. It is correct to assume that this is always the case.

        .. todo:: it might be better to replace these rebuild signals by one
                  single database-rebuild signal.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        LOG.warning("database is readonly")

    def version_supported(self):
        """
        Return True when the file has a supported version.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")
        return True

    def set_event_id_prefix(self, val):
        """
        Set the naming template for Gramps Event ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as E%d or E%04d.
        """
        LOG.warning("database is readonly")

    def set_family_id_prefix(self, val):
        """
        Set the naming template for Gramps Family ID values. The string is
        expected to be in the form of a simple text string, or in a format
        that contains a C/Python style format string using %d, such as F%d
        or F%04d.
        """
        LOG.warning("database is readonly")

    def set_note_id_prefix(self, val):
        """
        Set the naming template for Gramps Note ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as N%d or N%04d.
        """
        LOG.warning("database is readonly")

    def set_media_id_prefix(self, val):
        """
        Set the naming template for Gramps Media ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as O%d or O%04d.
        """
        LOG.warning("database is readonly")

    def set_person_id_prefix(self, val):
        """
        Set the naming template for Gramps Person ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as I%d or I%04d.
        """
        LOG.warning("database is readonly")

    def set_place_id_prefix(self, val):
        """
        Set the naming template for Gramps Place ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as P%d or P%04d.
        """
        LOG.warning("database is readonly")

    def set_prefixes(
        self, person, media, family, source, citation, place, event, repository, note
    ):
        """
        Set the prefixes for the gramps ids for all gramps objects
        """
        LOG.warning("database is readonly")

    def set_repository_id_prefix(self, val):
        """
        Set the naming template for Gramps Repository ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as R%d or R%04d.
        """
        LOG.warning("database is readonly")

    def set_source_id_prefix(self, val):
        """
        Set the naming template for Gramps Source ID values.

        The string is expected to be in the form of a simple text string, or
        in a format that contains a C/Python style format string using %d,
        such as S%d or S%04d.
        """
        LOG.warning("database is readonly")

    def set_mediapath(self, path):
        """
        Set the default media path for database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")

    def set_researcher(self, owner):
        """
        Set the information about the owner of the database.
        """
        if not self.db_is_open:
            LOG.debug("database is closed")

    def get_dbid(self):
        """
        A unique ID for this database on this computer.
        """
        return ""

    def get_dbname(self):
        """
        A name for this database on this computer.
        """
        return ""
