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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Simple/_SimpleAccess.py
# $Id$
#

"""
Provide a simplified database access interface to the GRAMPS database.
"""
from __future__ import with_statement
from types import NoneType

import gen.lib
import gen.datehandler
import Utils
import gen.utils
from gen.plug.report.utils import place_name

from gen.display.name import displayer as name_displayer
from gen.lib import EventType
import config
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# Local functions
#
#-------------------------------------------------------------------------
class SimpleAccess(object):
    """
    Provide a simplified database access system. This system has been designed to
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

    One can also alternatively supply a handle rather than a person.
    """

    def __init__(self, dbase):
        """
        Initialize the SimpleAccess object with the database that will be used.
        
        @param dbase: GRAMPS database object
        @type dbase: DbBase
        """
        self.dbase = dbase

    def name(self, person):
        """
        Return the name of the person, or and empty string if the person is None

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns the name of the person based of the program preferences
        @rtype: unicode
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        assert(isinstance(person, (gen.lib.Person, NoneType)))
        if person:
            return name_displayer.display(person)
        else:
            return u''

    def surname(self, person):
        """
        Return the name of the person, or and empty string if the person is None

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns the name of the person based of the program preferences
        @rtype: unicode
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        assert(isinstance(person, (gen.lib.Person, NoneType)))
        if person:
            surname = person.get_primary_name().get_surname()
            return surname or config.get('preferences.no-surname-text')
        else:
            return u''
        
    def first_name(self, person):
        """
        Return the first name of the person, or and empty string if the person is None

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns the first name of the person based of the program preferences
        @rtype: unicode
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        assert(isinstance(person, (gen.lib.Person, NoneType)))
        if person:
            return person.get_primary_name().get_first_name()
        else:
            return u''

    def gid(self, obj):
        """
        Return the GRAMPS ID of the person or family

        @param obj: Person or Family object
        @type obj: L{gen.lib.Person} or L{gen.lib.Family}
        @return: Returns the GRAMPS Id value of the person or family
        @rtype: unicode
        """
        if obj:
            return obj.get_gramps_id()
        else:
            return u''

    def gender(self, person):
        """
        Return a string representing the gender of the person

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns a string indentifying the person's gender
        @rtype: unicode
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        assert(isinstance(person, (gen.lib.Person, NoneType)))
        if person:
            return Utils.gender[person.get_gender()]
        return u''

    def __parent(self, person, func):
        """
        Return a person associated as a parent of the person

        @param person: Person object
        @type person: L{gen.lib.Person}
        @param func: function used to extract the appropriate parent
        @type func: function
        @return: mother or father of the associated person
        @rtype: L{gen.lib.Person}
        """
        assert(isinstance(person, (gen.lib.Person, NoneType)))

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

        @param family: Family object
        @type family: L{gen.lib.Family}
        @param func: function used to extract the appropriate parent
        @type func: function
        @return: mother or father of the associated family
        @rtype: L{gen.lib.Family}
        """
        assert(isinstance(family, (gen.lib.Family, NoneType)))

        if family:
            handle = func(family)
            if handle:
                return self.dbase.get_person_from_handle(handle)
        return None

    def __event_date(self, person, func):
        """
        Return a string describing the date associated with the person

        @param person: Person object
        @type person: L{gen.lib.Person}
        @param func: function used to extract the associated date information
        @type func: function
        @return: Returns a string describing the date
        @rtype: unicode
        """
        assert(isinstance(person, (gen.lib.Person, NoneType)))

        if person:
            ref = func(person)
            if ref:
                event_handle = ref.get_reference_handle()
                if event_handle:
                    event = self.dbase.get_event_from_handle(event_handle)
                    date_obj = event.get_date_object()
                    if date_obj:
                        return gen.datehandler.displayer.display(date_obj)
        return u''

    def __event_date_obj(self, person, func):
        """
        Return the date associated with the person

        @param person: Person object
        @type person: L{gen.lib.Person}
        @param func: function used to extract the associated date information
        @type func: function
        @return: Returns the date
        @rtype: l{gen.lib.Date}
        """
        assert(isinstance(person, (gen.lib.Person, NoneType)))

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
                        return gen.lib.Date()
        return gen.lib.Date()

    def __event_place(self, person, func):
        """
        Return a string describing the place associated with the person

        @param person: Person object
        @type person: L{gen.lib.Person}
        @param func: function used to extract the associated place information
        @type func: function
        @return: Returns a string describing the place
        @rtype: unicode
        """
        assert(isinstance(person, (gen.lib.Person, NoneType)))

        if person:
            ref = func(person)
            if ref:
                event_handle = ref.get_reference_handle()
                if event_handle:
                    event = self.dbase.get_event_from_handle(event_handle)
                    place_handle = event.get_place_handle()
                    return place_name(self.dbase, place_handle)
        return u''

    def spouse(self, person):
        """
        Return the primary spouse of the person

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: The spouse identified as the person's primary spouse
        @rtype: L{gen.lib.Person}
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        assert(isinstance(person, (gen.lib.Person, NoneType)))

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

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns a string describing the relationship between the person and
        his/per primary spouse.
        @rtype: unicode
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        assert(isinstance(person, (gen.lib.Person, NoneType)))

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
        Return a string describing the place where the person and his/her spouse
        where married.

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns a string describing the place where the person and his/her spouse
        where married.
        @rtype: unicode
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        assert(isinstance(person, (gen.lib.Person, NoneType)))

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
                                   if event.type == EventType.MARRIAGE ]
                        if events:
                            place_handle = events[0].get_place_handle()
                            return place_name(self.dbase, place_handle)
        return u''

    def marriage_date(self, person):
        """
        Return a string indicating the date when the person and his/her spouse
        where married.

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns a string indicicating the date when the person and his/her spouse
        where married.
        @rtype: unicode
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        assert(isinstance(person, (gen.lib.Person, NoneType)))

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
                                   if event.type == EventType.MARRIAGE ]
                        if events:
                            date_obj = events[0].get_date_object()
                            if date_obj:
                                return gen.datehandler.displayer.display(date_obj)
        return u''

    def children(self, obj):
        """
        Return a list of the children as the children of the primary spouse.

        @param obj: Person or Family object
        @type obj: L{gen.lib.Person} or L{gen.lib.Family}
        @return: Returns a list of L{gen.lib.Person} objects representing the children
        @rtype: list
        """
        assert(isinstance(obj, (gen.lib.Person, gen.lib.Family, NoneType)))

        if isinstance(obj, gen.lib.Person):
            family_handle_list = obj.get_family_handle_list()
            if family_handle_list:
                family_id = family_handle_list[0]
                family = self.dbase.get_family_from_handle(family_id)
                
                return [ self.dbase.get_person_from_handle(hndl.ref) 
                         for hndl in family.get_child_ref_list() ]
        elif isinstance(obj, gen.lib.Family):
            return [ self.dbase.get_person_from_handle(hndl.ref) 
                     for hndl in obj.get_child_ref_list() ]
        return []

    def father(self, obj):
        """
        Return the primary father of the person or the father of the associated
        family.

        @param obj: Person or Family object
        @type obj: L{gen.lib.Person} or L{gen.lib.Family}
        @return: The father in the person's primary family or the father of the
                 family
        @rtype: L{gen.lib.Person}
        """
        if isinstance(obj, gen.lib.Person):
            return self.__parent(obj, gen.lib.Family.get_father_handle)
        elif isinstance(obj, gen.lib.Family):
            return self.__family_parent(obj, gen.lib.Family.get_father_handle)
        else:
            return None

    def mother(self, obj):
        """
        Returns the primary mother of the person or the mother of the associated
        family.

        @param obj: Person object
        @type obj: L{gen.lib.Person} or L{gen.lib.Family}
        @return: The mother in the person's primary family or the mother of the
                 family
        @rtype: L{gen.lib.Person}
        """
        if isinstance(obj, gen.lib.Person):
            return self.__parent(obj, gen.lib.Family.get_mother_handle)
        elif isinstance(obj, gen.lib.Family):
            return self.__family_parent(obj, gen.lib.Family.get_mother_handle)
        else:
            return None
        
    def birth_date(self, person):
        """
        Return a string indicating the date when the person's birth.

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns a string indicating the date when the person's birth.
        @rtype: unicode
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        return self.__event_date(person, gen.lib.Person.get_birth_ref)

    def birth_date_obj(self, person):
        """
        Return the date when the person's birth.

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns the date when the person's birth.
        @rtype: L{gen.lib.Date}
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        return self.__event_date_obj(person, gen.lib.Person.get_birth_ref)


    def birth_or_fallback(self, person, get_event=False):
        """
        Return the date of the person's birth or fallback event.

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns the date when the person's birth or fallback.
        @rtype: L{gen.lib.Date}
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        event = gen.utils.get_birth_or_fallback(self.dbase, 
                                                person, "<i>%s</i>")
        if get_event:
            return event
        elif event:
            return event.date
        else:
            return gen.lib.Date()

    def birth_place(self, person):
        """
        Return a string indicating the place of the person's birth.

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns a string indicating the place of the person's birth.
        @rtype: unicode
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        return self.__event_place(person, gen.lib.Person.get_birth_ref)

    def death_date(self, person):
        """
        Return a string indicating the date when the person's death.

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns a string indicating the date when the person's death.
        @rtype: unicode
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        return self.__event_date(person, gen.lib.Person.get_death_ref)

    def death_date_obj(self, person):
        """
        Return the date when the person's death.

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns the date when the person's death.
        @rtype: L{gen.lib.Date}
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        return self.__event_date_obj(person, gen.lib.Person.get_death_ref)

    def death_or_fallback(self, person, get_event=False):
        """
        Return the date of the person's death or fallback event.

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns the date of the person's death or fallback.
        @rtype: L{gen.lib.Date}
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        event = gen.utils.get_death_or_fallback(self.dbase, 
                                                person, "<i>%s</i>")
        if get_event:
            return event
        elif event:
            return event.date
        else:
            return gen.lib.Date()

    def death_place(self, person):
        """
        Return a string indicating the place of the person's death.

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: Returns a string indicating the place of the person's death.
        @rtype: unicode
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        return self.__event_place(person, gen.lib.Person.get_death_ref)

    def event_place(self, event):
        """
        Return a string indicating the place of the event

        @param event: Event object
        @type event: L{gen.lib.Event}
        @return: Returns a string indicating the place of the event
        @rtype: unicode
        """
        assert(isinstance(event, (gen.lib.Event, NoneType)))

        if event:
            place_handle = event.get_place_handle()
            return place_name(self.dbase, place_handle)
        else:
            return u''

    def date_string(self, date_obj):
        """
        Return a string representation a date_obj

        @param date_obj: Date object
        @type date_obj: L{gen.lib.Date}
        @return: Returns a string representation a date_obj
        @rtype: unicode
        """
        if date_obj:
            return gen.datehandler.displayer.display(date_obj)
        else:
            return u''

    def event_date(self, event):
        """
        Return a string indicating the date of the event

        @param event: Event object
        @type event: L{gen.lib.Event}
        @return: Returns a string indicating the date of the event
        @rtype: unicode
        """
        assert(isinstance(event, (gen.lib.Event, NoneType)))
        date_obj = event.get_date_object()
        if date_obj:
            return gen.datehandler.displayer.display(date_obj)
        else:
            return u''

    def event_date_obj(self, event):
        """
        Return a string indicating the date of the event

        @param event: Event object
        @type event: L{gen.lib.Event}
        @return: Returns a string indicating the date of the event
        @rtype: unicode
        """
        assert(isinstance(event, (gen.lib.Event, NoneType)))
        if event:
            return event.get_date_object()

    def event_type(self, event):
        """
        Return a string indicating the type of the event

        @param event: Event object
        @type event: L{gen.lib.Event}
        @return: Returns a string indicating the type of the event
        @rtype: unicode
        """
        assert(isinstance(event, (gen.lib.Event, NoneType)))
        if event:
            return str(event.get_type())
        else:
            return u''

    def events(self, obj, restrict=None):
        """
        Return a list of events associated with the object. This object
        can be either a L{gen.lib.Person} or L{gen.lib.Family}.

        @param obj: Person or Family
        @type obj: L{gen.lib.Person} or L{gen.lib.Family}
        @param restrict: Optional list of strings that will limit the types
        of events to those of the specified types.
        @type restrict: list
        @return: list of events associated with the object
        @rtype: list
        """
        assert(isinstance(obj, (gen.lib.Person, gen.lib.Family, NoneType)))
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
        can be either a L{gen.lib.Person} or L{gen.lib.Family}.

        @param obj: Person or Family
        @type obj: L{gen.lib.Person} or L{gen.lib.Family}
        @return: list of events associated with the object
        @rtype: list
        """
        assert(isinstance(obj, (gen.lib.Person, gen.lib.Family, gen.lib.Event, NoneType)))

        if obj:
            handles = [ ref.ref for ref in obj.get_source_references() ]
            return map(self.dbase.get_source_from_handle, handles)
        else:
            return []

    def parent_in(self, person):
        """
        Return a list of families in which the person is listed as a parent.

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: list of L{gen.lib.Family} objects in which the person is listed
           as a parent.
        @rtype: list
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        assert(isinstance(person, (gen.lib.Person, NoneType)))
        
        if person:
            return [ self.dbase.get_family_from_handle(handle) 
                     for handle in person.get_family_handle_list() ]
        return []

    def child_in(self, person):
        """
        Return a list of families in which the person is listed as a child.

        @param person: Person object
        @type person: L{gen.lib.Person}
        @return: list of L{gen.lib.Family} objects in which the person is listed
           as a child.
        @rtype: list
        """
        if type(person) in [str, unicode]: 
            person = self.dbase.get_person_from_handle(person)
        assert(isinstance(person, (gen.lib.Person, NoneType)))
        
        if person:
            return [ self.dbase.get_family_from_handle(handle) 
                     for handle in person.get_parent_family_handle_list() ]
        return []

    def __all_objects(self, gen_cursor, get_object):
        """
        Return a all the objects of a particular type in the database, one 
        at a time as an iterator. The user can treat this just like a list. 

        @return: list of objects of a particular type in the database
        @rtype: list
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

        @return: list of people in the database
        @rtype: list
        """
        
        with self.dbase.get_person_cursor() as cursor:
            slist = sorted((data[3][3], key) for key, data in cursor)

        for info in slist:
            obj = self.dbase.get_person_from_handle(info[1])
            yield obj

    def all_families(self):
        """
        Return all the families in the database, one at a time as an iterator.
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
        Return all the events in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

           for person in sa.all_events():
              sa.print(sa.event_place(event))

        @return: list of events in the database
        @rtype: list
        """
        return self.__all_objects(self.dbase.get_event_cursor, 
                                  self.dbase.get_event_from_handle)

    def all_sources(self):
        """
        Return all the sources in the database, one at a time as an iterator.
        The user can treat this just like a list. For example::

        @return: list of sources in the database
        @rtype: list
        """
        return self.__all_objects(self.dbase.get_source_cursor, 
                                  self.dbase.get_source_from_handle)

    def title(self, source):
        """
        Return the title of the source.

        @param source: Source object
        @type source: L{gen.lib.Source}
        @return: title of the source
        @rtype: unicode
        """
        assert(isinstance(source, (gen.lib.Source, NoneType)))
        if source:
            return source.get_title()
        return u''

    def page(self, citation):
        """
        Return the page of the citation.

        @param citation: Source object
        @type citation: L{gen.lib.Citation}
        @return: title of the citation
        @rtype: unicode
        """
        assert(isinstance(citation, (gen.lib.Citation, NoneType)))
        if citation:
            return citation.get_page()
        return u''

    def author(self, source):
        """
        Return the author of the source.

        @param source: Source object
        @type source: L{gen.lib.Source}
        @return: author of the source
        @rtype: unicode
        """
        assert(isinstance(source, (gen.lib.Source, NoneType)))
        if source:
            return source.get_author()
        return u''

    def person(self, handle):
        assert(type(handle) in [str, unicode])
        return self.dbase.get_person_from_handle(handle)

    def event(self, handle):
        assert(type(handle) in [str, unicode])
        return self.dbase.get_event_from_handle(handle)

    def family(self, handle):
        assert(type(handle) in [str, unicode])
        return self.dbase.get_family_from_handle(handle)

    def display(self, object_class, prop, value):
        """
        Given a object_class, prop, and value return a display string
        describing object.  
        object_class is "Person", "Source", etc.
        prop is "gramps_id", or "handle"
        value is a gramps_id or handle.
        """
        if object_class in self.dbase.get_table_names():
            obj = self.dbase.get_table_metadata(object_class)\
                           [prop + "_func"](value)
            if obj:
                if isinstance(obj, gen.lib.Person):
                    return "%s: %s [%s]" % (_(object_class), 
                                            self.name(obj), 
                                            self.gid(obj))
                elif isinstance(obj, gen.lib.Event):
                    return "%s: %s [%s]" % (_(object_class), 
                                            self.event_type(obj),
                                            self.gid(obj))
                elif isinstance(obj, gen.lib.Family):
                    return "%s: %s/%s [%s]" % (_(object_class), 
                                            self.name(self.mother(obj)), 
                                            self.name(self.father(obj)), 
                                            self.gid(obj))
                elif isinstance(obj, gen.lib.MediaObject):
                    return "%s: %s [%s]" % (_(object_class), 
                                            obj.desc, 
                                            self.gid(obj))
                elif isinstance(obj, gen.lib.Source):
                    return "%s: %s [%s]" % (_(object_class), 
                                            self.title(obj), 
                                            self.gid(obj))
                elif isinstance(obj, gen.lib.Citation):
                    return "%s: [%s]" % (_(object_class), 
                                            self.gid(obj))
                elif isinstance(obj, gen.lib.Place):
                    return "%s: %s [%s]" % (_(object_class), 
                                            place_name(self.dbase, 
                                                       obj.handle), 
                                            self.gid(obj))
                elif isinstance(obj, gen.lib.Repository):
                    return "%s: %s [%s]" % (_(object_class), 
                                            obj.type, 
                                            self.gid(obj))
                elif isinstance(obj, gen.lib.Note):
                    return "%s: %s [%s]" % (_(object_class), 
                                            obj.type, 
                                            self.gid(obj))
                else:
                    return "Error: incorrect object class: '%s'" % type(obj)
            else:
                return "Error: missing object"
        else:
            return "Error: invalid object class: '%s'" % object_class

    def describe(self, obj):
        """
        Given a object, return a string describing the object.  
        """
        if isinstance(obj, gen.lib.Person):
            return self.name(obj)
        elif isinstance(obj, gen.lib.Event):
            return self.event_type(obj)
        elif isinstance(obj, gen.lib.Family):
            father = self.father(obj)
            mother = self.mother(obj)
            if father:
                father_text = self.name(father)
            else:
                father_text = _("Unknown father")
            if mother:
                mother_text = self.name(mother)
            else:
                mother_text = _("Unknown mother")
            return "%s and %s" % (mother_text, father_text)
        elif isinstance(obj, gen.lib.MediaObject):
            return obj.desc
        elif isinstance(obj, gen.lib.Citation):
            return obj.gramps_id
        elif isinstance(obj, gen.lib.Source):
            return self.title(obj)
        elif isinstance(obj, gen.lib.Place):
            return place_name(self.dbase, obj.handle)
        elif isinstance(obj, gen.lib.Repository):
            return obj.gramps_id
        elif isinstance(obj, gen.lib.Note):
            return obj.gramps_id
        elif obj is None:
            return ""
        else:
            return "Error: incorrect object class: '%s'" % type(obj)

    def get_link(self, object_class, prop, value):
        """
        Given a object_class, prop, and value return the object.
        object_class is "Person", "Source", etc.
        prop is "gramps_id", or "handle"
        value is a gramps_id or handle.
        """
        if object_class in self.dbase.get_table_names():
            return self.dbase.get_table_metadata(object_class) \
                [prop + "_func"](value)

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
    if event1 and event2:
        return cmp(event1.get_date_object() , event2.get_date_object())
    elif event1:
        return -1
    elif event2:
        return 1
    else:
        return 0
