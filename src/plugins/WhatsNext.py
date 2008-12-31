# encoding: utf-8
#
# Gramps - a GTK+/GNOME based genealogy program - What Next Gramplet plugin
#
# Copyright (C) 2008 Reinhard Mueller
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

# $Id: $

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.lib import EventType, FamilyRelType
from BasicUtils import name_displayer
from DataViews import register, Gramplet
from ReportBase import ReportUtils
#from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# The Gramplet
#
#------------------------------------------------------------------------
class WhatNextGramplet(Gramplet):

    # Minimum number of lines we want to see. Further lines with the same
    # distance to the main person will be added on top of this.
    TODOS_WANTED = 10

    # How many generations of descendants to process before we go up to the
    # next level of ancestors.
    DOWNS_PER_UP = 2

    # After an ancestor was processed, how many extra rounds to delay until the
    # descendants of this ancestor are processed.
    ANCESTOR_DELAY = 1

    # After a spouse was processed, how many extra rounds to delay until the
    # ancestors of this spouse are processed.
    SPOUSE_DELAY = 1

    def init(self):

        self.tooltip = _("Double-click name for details")
        self.set_text(_("No Family Tree loaded."))


    def db_changed(self):

        self.dbstate.db.connect('home-person-changed', self.update)
        self.dbstate.db.connect('person-add', self.update)
        self.dbstate.db.connect('person-delete', self.update)
        self.dbstate.db.connect('person-update', self.update)
        self.dbstate.db.connect('family-add', self.update)
        self.dbstate.db.connect('family-delete', self.update)
        self.dbstate.db.connect('family-update', self.update)


    def main(self):

        default_person = self.dbstate.db.get_default_person()
        if default_person == None:
            self.set_text(_("No Home Person set."))
            return

        self.__counter = 0
        self.__level = 1

        self.set_text("")


        # List of already processed persons and families, to avoid recursing
        # back down to ourselves or meeting the same person through different
        # paths.
        self.__processed_persons = {default_person.get_handle(): True}
        self.__processed_families = {}

        # List of lists of ancestors in currently processed generation. We go
        # up one generation in each round.
        # The lists are separated into my own ancestors, the ancestors of my
        # spouses, the ancestors of my children's spouses, the ancestors of my
        # parent's other spouses, the ancestors of my grandchildren's spouses,
        # the ancestors of my sibling's spouses etc.
        ancestors = [[default_person]]
        ancestors_queue = [[[default_person]]] + [[]] * self.ANCESTOR_DELAY

        # List of lists of families of relatives in currently processed
        # distance. We go up one level of distance in each round.
        # For example, at the end of the third round, this is (potentially) a
        # list of 4 lists:
        # 1. my own great-grandchildren
        # 2. grandchildren of my parents (= my nephews and nieces)
        # 3. children of my grandparents (= my uncles and aunts)
        # 4. my great-grandparents
        # At the beginning of the fourth round, the other families of my
        # great-grandparents are added (if they were married more than once).
        # The separation into these levels is done to allow the spouses of the
        # earlier level to be listed before the kins of the later level, e.g.
        # the spouses of my nephews and nieces are listed before my uncles and
        # aunts.
        # Not that this may slightly vary with the parameters given at the
        # beginning of this class definition, but the principle remains the
        # same.
        families = []
        families_queue = [[]] * self.ANCESTOR_DELAY

        # List of spouses to add to ancestors list so we track ancestors of
        # spouses, too, but delayed as defined by the parameter.
        spouses = []
        spouses_queue = [[]] * self.SPOUSE_DELAY

        while (ancestors or families):
            # (Other) families of parents
            for ancestor_group in ancestors_queue.pop(0):
                new_family_group = []
                new_spouses_group = []
                for person in ancestor_group:
                    for family in self.__get_families(person):
                        spouse = self.__get_spouse(person, family)
                        if spouse:
                            self.__process_person(spouse)
                            new_spouses_group.append(spouse)
                        elif family.get_relationship() == FamilyRelType.MARRIED:
                            self.__missing_spouse(person)
                        self.__process_family(family, person, spouse)
                        new_family_group.append(family)
                if new_family_group:
                    families.append(new_family_group)
                if new_spouses_group:
                    spouses.append(new_spouses_group)
            if self.__counter >= self.TODOS_WANTED:
                break

            # Now add the spouses of last round to the list
            spouses_queue.append(spouses)
            ancestors += spouses_queue.pop(0)

            # Separator between rounds
            if self.__counter > 0:
                self.append_text("\n")
                self.__level += 1

            # Next generation of children
            spouses = []
            for down in range(self.DOWNS_PER_UP):
                new_families = []
                for family_group in families:
                    children = []
                    for family in family_group:
                        for child in self.__get_children(family):
                            self.__process_person(child)
                            children.append(child)
                    if self.__counter >= self.TODOS_WANTED:
                        break

                    # Families of children
                    new_family_group = []
                    new_spouses_group = []
                    for person in children:
                        for family in self.__get_families(person):
                            spouse = self.__get_spouse(person, family)
                            if spouse:
                                self.__process_person(spouse)
                                new_spouses_group.append(spouse)
                            elif family.get_relationship() == FamilyRelType.MARRIED:
                                self.__missing_spouse(person)
                            self.__process_family(family, person, spouse)
                            new_family_group.append(family)
                    if new_family_group:
                        new_families.append(new_family_group)
                    if new_spouses_group:
                        spouses.append(new_spouses_group)
                    if self.__counter >= self.TODOS_WANTED:
                        break
                families = new_families
                if self.__counter >= self.TODOS_WANTED:
                    break
            if self.__counter >= self.TODOS_WANTED:
                break

            # Parents
            new_ancestors = []
            new_families = []
            for ancestor_group in ancestors:
                new_ancestor_group = []
                new_family_group = []
                for person in ancestor_group:
                    (father, mother, family) = self.__get_parents(person)
                    if family:
                        if father:
                            self.__process_person(father)
                            new_ancestor_group.append(father)
                        elif family.get_relationship() == FamilyRelType.MARRIED:
                            self.__missing_father(person)
                        if mother:
                            self.__process_person(mother)
                            new_ancestor_group.append(mother)
                        else:
                            self.__missing_mother(person)
                        self.__process_family(family, father, mother)
                        new_family_group.append(family)
                    else:
                        self.__missing_parents(person)
                if new_ancestor_group:
                    new_ancestors.append(new_ancestor_group)
                if new_family_group:
                    new_families.append(new_family_group)
                if self.__counter >= self.TODOS_WANTED:
                    break
            ancestors = new_ancestors
            ancestors_queue.append(ancestors)
            families_queue.append(new_families)
            families += families_queue.pop(0)
            if self.__counter >= self.TODOS_WANTED:
                break

        self.append_text("", scroll_to='begin')


    def __process_person(self, person):

        self.__processed_persons[person.get_handle()] = True

        missingbits = []

        primary_name = person.get_primary_name()

        if not primary_name.get_first_name():
            missingbits.append(_("first name unknown"))

        if not primary_name.get_surname():
            missingbits.append(_("surname unknown"))

        name = name_displayer.display_name(primary_name)
        if not name:
            name = _("(person with unknown name)")

        has_birth = False

        for event_ref in person.get_primary_event_ref_list():
            event = self.dbstate.db.get_event_from_handle(event_ref.ref)
            if event.get_type() not in [EventType.BIRTH, EventType.DEATH]:
                continue
            missingbits.extend(self.__process_event(event))
            if event.get_type() == EventType.BIRTH:
                has_birth = True

        if not has_birth:
            missingbits.append(_("birth event missing"))

        if missingbits:
            self.link(name, 'Person', person.get_handle())
            self.append_text(_(": %(list)s\n") % {
                'list': _(", ").join(missingbits)})
            self.__counter += 1


    def __process_family(self, family, person1, person2):

        self.__processed_families[family.get_handle()] = True

        missingbits = []

        if person1:
            name1 = name_displayer.display(person1)
            if not name1:
                name1 = _("(person with unknown name)")
        else:
            name1 = _("(unknown person)")

        if person2:
            name2 = name_displayer.display(person2)
            if not name2:
                name2 = _("(person with unknown name)")
        else:
            name2 = _("(unknown person)")

        name = _("%(name1)s and %(name2)s") % {
                'name1': name1,
                'name2': name2}

        has_marriage = False

        for event_ref in family.get_event_ref_list():
            event = self.dbstate.db.get_event_from_handle(event_ref.ref)
            if event.get_type() not in [EventType.MARRIAGE, EventType.DIVORCE]:
                continue
            missingbits.extend(self.__process_event(event))
            if event.get_type() == EventType.MARRIAGE:
                has_marriage = True

        if family.get_relationship() == FamilyRelType.MARRIED:
            if not has_marriage:
                missingbits.append(_("marriage event missing"))
        elif family.get_relationship() == FamilyRelType.UNKNOWN:
            missingbits.append(_("relation type unknown"))

        if missingbits:
            self.link(name, 'Family', family.get_handle())
            self.append_text(_(": %(list)s\n") % {
                'list': _(", ").join(missingbits)})
            self.__counter += 1


    def __process_event(self, event):

        missingbits = []

        date = event.get_date_object()
        if date.is_empty():
            missingbits.append(_("date unknown"))
        elif not date.is_regular():
            missingbits.append(_("date incomplete"))

        place_handle = event.get_place_handle()
        if not place_handle:
            missingbits.append(_("place unknown"))

        if missingbits:
            return [_("%(type)s: %(list)s") % {
                    'type': event.get_type(),
                    'list': _(", ").join(missingbits)}]
        else:
            return []


    def __missing_spouse(self, person):
        self.__missing_link(person, _("spouse missing"))


    def __missing_father(self, person):
        self.__missing_link(person, _("father missing"))


    def __missing_mother(self, person):
        self.__missing_link(person, _("mother missing"))


    def __missing_parents(self, person):
        self.__missing_link(person, _("parents missing"))


    def __missing_link(self, person, text):

        name = name_displayer.display(person)
        self.link(name, 'Person', person.get_handle())
        self.append_text(_(": %s\n") % text)
        self.__counter += 1


    def __get_spouse(self, person, family):

        spouse_handle = ReportUtils.find_spouse(person, family)
        if not spouse_handle:
            return None
        if spouse_handle in self.__processed_persons:
            return None
        return self.dbstate.db.get_person_from_handle(spouse_handle)


    def __get_children(self, family):

        for child_ref in family.get_child_ref_list():
            if child_ref.ref in self.__processed_persons:
                continue
            yield self.dbstate.db.get_person_from_handle(child_ref.ref)


    def __get_families(self, person):

        for family_handle in person.get_family_handle_list():
            if family_handle in self.__processed_families:
                continue
            yield self.dbstate.db.get_family_from_handle(family_handle)


    def __get_parents(self, person):

        family_handle = person.get_main_parents_family_handle()
        if not family_handle or family_handle in self.__processed_families:
            return (None, None, None)

        family = self.dbstate.db.get_family_from_handle(family_handle)

        father_handle = family.get_father_handle()
        if father_handle and father_handle not in self.__processed_persons:
            father = self.dbstate.db.get_person_from_handle(father_handle)
        else:
            father = None

        mother_handle = family.get_mother_handle()
        if mother_handle and mother_handle not in self.__processed_persons:
            mother = self.dbstate.db.get_person_from_handle(mother_handle)
        else:
            mother = None

        return (father, mother, family)


