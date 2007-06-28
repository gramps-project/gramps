#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
Provides a simplified database access interface to the GRAMPS database.
"""

from types import NoneType

import RelLib
import DateHandler
import Utils

from BasicUtils import name_displayer
from ReportBase import ReportUtils
from RelLib import EventType

class SimpleAccess:
    """
    Provides a simplified database access system. This system has been designed to
    ease the development of reports. 
    
    The user needs to take care when using this interface. Since it returns real 
    objects instead of database references, it can consume a significant amount
    of memory if the user is not careful.
    
    Example
    =======
    
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
    """

    def __init__(self, dbase):
        """
        Initializes the SimpleAccess object with the database that will be used.
        
        @param dbase: GRAMPS database object
        @type dbase: GrampsDbBase
        """
        self.dbase = dbase

    def name(self, person):
        """
        Returns the name of the person, or and empty string if the person is None

        @param person: Person object
        @type person: L{RelLib.Person}
        @return: Returns the name of the person based of the program preferences
        @rtype: unicode
        """
        assert(isinstance(person, (RelLib.Person, NoneType)))
        if person:
            return name_displayer.display(person)
        else:
            return u''

    def surname(self, person):
        """
        Returns the name of the person, or and empty string if the person is None

        @param person: Person object
        @type person: L{RelLib.Person}
        @return: Returns the name of the person based of the program preferences
        @rtype: unicode
        """
        assert(isinstance(person, (RelLib.Person, NoneType)))
        if person:
            return person.get_primary_name().get_surname()
        else:
            return u''

    def gid(self, obj):
        """
        Returns the GRAMPS ID of the person or family

        @param obj: Person or Family object
        @type obj: L{RelLib.Person} or L{RelLib.Family}
        @return: Returns the GRAMPS Id value of the person or family
        @rtype: unicode
        """
        assert(isinstance(obj, (RelLib.Person, RelLib.Family, NoneType)))
        if obj:
            return obj.get_gramps_id()
        else:
            return u''

    def gender(self, person):
        """
        Returns a string representing the gender of the person

        @param person: Person object
        @type person: L{RelLib.Person}
        @return: Returns a string indentifying the person's gender
        @rtype: unicode
        """
        assert(isinstance(person, (RelLib.Person, NoneType)))
        if person:
            return Utils.gender[person.get_gender()]
        return u''

    def __parent(self, person, func):
        """
        Returns a person associated as a parent of the person

        @param person: Person object
        @type person: L{RelLib.Person}
        @param func: function used to extract the appropriate parent
        @type func: function
        @return: mother or father of the associated person
        @rtype: L{RelLib.Person}
        """
        assert(isinstance(person, (RelLib.Person, NoneType)))

        if person:
            parent_handle_list = person.get_parent_family_handle_list()
            if parent_handle_list:
                family_id = parent_handle_list[0]
                family = self.dbase.get_family_from_handle(family_id)
                return self.__family_parent(family, func)
        return None

    def __family_parent(self, family, func):
        """
        Returns a person associated as a parent of the family

        @param family: Family object
        @type family: L{RelLib.Family}
        @param func: function used to extract the appropriate parent
        @type func: function
        @return: mother or father of the associated family
        @rtype: L{RelLib.Family}
        """
        assert(isinstance(family, (RelLib.Family, NoneType)))

        if family:
            handle = func(family)
            if handle:
                return self.dbase.get_person_from_handle(handle)
        return None

    def __event_date(self, person, func):
        """
        Returns a string describing the date associated with the person

        @param person: Person object
        @type person: L{RelLib.Person}
        @param func: function used to extract the associated date information
        @type func: function
        @return: Returns a string describing the date
        @rtype: unicode
        """
        assert(isinstance(person, (RelLib.Person, NoneType)))

        if person:
            ref = func(person)
            if ref:
                event_handle = ref.get_reference_handle()
                if event_handle:
                    event = self.dbase.get_event_from_handle(event_handle)
                    date_obj = event.get_date_object()
                    if date_obj:
                        return DateHandler.displayer.display(date_obj)
        return u''

    def __event_place(self, person, func):
        """
        Returns a string describing the place associated with the person

        @param person: Person object
        @type person: L{RelLib.Person}
        @param func: function used to extract the associated place information
        @type func: function
        @return: Returns a string describing the place
        @rtype: unicode
        """
        assert(isinstance(person, (RelLib.Person, NoneType)))

        if person:
            ref = func(person)
            if ref:
                event_handle = ref.get_reference_handle()
                if event_handle:
                    event = self.dbase.get_event_from_handle(event_handle)
                    place_handle = event.get_place_handle()
                    return ReportUtils.place_name(self.dbase, place_handle)
        return u''

    def spouse(self, person):
        """
        Returns the primary spouse of the person

        @param person: Person object
        @type person: L{RelLib.Person}
        @return: The spouse identified as the person's primary spouse
        @rtype: L{RelLib.Person}
        """
        assert(isinstance(person, (RelLib.Person, NoneType)))

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
        Returns a string describing the relationship between the person and
        his/per primary spouse.

        @param person: Person object
        @type person: L{RelLib.Person}
        @return: Returns a string describing the relationship between the person and
        his/per primary spouse.
        @rtype: unicode
        """
        assert(isinstance(person, (RelLib.Person, NoneType)))

        if person:
            family_handle_list = person.get_family_handle_list()
            if family_handle_list:
                family_id = family_handle_list[0]
                family = self.dbase.get_family_from_handle(family_id)
                if family:
                    return str(family.get_relationship())
        return u''

    def marriage_place(self, person):
        """
        Returns a string describing the place where the person and his/her spouse
        where married.

        @param person: Person object
        @type person: L{RelLib.Person}
        @return: Returns a string describing the place where the person and his/her spouse
        where married.
        @rtype: unicode
        """
        assert(isinstance(person, (RelLib.Person, NoneType)))

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
                                   if int(evnt.get_type()) == EventType.MARRIAGE ]
                        if events:
                            place_handle = events[0].get_place_handle()
                            return ReportUtils.place_name(self.dbase, place_handle)
        return u''

    def marriage_date(self, person):
        """
        Returns a string indicating the date when the person and his/her spouse
        where married.

        @param person: Person object
        @type person: L{RelLib.Person}
        @return: Returns a string indicicating the date when the person and his/her spouse
        where married.
        @rtype: unicode
        """
        assert(isinstance(person, (RelLib.Person, NoneType)))

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
                                   if int(evnt.get_type()) == EventType.MARRIAGE ]
                        if events:
                            date_obj = events[0].get_date_object()
                            if date_obj:
                                return DateHandler.displayer.display(date_obj)
        return u''

    def children(self, obj):
        """
        Returns a list of the children as the children of the primary spouse.

        @param obj: Person or Family object
        @type obj: L{RelLib.Person} or L{RelLib.Family}
        @return: Returns a list of L{RelLib.Person} objects representing the children
        @rtype: list
        """
        assert(isinstance(obj, (RelLib.Person, RelLib.Family, NoneType)))

        if isinstance(obj, RelLib.Person):
            family_handle_list = obj.get_family_handle_list()
            if family_handle_list:
                family_id = family_handle_list[0]
                family = self.dbase.get_family_from_handle(family_id)
                
                return [ self.dbase.get_person_from_handle(hndl.ref) 
                         for hndl in family.get_child_ref_list() ]
        elif isinstance(obj, RelLib.Family):
            return [ self.dbase.get_person_from_handle(hndl.ref) 
                     for hndl in obj.get_child_ref_list() ]
        return []

    def father(self, obj):
        """
        Returns the primary father of the person or the father of the associated
        family.

        @param obj: Person or Family object
        @type obj: L{RelLib.Person} or L{RelLib.Family}
        @return: The father in the person's primary family or the father of the
                 family
        @rtype: L{RelLib.Person}
        """
        if isinstance(obj, RelLib.Person):
            return self.__parent(obj, RelLib.Family.get_father_handle)
        elif isinstance(obj, RelLib.Family):
            return self.__family_parent(obj, RelLib.Family.get_father_handle)
        else:
            return None

    def mother(self, obj):
        """
        Returns the primary mother of the person or the mother of the associated
        family.

        @param obj: Person object
        @type obj: L{RelLib.Person} or L{RelLib.Family}
        @return: The mother in the person's primary family or the mother of the
                 family
        @rtype: L{RelLib.Person}
        """
        if isinstance(obj, RelLib.Person):
            return self.__parent(obj, RelLib.Family.get_mother_handle)
        elif isinstance(obj, RelLib.Family):
            return self.__family_parent(obj, RelLib.Family.get_mother_handle)
        else:
            return None
        
    def birth_date(self, person):
        """
        Returns a string indicating the date when the person's birth.

        @param person: Person object
        @type person: L{RelLib.Person}
        @return: Returns a string indicating the date when the person's birth.
        @rtype: unicode
        """
        return self.__event_date(person, RelLib.Person.get_birth_ref)

    def birth_place(self, person):
        """
        Returns a string indicating the place of the person's birth.

        @param person: Person object
        @type person: L{RelLib.Person}
        @return: Returns a string indicating the place of the person's birth.
        @rtype: unicode
        """
        return self.__event_place(person, RelLib.Person.get_birth_ref)

    def death_date(self, person):
        """
        Returns a string indicating the date when the person's death.

        @param person: Person object
        @type person: L{RelLib.Person}
        @return: Returns a string indicating the date when the person's death.
        @rtype: unicode
        """
        return self.__event_date(person, RelLib.Person.get_death_ref)

    def death_place(self, person):
        """
        Returns a string indicating the place of the person's death.

        @param person: Person object
        @type person: L{RelLib.Person}
        @return: Returns a string indicating the place of the person's death.
        @rtype: unicode
        """
        return self.__event_place(person, RelLib.Person.get_death_ref)

    def event_place(self, event):
        """
        Returns a string indicating the place of the event

        @param event: Event object
        @type event: L{RelLib.Event}
        @return: Returns a string indicating the place of the event
        @rtype: unicode
        """
        assert(isinstance(event, (RelLib.Event, NoneType)))

        if event:
            place_handle = event.get_place_handle()
            return ReportUtils.place_name(self.dbase, place_handle)
        else:
            return u''

    def event_date(self, event):
        """
        Returns a string indicating the date of the event

        @param event: Event object
        @type event: L{RelLib.Event}
        @return: Returns a string indicating the date of the event
        @rtype: unicode
        """
        assert(isinstance(event, (RelLib.Event, NoneType)))
        date_obj = event.get_date_object()
        if date_obj:
            return DateHandler.displayer.display(date_obj)
        else:
            return u''

    def event_type(self, event):
        """
        Returns a string indicating the type of the event

        @param event: Event object
        @type event: L{RelLib.Event}
        @return: Returns a string indicating the type of the event
        @rtype: unicode
        """
        assert(isinstance(event, (RelLib.Event, NoneType)))
        if event:
            return str(event.get_type())
        else:
            return u''

    def events(self, obj, restrict=None):
        """
        Returns a list of events associated with the object. This object
        can be either a L{RelLib.Person} or L{RelLib.Family}.

        @param obj: Person or Family
        @type obj: L{RelLib.Person} or L{RelLib.Family}
        @param restrict: Optional list of strings that will limit the types
        of events to those of the specfied types.
        @type restrict: list
        @return: list of events assocated with the object
        @rtype: list
        """
        assert(isinstance(obj, (RelLib.Person, RelLib.Family, NoneType)))
        assert(type(restrict) == type([]) or restrict == None)

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
        Returns a list of events associated with the object. This object
        can be either a L{RelLib.Person} or L{RelLib.Family}.

        @param obj: Person or Family
        @type obj: L{RelLib.Person} or L{RelLib.Family}
        @return: list of events assocated with the object
        @rtype: list
        """
        assert(isinstance(obj, (RelLib.Person, RelLib.Family, RelLib.Event, NoneType)))

        if obj:
            handles = [ ref.ref for ref in obj.get_source_references() ]
            return [ self.dbase.get_source_from_handle(h) for h in handles ]
        else:
            return []

    def parent_in(self, person):
        """
        Returns a list of families in which the person is listed as a parent.

        @param person: Person object
        @type person: L{RelLib.Person}
        @return: list of L{RelLib.Family} objects in which the person is listed
           as a parent.
        @rtype: list
        """
        assert(isinstance(person, (RelLib.Person, NoneType)))
        
        if person:
            return [ self.dbase.get_family_from_handle(handle) 
                     for handle in person.get_family_handle_list() ]
        return []

    def child_in(self, person):
        """
        Returns a list of families in which the person is listed as a child.

        @param person: Person object
        @type person: L{RelLib.Person}
        @return: list of L{RelLib.Family} objects in which the person is listed
           as a child.
        @rtype: list
        """
        assert(isinstance(person, (RelLib.Person, NoneType)))
        
        if person:
            return [ self.dbase.get_family_from_handle(handle) 
                     for handle in person.get_parent_family_handle_list() ]
        return []

    def __all_objects(self, gen_cursor, get_object):
        """
        Returns a all the objects of a particular type in the database, one 
        at a time as an iterator. The user can treat this just like a list. 

        @return: list of objects of a particular type in the database
        @rtype: list
        """
        slist = []
        cursor = gen_cursor()
        data = cursor.first()
        while data:
            slist.append(data[0])
            data = cursor.next()
        cursor.close()
        for info in slist:
            obj = get_object(info)
            yield obj

    def all_people(self):
        """
        Returns a all the people in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

           for person in sa.all_people():
              sa.print(person)

        @return: list of people in the database
        @rtype: list
        """
        slist = []
        cursor = self.dbase.get_person_cursor()
        data = cursor.first()
        while data:
            slist.append((data[1][3][3], data[0]))
            data = cursor.next()
        cursor.close()
        slist.sort()
        for info in slist:
            obj = self.dbase.get_person_from_handle(info[1])
            yield obj

    def all_families(self):
        """
        Returns all the families in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

           for person in sa.all_families():
              sa.print(sa.father(person))

        @return: list of families in the database
        @rtype: list
        """
        return self.__all_objects(self.dbase.get_family_cursor, 
                                  self.dbase.get_family_from_handle)

    def all_events(self):
        """
        Returns all the events in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

           for person in sa.all_events():
              sa.print(sa.event_place(event))

        @return: list of events in the database
        @rtype: list
        """
        return self.__all_objects(self.dbase.get_events_cursor, 
                                  self.dbase.get_event_from_handle)

    def all_sources(self):
        """
        Returns all the sources in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

        @return: list of sources in the database
        @rtype: list
        """
        return self.__all_objects(self.dbase.get_source_cursor, 
                                  self.dbase.get_source_from_handle)

    def title(self, source):
        """
        Returns the title of the source.

        @param source: Source object
        @type source: L{RelLib.Source}
        @return: title of the source
        @rtype: unicode
        """
        assert(isinstance(source, (RelLib.Source, NoneType)))
        if source:
            return source.get_title()
        return u''

    def author(self, source):
        """
        Returns the author of the source.

        @param source: Source object
        @type source: L{RelLib.Source}
        @return: author of the source
        @rtype: unicode
        """
        assert(isinstance(source, (RelLib.Source, NoneType)))
        if source:
            return source.get_author()
        return u''

def by_date(event1, event2):
    """
    Sort function that will compare two events by their dates.

    @param event1: first event
    @type event1: L{Event}
    @param event2: second event
    @type event2: L{Event}
    @return: Returns -1 if event1 < event2, 0 if they are equal, and
       1 if they are the same.
    @rtype: int
    """
    return cmp(event1.get_date_object() , event2.get_date_object())
