#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Donald N. Allingham
# Copyright (C) 2010       Jakim Friant
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
Provide a simplified database access interface to the Gramps database.
"""
from ..lib import (Person, Family, Event, Source, Place, Citation,
                   Media, Repository, Note, Date, Tag)
from ..errors import HandleError
from ..datehandler import displayer
from ..utils.string import gender as gender_map
from ..utils.db import get_birth_or_fallback, get_death_or_fallback

from ..display.name import displayer as name_displayer
from ..display.place import displayer as place_displayer
from ..lib import EventType
from ..config import config
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Local functions
#
#-------------------------------------------------------------------------
class SimpleAccess:
    """
    Provide a simplified database access system. This system has been designed
    to ease the development of reports.

    The user needs to take care when using this interface. Since it returns real
    objects instead of database references, it can consume a significant amount
    of memory if the user is not careful.

    **Example**

    A typical system of usage would be::

      sa = SimpleAccess(database)

      print "Person        : ", sa.name(person)
      print "Gender        : ", sa.gender(person)
      print "Birth date    : ", sa.birth_date(person)
      print "Birth place   : ", sa.birth_place(person)
      print "Death date    : ", sa.death_date(person)
      print "Death place   : ", sa.death_place(person)
      print "Father        : ", sa.name(sa.father(person))
      print "Mother        : ", sa.name(sa.mother(person))
      print "Spouse        : ", sa.name(sa.spouse(person))
      print "Marriage Type : ", sa.marriage_type(person)
      print "Marriage Date : ", sa.marriage_date(person)
      print "Marriage Place: ", sa.marriage_place(person)
      for child in sa.children(person):
         print "Child         : ", sa.name(child)

      # Print out burial and baptism events
      for event in sa.events( person , [ "Burial", "Baptism" ]):
         print "Event         : ", sa.event_type(event), sa.event_date(event),
         print sa.event_place(event)

    This would produce an output that looks like::

         Person        :  Garner, Lewis Anderson
         Gender        :  male
         Birth date    :  6/21/1855
         Birth place   :  Great Falls, MT
         Death date    :  6/28/1911
         Death place   :  Twin Falls, ID
         Father        :  Garner, Robert W.
         Mother        :  Zielinski, Phoebe Emily
         Spouse        :  Martel, Luella Jacques
         Marriage Type :  Married
         Marriage Date :  4/1/1875
         Marriage Place:  Paragould, AR
         Child         :  Garner, Eugene Stanley
         Child         :  Garner, Jesse V.
         Child         :  Garner, Raymond E.
         Child         :  Garner, Jennie S.
         Child         :  Garner, Walter E.
         Child         :  Garner, Daniel Webster
         Child         :  Garner, Bertha P.
         Child         :  Garner, Elizabeth
         Event         :  Burial 7/1/1911 Twin Falls, ID

    One can also alternatively supply a handle rather than a person.
    """

    def __init__(self, dbase):
        """
        Initialize the SimpleAccess object with the database that will be used.

        :param dbase: Gramps database object
        :type dbase: DbBase
        """
        self.dbase = dbase

    def name(self, person):
        """
        Return the name of the person, or and empty string if the person is None

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns the name of the person based of the program preferences
        :rtype: unicode
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        assert(person is None or isinstance(person, Person))
        if person:
            return name_displayer.display(person)
        else:
            return ''

    def surname(self, person):
        """
        Return the name of the person, or and empty string if the person is None

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns the name of the person based of the program preferences
        :rtype: unicode
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        assert(person is None or isinstance(person, Person))
        if person:
            surname = person.get_primary_name().get_surname()
            return surname or config.get('preferences.no-surname-text')
        else:
            return ''

    def first_name(self, person):
        """
        Return the first name of the person, or and empty string if the person
        is None

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns the first name of the person based of the program
                 preferences
        :rtype: unicode
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        assert(person is None or isinstance(person, Person))
        if person:
            return person.get_primary_name().get_first_name()
        else:
            return ''

    def gid(self, obj):
        """
        Return the Gramps ID of the person or family

        :param obj: Person or Family object
        :type obj: :py:class:`.Person` or :py:class:`.Family`
        :return: Returns the Gramps ID value of the person or family
        :rtype: unicode
        """
        if obj:
            return obj.get_gramps_id()
        else:
            return ''

    def gender(self, person):
        """
        Return a string representing the gender of the person

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns a string indentifying the person's gender
        :rtype: unicode
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        assert(person is None or isinstance(person, Person))
        if person:
            return gender_map[person.get_gender()]
        return ''

    def __parent(self, person, func):
        """
        Return a person associated as a parent of the person

        :param person: Person object
        :type person: :py:class:`.Person`
        :param func: function used to extract the appropriate parent
        :type func: function
        :return: mother or father of the associated person
        :rtype: :py:class:`.Person`
        """
        assert(person is None or isinstance(person, Person))

        if person:
            parent_handle_list = person.get_parent_family_handle_list()
            if parent_handle_list:
                family_id = parent_handle_list[0]
                family = self.dbase.get_family_from_handle(family_id)
                return self.__family_parent(family, func)
        return None

    def __family_parent(self, family, func):
        """
        Return a person associated as a parent of the family

        :param family: Family object
        :type family: :py:class:`.Family`
        :param func: function used to extract the appropriate parent
        :type func: function
        :return: mother or father of the associated family
        :rtype: :py:class:`.Family`
        """
        assert(family is None or isinstance(family, Family))

        if family:
            handle = func(family)
            if handle:
                return self.dbase.get_person_from_handle(handle)
        return None

    def __event_date(self, person, func):
        """
        Return a string describing the date associated with the person

        :param person: Person object
        :type person: :py:class:`.Person`
        :param func: function used to extract the associated date information
        :type func: function
        :return: Returns a string describing the date
        :rtype: unicode
        """
        assert(person is None or isinstance(person, Person))

        if person:
            ref = func(person)
            if ref:
                event_handle = ref.get_reference_handle()
                if event_handle:
                    event = self.dbase.get_event_from_handle(event_handle)
                    date_obj = event.get_date_object()
                    if date_obj:
                        return displayer.display(date_obj)
        return ''

    def __event_date_obj(self, person, func):
        """
        Return the date associated with the person

        :param person: Person object
        :type person: :py:class:`.Person`
        :param func: function used to extract the associated date information
        :type func: function
        :return: Returns the date
        :rtype: l{gen.lib.Date}
        """
        assert(person is None or isinstance(person, Person))

        if person:
            ref = func(person)
            if ref:
                event_handle = ref.get_reference_handle()
                if event_handle:
                    event = self.dbase.get_event_from_handle(event_handle)
                    date_obj = event.get_date_object()
                    if date_obj:
                        return date_obj
                    else:
                        return Date()
        return Date()

    def __event_place(self, person, func):
        """
        Return a string describing the place associated with the person

        :param person: Person object
        :type person: :py:class:`.Person`
        :param func: function used to extract the associated place information
        :type func: function
        :return: Returns a string describing the place
        :rtype: unicode
        """
        assert(person is None or isinstance(person, Person))

        if person:
            ref = func(person)
            if ref:
                event_handle = ref.get_reference_handle()
                if event_handle:
                    event = self.dbase.get_event_from_handle(event_handle)
                    return place_displayer.display_event(self.dbase, event)
        return ''

    def spouse(self, person):
        """
        Return the primary spouse of the person

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: The spouse identified as the person's primary spouse
        :rtype: :py:class:`.Person`
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        assert(person is None or isinstance(person, Person))

        if person:
            family_handle_list = person.get_family_handle_list()
            if family_handle_list:
                family_id = family_handle_list[0]
                family = self.dbase.get_family_from_handle(family_id)
                if family.get_father_handle() == person.get_handle():
                    person_handle = family.get_mother_handle()
                else:
                    person_handle = family.get_father_handle()
                if person_handle:
                    return self.dbase.get_person_from_handle(person_handle)
        return None

    def marriage_type(self, person):
        """
        Return a string describing the relationship between the person and
        his/per primary spouse.

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns a string describing the relationship between the
                 person and his/per primary spouse.
        :rtype: unicode
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        assert(person is None or isinstance(person, Person))

        if person:
            family_handle_list = person.get_family_handle_list()
            if family_handle_list:
                family_id = family_handle_list[0]
                family = self.dbase.get_family_from_handle(family_id)
                if family:
                    return str(family.get_relationship())
        return ''

    def marriage_place(self, person):
        """
        Return a string describing the place where the person and his/her spouse
        where married.

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns a string describing the place where the person and
                 his/her spouse where married.
        :rtype: unicode
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        assert(person is None or isinstance(person, Person))

        if person:
            family_handle_list = person.get_family_handle_list()
            if family_handle_list:
                family_id = family_handle_list[0]
                family = self.dbase.get_family_from_handle(family_id)
                if family:
                    reflist = family.get_event_ref_list()
                    if reflist:
                        # 'evnt' should be renamed to 'event'?
                        elist = [ self.dbase.get_event_from_handle(ref.ref)
                                  for ref in reflist ]
                        events = [ evnt for evnt in elist
                                   if evnt.type == EventType.MARRIAGE ]
                        if events:
                            return place_displayer.display_event(self.dbase, events[0])
        return ''

    def marriage_date(self, person):
        """
        Return a string indicating the date when the person and his/her spouse
        where married.

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns a string indicicating the date when the person and
                 his/her spouse where married.
        :rtype: unicode
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        assert(person is None or isinstance(person, Person))

        if person:
            family_handle_list = person.get_family_handle_list()
            if family_handle_list:
                family_id = family_handle_list[0]
                family = self.dbase.get_family_from_handle(family_id)
                if family:
                    reflist = family.get_event_ref_list()
                    if reflist:
                        elist = [ self.dbase.get_event_from_handle(ref.ref)
                                  for ref in reflist ]
                        events = [ evnt for evnt in elist
                                   if evnt.type == EventType.MARRIAGE ]
                        if events:
                            date_obj = events[0].get_date_object()
                            if date_obj:
                                return displayer.display(date_obj)
        return ''

    def children(self, obj):
        """
        Return a list of the children as the children of the primary spouse.

        :param obj: Person or Family object
        :type obj: :py:class:`.Person` or :py:class:`.Family`
        :return: Returns a list of :py:class:`.Person` objects representing the
                 children
        :rtype: list
        """
        assert(obj is None or isinstance(obj, (Person, Family)))

        if isinstance(obj, Person):
            family_handle_list = obj.get_family_handle_list()
            if family_handle_list:
                family_id = family_handle_list[0]
                family = self.dbase.get_family_from_handle(family_id)

                return [ self.dbase.get_person_from_handle(hndl.ref)
                         for hndl in family.get_child_ref_list() ]
        elif isinstance(obj, Family):
            return [ self.dbase.get_person_from_handle(hndl.ref)
                     for hndl in obj.get_child_ref_list() ]
        return []

    def father(self, obj):
        """
        Return the primary father of the person or the father of the associated
        family.

        :param obj: Person or Family object
        :type obj: :py:class:`.Person` or :py:class:`.Family`
        :return: The father in the person's primary family or the father of the
                 family
        :rtype: :py:class:`.Person`
        """
        if isinstance(obj, Person):
            return self.__parent(obj, Family.get_father_handle)
        elif isinstance(obj, Family):
            return self.__family_parent(obj, Family.get_father_handle)
        else:
            return None

    def mother(self, obj):
        """
        Returns the primary mother of the person or the mother of the associated
        family.

        :param obj: Person object
        :type obj: :py:class:`.Person` or :py:class:`.Family`
        :return: The mother in the person's primary family or the mother of the
                 family
        :rtype: :py:class:`.Person`
        """
        if isinstance(obj, Person):
            return self.__parent(obj, Family.get_mother_handle)
        elif isinstance(obj, Family):
            return self.__family_parent(obj, Family.get_mother_handle)
        else:
            return None

    def birth_date(self, person):
        """
        Return a string indicating the date when the person's birth.

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns a string indicating the date when the person's birth.
        :rtype: unicode
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        return self.__event_date(person, Person.get_birth_ref)

    def birth_date_obj(self, person):
        """
        Return the date when the person's birth.

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns the date when the person's birth.
        :rtype: :py:class:`.Date`
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        return self.__event_date_obj(person, Person.get_birth_ref)


    def birth_or_fallback(self, person, get_event=False):
        """
        Return the date of the person's birth or fallback event.

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns the date when the person's birth or fallback.
        :rtype: :py:class:`.Date`
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        event = get_birth_or_fallback(self.dbase, person, "<i>%s</i>")
        if get_event:
            return event
        elif event:
            return event.date
        else:
            return Date()

    def birth_place(self, person):
        """
        Return a string indicating the place of the person's birth.

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns a string indicating the place of the person's birth.
        :rtype: unicode
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        return self.__event_place(person, Person.get_birth_ref)

    def death_date(self, person):
        """
        Return a string indicating the date when the person's death.

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns a string indicating the date when the person's death.
        :rtype: unicode
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        return self.__event_date(person, Person.get_death_ref)

    def death_date_obj(self, person):
        """
        Return the date when the person's death.

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns the date when the person's death.
        :rtype: :py:class:`.Date`
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        return self.__event_date_obj(person, Person.get_death_ref)

    def death_or_fallback(self, person, get_event=False):
        """
        Return the date of the person's death or fallback event.

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns the date of the person's death or fallback.
        :rtype: :py:class:`.Date`
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        event = get_death_or_fallback(self.dbase, person, "<i>%s</i>")
        if get_event:
            return event
        elif event:
            return event.date
        else:
            return Date()

    def death_place(self, person):
        """
        Return a string indicating the place of the person's death.

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: Returns a string indicating the place of the person's death.
        :rtype: unicode
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        return self.__event_place(person, Person.get_death_ref)

    def event_place(self, event):
        """
        Return a string indicating the place of the event

        :param event: Event object
        :type event: :py:class:`.Event`
        :return: Returns a string indicating the place of the event
        :rtype: unicode
        """
        assert(event is None or isinstance(event, Event))

        if event:
            return place_displayer.display_event(self.dbase, event)
        else:
            return ''

    def date_string(self, date_obj):
        """
        Return a string representation a date_obj

        :param date_obj: Date object
        :type date_obj: :py:class:`.Date`
        :return: Returns a string representation a date_obj
        :rtype: unicode
        """
        if date_obj:
            return displayer.display(date_obj)
        else:
            return ''

    def event_date(self, event):
        """
        Return a string indicating the date of the event

        :param event: Event object
        :type event: :py:class:`.Event`
        :return: Returns a string indicating the date of the event
        :rtype: unicode
        """
        assert(event is None or isinstance(event, Event))
        date_obj = event.get_date_object()
        if date_obj:
            return displayer.display(date_obj)
        else:
            return ''

    def event_date_obj(self, event):
        """
        Return a string indicating the date of the event

        :param event: Event object
        :type event: :py:class:`.Event`
        :return: Returns a string indicating the date of the event
        :rtype: unicode
        """
        assert(event is None or isinstance(event, Event))
        if event:
            return event.get_date_object()

    def event_type(self, event):
        """
        Return a string indicating the type of the event

        :param event: Event object
        :type event: :py:class:`.Event`
        :return: Returns a string indicating the type of the event
        :rtype: unicode
        """
        assert(event is None or isinstance(event, Event))
        if event:
            return str(event.get_type())
        else:
            return ''

    def events(self, obj, restrict=None):
        """
        Return a list of events associated with the object. This object
        can be either a :py:class:`.Person` or :py:class:`.Family`.

        :param obj: Person or Family
        :type obj: :py:class:`.Person` or :py:class:`.Family`
        :param restrict: Optional list of strings that will limit the types
                         of events to those of the specified types.
        :type restrict: list
        :return: list of events associated with the object
        :rtype: list
        """
        assert(obj is None or isinstance(obj, (Person, Family)))
        assert(isinstance(restrict, list) or restrict is None)

        if obj:
            event_handles = [ ref.ref for ref in obj.get_event_ref_list() ]
            events = [ self.dbase.get_event_from_handle(h)
                       for h in event_handles ]
            if restrict:
                restrict = [ r.lower() for r in restrict ]
                events = [ event for event in events
                           if str(event.get_type()).lower() in restrict ]
            return events
        else:
            return []

    def sources(self, obj):
        """
        Return a list of events associated with the object. This object
        can be either a :py:class:`.Person` or :py:class:`.Family`.

        :param obj: Person or Family
        :type obj: :py:class:`.Person` or :py:class:`.Family`
        :return: list of events associated with the object
        :rtype: list
        """
        assert(obj is None or isinstance(obj, (Person, Family, Event)))

        if obj:
            handles = [ ref.ref for ref in obj.get_source_references() ]
            return list(map(self.dbase.get_source_from_handle, handles))
        else:
            return []

    def parent_in(self, person):
        """
        Return a list of families in which the person is listed as a parent.

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: list of :py:class:`.Family` objects in which the person is
                 listed as a parent.
        :rtype: list
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        assert(person is None or isinstance(person, Person))

        if person:
            return [ self.dbase.get_family_from_handle(handle)
                     for handle in person.get_family_handle_list() ]
        return []

    def child_in(self, person):
        """
        Return a list of families in which the person is listed as a child.

        :param person: Person object
        :type person: :py:class:`.Person`
        :return: list of :py:class:`.Family` objects in which the person is
                 listed as a child.
        :rtype: list
        """
        if isinstance(person, str):
            person = self.dbase.get_person_from_handle(person)
        assert(person is None or isinstance(person, Person))

        if person:
            return [ self.dbase.get_family_from_handle(handle)
                     for handle in person.get_parent_family_handle_list() ]
        return []

    def __all_objects(self, gen_cursor, get_object):
        """
        Return a all the objects of a particular type in the database, one
        at a time as an iterator. The user can treat this just like a list.

        :return: list of objects of a particular type in the database
        :rtype: list
        """

        with gen_cursor() as cursor:
            for key, data in cursor:
                yield get_object(key)

    def all_people(self):
        """
        Return a all the people in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

           for person in sa.all_people():
              sa.print(person)

        :return: list of people in the database
        :rtype: list
        """

        with self.dbase.get_person_cursor() as cursor:
            # data[3] is primary_name; data[3][5][0][0] is surname
            slist = sorted((data[3][5][0][0] if data[3][5] else '', key)
                           for key, data in cursor)

        for info in slist:
            obj = self.dbase.get_person_from_handle(info[1])
            yield obj

    def all_families(self):
        """
        Return all the families in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

           for person in sa.all_families():
              sa.print(sa.father(person))

        :return: list of families in the database
        :rtype: list
        """
        return self.__all_objects(self.dbase.get_family_cursor,
                                  self.dbase.get_family_from_handle)

    def all_events(self):
        """
        Return all the events in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

           for person in sa.all_events():
              sa.print(sa.event_place(event))

        :return: list of events in the database
        :rtype: list
        """
        return self.__all_objects(self.dbase.get_event_cursor,
                                  self.dbase.get_event_from_handle)

    def all_sources(self):
        """
        Return all the sources in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

        :return: list of sources in the database
        :rtype: list
        """
        return self.__all_objects(self.dbase.get_source_cursor,
                                  self.dbase.get_source_from_handle)

    def all_citations(self):
        """
        Return all the citations in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

        :return: list of citations in the database
        :rtype: list
        """
        return self.__all_objects(self.dbase.get_citation_cursor,
                                  self.dbase.get_citation_from_handle)

    def all_repositories(self):
        """
        Return all the repositories in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

        :return: list of repositories in the database
        :rtype: list
        """
        return self.__all_objects(self.dbase.get_repository_cursor,
                                  self.dbase.get_repository_from_handle)

    def all_media(self):
        """
        Return all the media in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

        :return: list of media in the database
        :rtype: list
        """
        return self.__all_objects(self.dbase.get_media_cursor,
                                  self.dbase.get_media_from_handle)

    def all_places(self):
        """
        Return all the places in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

        :return: list of places in the database
        :rtype: list
        """
        return self.__all_objects(self.dbase.get_place_cursor,
                                  self.dbase.get_place_from_handle)

    def all_notes(self):
        """
        Return all the notes in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

        :return: list of notes in the database
        :rtype: list
        """
        return self.__all_objects(self.dbase.get_note_cursor,
                                  self.dbase.get_note_from_handle)

    def all_tags(self):
        """
        Return all the tags in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

        :return: list of tags in the database
        :rtype: list
        """
        return self.__all_objects(self.dbase.get_tag_cursor,
                                  self.dbase.get_tag_from_handle)

    def title(self, source):
        """
        Return the title of the source.

        :param source: Source object
        :type source: :py:class:`.Source`
        :return: title of the source
        :rtype: unicode
        """
        assert(source is None or isinstance(source, Source))
        if source:
            return source.get_title()
        return ''

    def page(self, citation):
        """
        Return the page of the citation.

        :param citation: Source object
        :type citation: :py:class:`Citation <.lib.citation.Citation>`
        :return: title of the citation
        :rtype: unicode
        """
        assert(citation is None or isinstance(citation, Citation))
        if citation:
            return citation.get_page()
        return ''

    def author(self, source):
        """
        Return the author of the source.

        :param source: Source object
        :type source: :py:class:`.Source`
        :return: author of the source
        :rtype: unicode
        """
        assert(source is None or isinstance(source, Source))
        if source:
            return source.get_author()
        return ''

    def person(self, handle):
        assert(isinstance(handle, str))
        return self.dbase.get_person_from_handle(handle)

    def event(self, handle):
        assert(isinstance(handle, str))
        return self.dbase.get_event_from_handle(handle)

    def family(self, handle):
        assert(isinstance(handle, str))
        return self.dbase.get_family_from_handle(handle)

    def display(self, object_class, prop, value):
        """
        Given a object_class, prop, and value return a display string
        describing object.

        :param object_class: "Person", "Source", etc.
        :param prop: "gramps_id", or "handle"
        :param value: gramps_id or handle.
        """
        func = self.dbase.method('get_%s_from_%s', object_class, prop)
        if func:
            try:
                obj = func(value)
            except HandleError:
                # Deals with deleted objects referenced in Note Links
                obj = None
            if obj:
                if isinstance(obj, Person):
                    return "%s: %s [%s]" % (_(object_class),
                                            self.name(obj),
                                            self.gid(obj))
                elif isinstance(obj, Event):
                    return "%s: %s [%s]" % (_(object_class),
                                            self.event_type(obj),
                                            self.gid(obj))
                elif isinstance(obj, Family):
                    return "%s: %s/%s [%s]" % (_(object_class),
                                            self.name(self.mother(obj)),
                                            self.name(self.father(obj)),
                                            self.gid(obj))
                elif isinstance(obj, Media):
                    return "%s: %s [%s]" % (_(object_class),
                                            obj.desc,
                                            self.gid(obj))
                elif isinstance(obj, Source):
                    return "%s: %s [%s]" % (_(object_class),
                                            self.title(obj),
                                            self.gid(obj))
                elif isinstance(obj, Citation):
                    return "%s: [%s]" % (_(object_class),
                                            self.gid(obj))
                elif isinstance(obj, Place):
                    place_title = place_displayer.display(self.dbase, obj)
                    return "%s: %s [%s]" % (_(object_class),
                                            place_title,
                                            self.gid(obj))
                elif isinstance(obj, Repository):
                    return "%s: %s [%s]" % (_(object_class),
                                            obj.type,
                                            self.gid(obj))
                elif isinstance(obj, Note):
                    return "%s: %s [%s]" % (_(object_class),
                                            obj.type,
                                            self.gid(obj))
                elif isinstance(obj, Tag):
                    return "%s: [%s]" % (_(object_class),
                                         obj.name)
                else:
                    return "Error: incorrect object class in display: '%s'" % type(obj)
            else:
                return "Error: missing object"
        else:
            return "Error: invalid object class in display: '%s'" % object_class

    def describe(self, obj, prop=None, value=None):
        """
        Given a object, return a string describing the object.
        """
        if prop and value:
            func = self.dbase.method('get_%s_from_%s', object_class, prop)
            if func:
                obj = func(value)
        if isinstance(obj, Person):
            return "%s [%s]" % (self.name(obj),
                                self.gid(obj))
        elif isinstance(obj, Event):
            return "%s [%s]" % (self.event_type(obj),
                                self.gid(obj))
        elif isinstance(obj, Family):
            return "%s/%s [%s]" % (self.name(self.mother(obj)),
                                   self.name(self.father(obj)),
                                   self.gid(obj))
        elif isinstance(obj, Media):
            return "%s [%s]" % (obj.desc,
                                self.gid(obj))
        elif isinstance(obj, Source):
            return "%s [%s]" % (self.title(obj),
                                self.gid(obj))
        elif isinstance(obj, Citation):
            return "[%s]" % (self.gid(obj))
        elif isinstance(obj, Place):
            place_title = place_displayer.display(self.dbase, obj)
            return "%s [%s]" % (place_title,
                                self.gid(obj))
        elif isinstance(obj, Repository):
            return "%s [%s]" % (obj.type,
                                self.gid(obj))
        elif isinstance(obj, Note):
            return "%s [%s]" % (obj.type,
                                self.gid(obj))
        elif isinstance(obj, Tag):
            return "[%s]" % (obj.name)
        else:
            return "Error: incorrect object class in describe: '%s'" % type(obj)

    def get_link(self, object_class, prop, value):
        """
        Given a object_class, prop, and value return the object.

        :param object_class: "Person", "Source", etc.
        :param prop: "gramps_id", or "handle"
        :param value: gramps_id or handle.
        """
        func = self.dbase.method('get_%s_from_%s', object_class, prop)
        if func:
            return func(value)