#------------------------------------------------------------------------
#
# Translation hack
#
#------------------------------------------------------------------------
mytranslation = {
        u"first name unknown"        : u"Vorname unbekannt",
        u"surname unknown"           : u"Familienname unbekannt",
        u"(person with unknown name)": u"(Person mit unbekanntem Namen)",
        u"birth event missing"       : u"Geburtsereignis fehlt",
        u"(unknown person)"          : u"(unbekannte Person)",
        u"%(name1)s and %(name2)s"   : u"%(name1)s und %(name2)s",
        u" and "                     : u" und ",
        u"marriage event missing"    : u"Hochzeitsereignis fehlt",
        u"relation type unknown"     : u"Beziehungstyp unbekannt",
        u"date unknown"              : u"Datum unbekannt",
        u"date incomplete"           : u"Datum unvollständig",
        u"place unknown"             : u"Ort unbekannt",
        u"spouse missing"            : u"Partner fehlt",
        u"father missing"            : u"Vater fehlt",
        u"mother missing"            : u"Mutter fehlt",
        u"parents missing"           : u"Eltern fehlen"}

from gettext import gettext
import locale
lang = locale.getdefaultlocale()[0]
if lang:
    lang = lang.split('_')[0]
def _(string):
    if lang == 'de':
        print string
        return mytranslation.get(string, gettext(string))
    else:
        return gettext(string)


#------------------------------------------------------------------------
#
# Register the gramplet
#
#------------------------------------------------------------------------
register(
        type = "gramplet", 
        name = "What's Next Gramplet", 
        tname =_("What's Next Gramplet"), 
        height = 230,
        expand = True,
        content = WhatNextGramplet,
        title = _("What's Next?"))
