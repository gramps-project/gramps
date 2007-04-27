
from types import NoneType

import RelLib
import DateHandler

from BasicUtils import NameDisplay
from ReportBase import ReportUtils

class SimpleReport:

    def __init__(self, db, person):
        self.db = db
        self.person = person

    def run(self):
        pass

    def name(self, person):
        assert(isinstance(person, (RelLib.Person, NoneType)))
        if person:
            return NameDisplay.displayer.display(person)
        else:
            return u''

    def __parent(self, person, func):
        assert(isinstance(person, (RelLib.Person, NoneType)))

        if person:
            parent_handle_list = person.get_parent_family_handle_list()
            if parent_handle_list:
                family_id = parent_handle_list[0]
                family = self.db.get_family_from_handle(family_id)
                person_handle = func(family)
                if person_handle:
                    return self.db.get_person_from_handle(person_handle)
        return None

    def __event_date(self, person, func):
        assert(isinstance(person, (RelLib.Person, NoneType)))

        if person:
            ref = func(person)
            if ref:
                event_handle = ref.get_reference_handle()
                if event_handle:
                    event = self.db.get_event_from_handle(event_handle)
                    date_obj = event.get_date_object()
                    if date_obj:
                        return DateHandler.displayer.display(date_obj)
        return u''

    def __event_place(self, person, func):
        assert(isinstance(person, (RelLib.Person, NoneType)))

        if person:
            ref = func(person)
            if ref:
                event_handle = ref.get_reference_handle()
                if event_handle:
                    event = self.db.get_event_from_handle(event_handle)
                    place_handle = event.get_place_handle()
                    return ReportUtils.place_name(self.db, place_handle)
        return u''

    def spouse(self, person):
        assert(isinstance(person, (RelLib.Person, NoneType)))

        if person:
            family_handle_list = person.get_family_handle_list()
            if family_handle_list:
                family_id = family_handle_list[0]
                family = self.db.get_family_from_handle(family_id)
                if family.get_father_handle() == person.get_handle():
                    person_handle = family.get_mother_handle()
                else:
                    person_handle = family.get_father_handle()
                if person_handle:
                    return self.db.get_person_from_handle(person_handle)
        return None

    def marriage_type(self, person):
        assert(isinstance(person, (RelLib.Person, NoneType)))

        if person:
            family_handle_list = person.get_family_handle_list()
            if family_handle_list:
                family_id = family_handle_list[0]
                family = self.db.get_family_from_handle(family_id)
                if family:
                    return str(family.get_relationship())
        return u''

    def marriage_place(self, person):
        assert(isinstance(person, (RelLib.Person, NoneType)))

        if person:
            family_handle_list = person.get_family_handle_list()
            if family_handle_list:
                family_id = family_handle_list[0]
                family = self.db.get_family_from_handle(family_id)
                if family:
                    reflist = family.get_event_ref_list()
                    if reflist:
                        ref = reflist[0].ref
                        event = self.db.get_event_from_handle(ref)
                        place_handle = event.get_place_handle()
                        return ReportUtils.place_name(self.db, place_handle)
        return u''

    def marriage_date(self, person):
        assert(isinstance(person, (RelLib.Person, NoneType)))

        if person:
            family_handle_list = person.get_family_handle_list()
            if family_handle_list:
                family_id = family_handle_list[0]
                family = self.db.get_family_from_handle(family_id)
                if family:
                    reflist = family.get_event_ref_list()
                    if reflist:
                        ref = reflist[0].ref
                        event = self.db.get_event_from_handle(ref)
                        date_obj = event.get_date_object()
                        if date_obj:
                            return DateHandler.displayer.display(date_obj)
        return u''

    def children(self, person):
        assert(isinstance(person, (RelLib.Person, NoneType)))

        if person:
            family_handle_list = person.get_family_handle_list()
            if family_handle_list:
                family_id = family_handle_list[0]
                family = self.db.get_family_from_handle(family_id)
                
                return [ self.db.get_person_from_handle(hndl.ref) 
                         for hndl in family.get_child_ref_list() ]
        return []

    def father(self, person):
        return self.__parent(person, RelLib.Family.get_father_handle)

    def mother(self, person):
        return self.__parent(person, RelLib.Family.get_mother_handle)
        
    def birth_date(self, person):
        return self.__event_date(person, RelLib.Person.get_birth_ref)

    def birth_place(self, person):
        return self.__event_place(person, RelLib.Person.get_birth_ref)

    def death_date(self, person):
        return self.__event_date(person, RelLib.Person.get_death_ref)

    def death_place(self, person):
        return self.__event_place(person, RelLib.Person.get_death_ref)

if __name__ == "__main__":

    from GrampsDb import gramps_db_factory
    import sys
    import const

    class MyReport(SimpleReport):

        def run(self):
            print "Person        : ", self.name(self.person)
            print "Birth date    : ", self.birth_date(self.person)
            print "Birth place   : ", self.birth_place(self.person)
            print "Death date    : ", self.death_date(self.person)
            print "Death place   : ", self.death_place(self.person)
            print "Father        : ", self.name(self.father(self.person))
            print "Mother        : ", self.name(self.mother(self.person))
            print "Spouse        : ", self.name(self.spouse(self.person))
            print "Marriage Type : ", self.marriage_type(self.person)
            print "Marriage Date : ", self.marriage_date(self.person)
            print "Marriage Place: ", self.marriage_place(self.person)
            for child in self.children(self.person):
                print "Child         : ", self.name(child)

    db_class = gramps_db_factory(const.app_gramps_xml)
    database = db_class()
    database.load(sys.argv[1], lambda x: None, mode="w")
    person = database.get_default_person()
    
    a = MyReport(database, person)

    a.run()
        

