#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004 Bruce J. DeGrasse
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

# $Id$

"Generate files/Detailed Descendant Report"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Gnome/GTK modules
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import RelLib
import Errors
from QuestionDialog import ErrorDialog
import Report
import BaseDoc
import ReportOptions
import const
from DateHandler import displayer as _dd

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class DetDescendantReport(Report.Report):

    def __init__(self,database,person,options_class):
        """
        Creates the DetDescendantReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        gen           - Maximum number of generations to include.
        pagebgg       - Whether to include page breaks between generations.
        firstName     - Whether to use first names instead of pronouns.
        fullDate      - Whether to use full dates instead of just year.
        listChildren  - Whether to list children.
        includeNotes  - Whether to include notes.
        blankPlace    - Whether to replace missing Places with ___________.
        blankDate     - Whether to replace missing Dates with ___________.
        calcAgeFlag   - Whether to compute age.
        dupPerson     - Whether to omit duplicate ancestors (e.g. when distant cousins mary).
        childRef      - Whether to add descendant references in child list.
        addImages     - Whether to include images.
        """
        Report.Report.__init__(self,database,person,options_class)

        self.map = {}

        (self.max_generations,self.pgbrk) \
                        = options_class.get_report_generations()

        self.firstName     = options_class.handler.options_dict['firstnameiop']
        self.fullDate      = options_class.handler.options_dict['fulldates']
        self.listChildren  = options_class.handler.options_dict['listc']
        self.includeNotes  = options_class.handler.options_dict['incnotes']
        self.blankPlace    = options_class.handler.options_dict['repplace']
        self.blankDate     = options_class.handler.options_dict['repdate']
        self.calcAgeFlag   = options_class.handler.options_dict['computeage']
        self.dupPerson     = options_class.handler.options_dict['omitda']
        self.childRef      = options_class.handler.options_dict['desref']
        self.addImages     = options_class.handler.options_dict['incphotos']

        self.genIDs = {}
        self.prevGenIDs= {}
        self.genKeys = []

    def apply_filter(self,person_handle,index,cur_gen=1):
        if (not person_handle) or (cur_gen > self.max_generations):
            return 
        self.map[index] = person_handle

        if len(self.genKeys) < cur_gen:
            self.genKeys.append([index])
        else: 
            self.genKeys[cur_gen-1].append(index)

        person = self.database.get_person_from_handle(person_handle)
        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            for child_handle in family.get_child_handle_list():
                child = self.database.get_family_from_handle(child_handle)
                ix = max(self.map.keys())
                self.apply_filter(child_handle, ix+1, cur_gen+1)

    def calcAge(self, ind):
        """ Calulate age
        APHRASE=
            at the age of NUMBER UNIT(S)
        UNIT= year | month | day
        UNITS= years | months | days
        null
        """

        birth_handle = ind.get_birth_handle()
        if birth_handle:
            birth = self.database.get_event_from_handle(birth_handle).get_date_object()
            birth_year_valid = birth.get_year_valid()
        else:
            birth_year_valid = None
        death_handle = ind.get_death_handle()
        if death_handle:
            death = self.database.get_event_from_handle(death_handle).get_date_object()
            death_year_valid = death.get_year_valid()
        else:
            death_year_valid = None

        the_text = ""
        if birth_year_valid and death_year_valid:
            age = death.get_year() - birth.get_year()
            units = 3                          # year
            if birth.get_month_valid() and death.get_month_valid():
                if birth.get_month() > death.get_month():
                    age = age -1
                if birth.get_day_valid() and death.get_day_valid():
                    if birth.get_month() == death.get_month() and birth.get_day() > death.get_day():
                        age = age -1
                    if age == 0:
                        age = death.get_month() - birth.get_month()   # calc age in months
                        if birth.get_day() > death.get_day():
                            age = age - 1
                            units = 2                        # month
                        if age == 0:
                            age = death.get-day() + 31 - birth.get_day() # calc age in days
                            units = 1            # day
            if age > 1:
                if units == 1:
                    the_text = _(" at the age of %d days") % age
                elif units == 2:
                    the_text = _(" at the age of %d months") % age
                else:
                    the_text = _(" at the age of %d years") % age
            else:
                if units == 1:
                    the_text = _(" at the age of %d day") % age
                elif units == 2:
                    the_text = _(" at the age of %d month") % age
                else:
                    the_text = _(" at the age of %d year") % age
        return the_text

    def write_children(self, family):
        """ List children
            Statement formats:
                Child of MOTHER and FATHER is:
                Children of MOTHER and FATHER are:

                NAME Born: DATE PLACE Died: DATE PLACE          f
                NAME Born: DATE PLACE Died: DATE                e
                NAME Born: DATE PLACE Died: PLACE               d
                NAME Born: DATE PLACE                           c
                NAME Born: DATE Died: DATE PLACE                b
                NAME Born: DATE Died: DATE                      a
                NAME Born: DATE Died: PLACE                     9
                NAME Born: DATE                                 8
                NAME Born: PLACE Died: DATE PLACE               7
                NAME Born: PLACE Died: DATE                     6
                NAME Born: PLACE Died: PLACE                    5
                NAME Born: PLACE                                4
                NAME Died: DATE                                 2
                NAME Died: DATE PLACE                           3
                NAME Died: PLACE                                1
                NAME                                            0
        """

        num_children = len(family.get_child_handle_list())
        if num_children:
            self.doc.start_paragraph("DDR-ChildTitle")
            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = self.database.get_person_from_handle(mother_handle).get_primary_name().get_regular_name()
            else:
                mother = _("unknown")
            father_handle = family.get_father_handle()
            if father_handle:
                father = self.database.get_person_from_handle(father_handle).get_primary_name().get_regular_name()
            else:
                father = _("unknown")
            self.doc.start_bold()
            if num_children == 1:
                self.doc.write_text(_("Child of %s and %s is:") % (mother, father))
            else:
                self.doc.write_text(_("Children of %s and %s are:") % (mother, father))
            self.doc.end_bold()
            self.doc.end_paragraph()

            for child_handle in family.get_child_handle_list():
                child = self.database.get_person_from_handle(child_handle)
                self.doc.start_paragraph("DDR-ChildList")
                name = child.get_primary_name().get_regular_name()
                birth_handle = child.get_birth_handle()
                death_handle = child.get_death_handle()
                if self.childRef:
                    if self.prevGenIDs.get(child_handle) != None:
                        name= "[" + str(self.prevGenIDs.get(child_handle)) + "] "+ name

                if birth_handle:
                    birth = self.database.get_event_from_handle(birth_handle)
                else:
                    birth = None

                if death_handle:
                    death = self.database.get_event_from_handle(death_handle)
                else:
                    death = None

                if birth and birth.get_date():
                    if birth.get_place_handle():
                        bplace = self.database.get_place_from_handle(birth.get_place_handle()).get_title()
                        if death and death.get_date():
                            if death.get_place_handle():
                                dplace = self.database.get_place_from_handle(death.get_place_handle()).get_title()
                                self.doc.write_text(_("- %s Born: %s %s Died: %s %s") % \
                                    (name, birth.get_date(), bplace,
                                     death.get_date(), dplace))  # f
                            else:
                                self.doc.write_text(_("- %s Born: %s %s Died: %s") % \
                                    (name, birth.get_date(), bplace,
                                     death.get_date()))                    # e
                        elif death and death.get_place_handle():
                            dplace = self.database.get_place_from_handle(death.get_place_handle()).get_title()
                            self.doc.write_text(_("- %s Born: %s %s Died: %s") % \
                                (name, birth.get_date(), bplace,
                                 dplace))                   # d
                        else:   self.doc.write_text(_("- %s Born: %s %s") % \
                                    (name, birth.get_date(), bplace)) # c
                    else:
                        if death and death.get_date():
                            if death.get_place_handle():
                                dplace = self.database.get_place_from_handle(death.get_place_handle()).get_title()
                                self.doc.write_text(_("- %s Born: %s Died: %s %s") % \
                                    (name, birth.get_date(), death.get_date(), \
                                     dplace))                    # b
                            else:
                                self.doc.write_text(_("- %s Born: %s Died: %s") % \
                                    (name, birth.get_date(), death.get_date())) # a
                        elif death and death.get_place_handle():
                            dplace = self.database.get_place_from_handle(death.get_place_handle()).get_title()
                            self.doc.write_text(_("- %s Born: %s Died: %s") % \
                                (name, birth.get_date(), dplace)) # 9
                        else:
                            self.doc.write_text(_("- %s Born: %s") % \
                                (name, birth.get_date()))               # 8
                else:
                    if birth and birth.get_place_handle():
                        bplace = self.database.get_place_from_handle(birth.get_place_handle()).get_title()
                        if death and death.get_date():
                            if death.get_place_handle():
                                dplace = self.database.get_place_from_handle(death.get_place_handle()).get_title()
                                self.doc.write_text(_("- %s Born: %s Died: %s %s") % \
                                    (name, bplace,                  \
                                     death.get_date(), dplace))  # 7
                            else:
                                self.doc.write_text(_("- %s Born: %s Died: %s") % \
                                    (name, bplace, death.get_date())) # 6
                        elif death and death.get_place_handle():
                            dplace = self.database.get_place_from_handle(death.get_place_handle()).get_title()
                            self.doc.write_text(_("- %s Born: %s Died: %s") % \
                                (name, bplace, dplace)) # 5
                        else:
                            self.doc.write_text(_("- %s Born: %s") % \
                                (name, bplace))             # 4
                    else:
                        if death and death.get_date():
                            if death.get_place_handle():
                                dplace = self.database.get_place_from_handle(death.get_place_handle()).get_title()
                                self.doc.write_text(_("- %s Died: %s %s") % \
                                    (name, death.get_date(), dplace)) # 3
                            else:
                                self.doc.write_text(_("- %s Died: %s") % \
                                    (name, death.get_date()))               # 2
                        elif death and death.get_place_handle():
                            dplace = self.database.get_place_from_handle(death.get_place_handle()).get_title()
                            self.doc.write_text(_("- %s Died: %s") % \
                                (name, dplace)) # 1
                        else:
                            self.doc.write_text(_("- %s") % name)          # 0

                self.doc.end_paragraph()

    def write_person(self, key):
        """Output birth, death, parentage, marriage and notes information """

        person_handle = self.map[key]
        person = self.database.get_person_from_handle(person_handle)
        if self.addImages:
            self.insert_images(person)

        self.doc.start_paragraph("DDR-First-Entry","%s." % str(key))

        name = person.get_primary_name().get_regular_name()

        if self.firstName:
            firstName = person.get_primary_name().get_first_name()
        elif person.get_gender() == RelLib.Person.male:
            firstName = _("He")
        else:
            firstName = _("She")

        self.doc.start_bold()
        self.doc.write_text(name)
        self.doc.end_bold()

        if self.dupPerson:
            # Check for duplicate record (result of distant cousins marrying)
            keys = self.map.keys()
            keys.sort()
            for dkey in keys:
                if dkey >= key:
                    break
                if self.map[key] == self.map[dkey]:
                    self.doc.write_text(_(" is the same person as [%s].") % str(dkey))
                    self.doc.end_paragraph()
                    return 1	# Duplicate person

        # Check birth record
        birth_handle = person.get_birth_handle()
        if birth_handle:
            self.write_birth(person)
        self.write_death(person, firstName)
        self.write_parents(person, firstName)
        self.write_marriage(person)
        self.doc.end_paragraph()

        self.write_mate(person)

        if person.get_note() and self.includeNotes:
            self.doc.start_paragraph("DDR-NoteHeader")
            self.doc.start_bold()
            self.doc.write_text(_("Notes for %s" % name))
            self.doc.end_bold()
            self.doc.end_paragraph()
            self.doc.write_note(person.get_note(),person.get_note_format(),"DDR-Entry")

        return 0		# Not duplicate person

    def write_birth(self, person):
        """ Check birth record
            Statement formats name precedes this
               was born on DATE.
               was born on ________.
               was born on Date in Place.
               was born on ________ in PLACE.
               was born in ____________.
               was born in the year YEAR.
               was born in PLACE.
               was born in ____________.
        """

        birth_handle = person.get_birth_handle()
        if birth_handle:
            birth = self.database.get_event_from_handle(birth_handle)
            date_obj = birth.get_date_object()
	    date_txt = birth.get_date()
            if birth.get_place_handle():
                place = self.database.get_place_from_handle(birth.get_place_handle()).get_title()
                if place[-1:] == '.':
                    place = place[:-1]
            elif self.blankDate:
                place = "______________"
            else:
                place = ""

            if date_txt:
                if date_obj.get_day_valid() and date_obj.get_month_valid() and \
                        self.fullDate:
                    if place:
                        self.doc.write_text(_(" was born on %s in %s.") % (date_txt, place))
                    else:
                        self.doc.write_text(_(" was born on %s.") % date_txt )
                elif place:
                    self.doc.write_text(_(" was born in the year %s in %s.") % \
                          (date_obj.get_year(), place))
                else:
                    self.doc.write_text(_(" was born in the year %s.") % date_obj.get_year())
            elif place:
                self.doc.write_text(_(" was born in %s.") % place)
            else:
                self.doc.write_text(_("."))

    def write_death(self, person, firstName):
        """ Write obit sentence
        Statement format: DPHRASE APHRASE BPHRASE
        DPHRASE=
            FIRSTNAME died on FULLDATE in PLACE
            FIRSTNAME died on FULLDATE
            FIRSTNAME died in PLACE
            FIRSTNAME died on FULLDATE in PLACE
            FIRSTNAME died in YEAR in PLACE
            FIRSTNAME died in YEAR

        APHRASE=           see calcAge
            at the age of NUMBER UNIT(S)
            null

            where
            UNIT= year | month | day
            UNITS= years | months | days

        BPHRASE=
            , and was buried on FULLDATE in PLACE.
            , and was buried on FULLDATE.
            , and was buried in PLACE.
            .
        """
        t= ""
        death_handle = person.get_death_handle()
        if death_handle:
            death = self.database.get_event_from_handle(death_handle)
            date_obj = death.get_date_object()
            date_txt = death.get_date()
            place_handle = death.get_place_handle()
            if place_handle:
                place = self.database.get_place_from_handle(place_handle).get_title()
                if place[-1:] == '.':
                    place = place[:-1]
            elif self.blankPlace:
                place = "_____________"
            else:
                place = ""

            if date_txt:
                if date_obj.get_day() and date_obj.get_month() and \
                            self.fullDate:
                    fulldate = date_txt
                elif date_obj.get_month() and self.fullDate:
                    fulldate = "%s %s" % (date_obj.get_month(), date_obj.get_year())
                else:
                    fulldate = ""
            elif self.blankDate:
                fulldate = "_____________"
            else:
                fulldate = ""

            if fulldate:
                if place:
                    t = _("  %s died on %s in %s") % (firstName, fulldate, place)
                else:
                    t = _("  %s died on %s") % (firstName, fulldate)
            elif date_obj.get_year() > 0:
                if place:
                    t = _("  %s died in %s in %s") % (firstName, date_obj.get_year(), place)
                else:
                    t = _("  %s died in %s") % (firstName, date_obj.get_year())
            elif place:
                t = _("  %s died in %s") % (firstName, place)

            if self.calcAgeFlag:
                t = t + self.calcAge(person)

            if t:
                self.doc.write_text(t)

        t = ""
        famList = person.get_family_handle_list()
        if len(famList):
            for fam_id in famList:
                fam = self.database.get_family_from_handle(fam_id)
                buried = None
                if buried:
                    date_obj = buried.get_date_object()
                    date_txt = buried.get_date()
                    place = buried.get_place_name()
                    if place[-1:] == '.':
                        place = place[:-1]
                    fulldate= ""
                    if date_txt:
                        if date_obj.get_day_valid() and date_obj.get_month_valid() and \
                                        self.fullDate:
                            fulldate = date_txt
                    elif self.blankDate:
                            fulldate= "___________"

                    if fulldate and place:
                        t = _("  And %s was buried on %s in %s.") % (firstName, fulldate, place)
                    elif fulldate and not place:
                        t = _("  And %s was buried on %s.") % (firstName, fulldate)
                    elif not fulldate and place:
                        t = _("  And %s was buried in %s.") % (firstName, place)

        if t:
            self.doc.write_text(t)
        else:
            self.doc.write_text(".")

    def write_parents(self, person, firstName):
        """ Ouptut parents sentence
        Statement format:

        FIRSTNAME is the son of FATHER and MOTHER.
        FIRSTNAME is the son of FATHER.
        FIRSTNAME is the son of MOTHER.
        FIRSTNAME is the daughter of FATHER and MOTHER.
        FIRSTNAME is the daughter of FATHER.
        FIRSTNAME is the daughter of MOTHER.
        """
        ext_family_handle = person.get_main_parents_family_handle()
        if ext_family_handle:
            ext_family = self.database.get_family_from_handle(ext_family_handle)
            father_handle = ext_family.get_father_handle()
            if father_handle:
                father = self.database.get_person_from_handle(father_handle).get_primary_name().get_regular_name()
            else:
                father = ""
            mother_handle = ext_family.get_father_handle()
            if mother_handle:
                mother = self.database.get_person_from_handle(mother_handle).get_primary_name().get_regular_name()
            else:
                mother = ""

            if father or mother:
                if person.get_gender() == RelLib.Person.male:
                    if father:
                        if mother:
                            self.doc.write_text(_(" %s is the son of %s and %s.") % \
                                (firstName, father, mother))
                        else:
                            self.doc.write_text(_(" %s is the son of %s.") % \
                                (firstName, father))
                    else:
                        self.doc.write_text(_(" %s is the son of %s.") % \
                                (firstName, mother))
                else:
                    if father:
                        if mother:
                            self.doc.write_text(_(" %s is the daughter of %s and %s.") % \
                                (firstName, father, mother))
                        else:
                            self.doc.write_text(_(" %s is the daughter of %s.") % \
                                (firstName, father))
                    else:
                        self.doc.write_text(_(" %s is the daughter of %s.") % \
                                (firstName, mother))


    def write_marriage(self, person):
        """ Output marriage sentence
        HE/SHE married SPOUSE on FULLDATE in PLACE.
        HE/SHE married SPOUSE on FULLDATE.
        HE/SHE married SPOUSE in PLACE.
        HE/SHE married SPOUSE
        """
        famList = person.get_family_handle_list()
        if len(famList):
            fam_num= 0
            for fam_id in famList:
                fam = self.database.get_family_from_handle(fam_id)
                fam_num= fam_num + 1
                spouse = ""
                if person.get_gender() == RelLib.Person.male:
                    mother_handle = fam.get_mother_handle()
                    if mother_handle:
                        spouse = self.database.get_person_from_handle(mother_handle).get_primary_name().get_regular_name()
                    if fam_num == 1:
                        heshe = _("He")
                    elif fam_num < len(famList):
                        heshe = _(",")
                    else:
                        heshe = _("and he")
                else:
                    if fam_num == 1:
                        heshe = _("She")
                    elif fam_num < len(famList):
                        heshe = _(",")
                    else:
                        heshe = _("and she")

                    father_handle = fam.get_father_handle()
                    if father_handle:
                        spouse = self.database.get_person_from_handle(father_handle).get_primary_name().get_regular_name()

                for event_handle in fam.get_event_list():
                    if event_handle:
                        event = self.database.get_event_from_handle(event_handle)
                        if event.get_name() == "Marriage":
                            marriage = event
                            break
                else:
                    marriage = None

                fulldate = ""
                place = ""
                if marriage:
                    if marriage.get_place_handle():
                        place = self.database.get_place_from_handle(marriage.get_place_handle()).get_title()
                    elif self.blankPlace:
                        place= "____________"

                    date_obj = marriage.get_date_object()
                    if date_obj:
                        if date_obj.get_year_valid():
                            if date_obj.get_day_valid() and date_obj.get_month_valid() and \
                                    self.fullDate:
                                fulldate = marriage.get_date()
                            elif self.blankDate:
                                fulldate = "__________"

                if spouse:
                    if not fulldate and not place:
                        t = _("  %s married %s") % (heshe, spouse)
                    elif not fulldate and place:
                        t = _("  %s married %s in %s") % (heshe, spouse, place)
                    elif fulldate and not place:
                        t = _("  %s married %s on %s") % (heshe, spouse, fulldate)
                    else:
                        t = _("  %s married %s on %s in %s") % \
                            (heshe, spouse, fulldate, place)
                else:
                    if not fulldate and not place:
                        t = _("  %s married") % heshe
                    elif not fulldate and place:
                        t = _("  %s married in %s") % (heshe, place)
                    elif fulldate and not place:
                        t = _("  %s married on %s") % (heshe, fulldate)
                    else: 
                        t = _("  %s married on %s in %s") % \
                            (heshe, fulldate, place)

                if t: 
                    self.doc.write_text(t)
                if fam_num == len(famList):
                    self.doc.write_text(".")

    def write_mate(self, person):
        """Output birth, death, parentage, marriage and notes information """

        for fam_id in person.get_family_handle_list():
            fam = self.database.get_family_from_handle(fam_id)
            mate = ""
            if person.get_gender() == RelLib.Person.male:
                heshe = _("She")
                mother_handle = fam.get_mother_handle()
                if mother_handle:
                    mate = self.database.get_person_from_handle(mother_handle)
                    mateName = mate.get_primary_name().get_regular_name()
                    mateFirstName = mate.get_primary_name().get_first_name()
            else:
                heshe = _("He")
                father_handle = fam.get_father_handle()
                if father_handle:
                    mate = self.database.get_person_from_handle(father_handle)
                    mateName = mate.get_primary_name().get_regular_name()
                    mateFirstName = mate.get_primary_name().get_first_name()

            if mate:
                if self.addImages:
                    self.insert_images(mate)

                self.doc.start_paragraph("DDR-Entry")

                if not self.firstName:
                    mateFirstName = heshe

                self.doc.write_text(mateName)
                self.write_birth(mate)
                self.write_death(mate, mateFirstName)
                self.write_parents(mate, mateFirstName)
                self.doc.end_paragraph()


    #--------------------------------------------------------------------
    #
    #
    #
    #--------------------------------------------------------------------
    def insert_images(self, person):

        photos = person.get_media_list()
        for photo in photos :
            object_handle = photo.get_reference_handle()
            object = self.database.get_object_from_handle(object_handle)
            if object.get_mime_type()[0:5] == "image":
                file = object.get_path()
                self.doc.add_media_object(file,"row",4.0,4.0)

    #--------------------------------------------------------------------
    #
    #
    #
    #--------------------------------------------------------------------
    def write_report(self):
        self.cur_gen= 1
        self.apply_filter(self.start_person.get_handle(),1)

        name = self.start_person.get_primary_name().get_regular_name()

        famList = self.start_person.get_family_handle_list()
        spouseName= ""
        if len(famList):
            for fam_id in famList:
                fam = self.database.get_family_from_handle(fam_id)
                if self.start_person.get_gender() == RelLib.Person.male:
                    mother_handle = fam.get_mother_handle()
                    if mother_handle:
                        spouseName = self.database.get_person_from_handle(mother_handle).get_primary_name().get_first_name()
                else:
                    father_handle = fam.get_father_handle()
                    if father_handle:
                        spouseName = self.database.get_person_from_handle(father_handle).get_primary_name().get_first_name()

        self.doc.start_paragraph("DDR-Title")
        if spouseName:
            name = spouseName + _(" and ") + name

        title = _("Detailed Descendant Report for %s") % name
        self.doc.write_text(title)
        self.doc.end_paragraph()

        keys = self.map.keys()
        keys.sort()
        generation = 0
        need_header = 1

        for generation in xrange(len(self.genKeys)):
            if self.pgbrk and generation > 0:
                self.doc.page_break()
            self.doc.start_paragraph("DDR-Generation")
            t = _("%s Generation") % DetDescendantReport.gen[generation+1]
            self.doc.write_text(t)
            self.doc.end_paragraph()
            if self.childRef:
                self.prevGenIDs= self.genIDs.copy()
                self.genIDs.clear()


            for key in self.genKeys[generation]:
                person_handle = self.map[key]
                person = self.database.get_person_from_handle(person_handle)
                self.genIDs[person_handle]= key
                dupPerson= self.write_person(key)
                if dupPerson == 0:		# Is this a duplicate ind record
                    if self.listChildren and  \
                         len(person.get_family_handle_list()) > 0:
                        family_handle = person.get_family_handle_list()[0]
                        family = self.database.get_family_from_handle(family_handle)
                        self.write_children(family)

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class DetDescendantOptions(ReportOptions.ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.ReportOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'firstnameiop'  : 0,
            'fulldates'     : 1,
            'listc'         : 1,
            'incnotes'      : 1,
            'repplace'      : 0,
            'repdate'       : 0,
            'computeage'    : 1,
            'omitda'        : 1,
            'desref'        : 1,
            'incphotos'     : 0,
        }
        self.options_help = {
            'firstnameiop'  : ("=0/1","Whether to use first names instead of pronouns",
                            ["Do not use first names","Use first names"],
                            True),
            'fulldates'     : ("=0/1","Whether to use full dates instead of just year.",
                            ["Do not use full dates","Use full dates"],
                            True),
            'listc'         : ("=0/1","Whether to list children.",
                            ["Do not list children","List children"],
                            True),
            'incnotes'      : ("=0/1","Whether to include notes.",
                            ["Do not include notes","Include notes"],
                            True),
            'repplace'      : ("=0/1","Whether to replace missing Places with blanks.",
                            ["Do not replace missing Places","Replace missing Places"],
                            True),
            'repdate'       : ("=0/1","Whether to replace missing Dates with blanks.",
                            ["Do not replace missing Dates","Replace missing Dates"],
                            True),
            'computeage'    : ("=0/1","Whether to compute age.",
                            ["Do not compute age","Compute age"],
                            True),
            'omitda'        : ("=0/1","Whether to omit duplicate ancestors.",
                            ["Do not omit duplicates","Omit duplicates"],
                            True),
            'desref'        : ("=0/1","Whether to add descendant references in child list.",
                            ["Do not add references","Add references"],
                            True),
            'incphotos'     : ("=0/1","Whether to include images.",
                            ["Do not include images","Include images"],
                            True),
        }

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'gen'       : 10,
            'pagebbg'   : 0,
        }

    def make_default_style(self,default_style):
        """Make the default output style for the Detailed Descendant Report"""
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=16,bold=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set(pad=0.5)
        para.set_description(_('The style used for the title of the page.'))
        default_style.add_style("DDR-Title",para)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set(pad=0.5)
        para.set_description(_('The style used for the generation header.'))
        default_style.add_style("DDR-Generation",para)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=10,italic=0, bold=0)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        #para.set_header_level(3)
        para.set_left_margin(1.0)   # in centimeters
        para.set(pad=0.5)
        para.set_description(_('The style used for the children list title.'))
        default_style.add_style("DDR-ChildTitle",para)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=9)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0.0,lmargin=1.0,pad=0.25)
        para.set_description(_('The style used for the children list.'))
        default_style.add_style("DDR-ChildList",para)

        para = BaseDoc.ParagraphStyle()
        para.set(first_indent=0.0,lmargin=1.0,pad=0.25)
        para.set_description(_('The style used for the notes section header.'))
        default_style.add_style("DDR-NoteHeader",para)

        para = BaseDoc.ParagraphStyle()
        para.set(first_indent=0.5,lmargin=0.0,pad=0.25)
        default_style.add_style("DDR-Entry",para)

        para = BaseDoc.ParagraphStyle()
        para.set(first_indent=-1.0,lmargin=1.0,pad=0.25)
        para.set_description(_('The style used for the first personal entry.'))
        default_style.add_style("DDR-First-Entry",para)

    def add_user_options(self,dialog):
        """
        Override the base class add_user_options task to add a menu that allows
        the user to select the sort method.
        """

        # Pronoun instead of first name
        self.first_name_option = gtk.CheckButton(_("Use first names instead of pronouns"))
        self.first_name_option.set_active(self.options_dict['firstnameiop'])

        # Full date usage
        self.full_date_option = gtk.CheckButton(_("Use full dates instead of only the year"))
        self.full_date_option.set_active(self.options_dict['fulldates'])

        # Children List
        self.list_children_option = gtk.CheckButton(_("List children"))
        self.list_children_option.set_active(self.options_dict['listc'])

        # Print notes
        self.include_notes_option = gtk.CheckButton(_("Include notes"))
        self.include_notes_option.set_active(self.options_dict['incnotes'])

        # Replace missing Place with ___________
        self.place_option = gtk.CheckButton(_("Replace Place with ______"))
        self.place_option.set_active(self.options_dict['repplace'])

        # Replace missing dates with __________
        self.date_option = gtk.CheckButton(_("Replace Dates with ______"))
        self.date_option.set_active(self.options_dict['repdate'])

        # Add "Died at the age of NN" in text
        self.age_option = gtk.CheckButton(_("Compute age"))
        self.age_option.set_active(self.options_dict['computeage'])

        # Omit duplicate persons, occurs when distant cousins marry
        self.dupPersons_option = gtk.CheckButton(_("Omit duplicate ancestors"))
        self.dupPersons_option.set_active(self.options_dict['omitda'])

        #Add descendant reference in child list
        self.childRef_option = gtk.CheckButton(_("Add descendant reference in child list"))
        self.childRef_option.set_active(self.options_dict['desref'])

        #Add photo/image reference
        self.image_option = gtk.CheckButton(_("Include Photo/Images from Gallery"))
        self.image_option.set_active(self.options_dict['incphotos'])

        # Add new options. The first argument is the tab name for grouping options.
        # if you want to put everyting in the generic "Options" category, use
        # self.add_option(text,widget) instead of self.add_frame_option(category,text,widget)

        dialog.add_frame_option(_('Content'),'',self.first_name_option)
        dialog.add_frame_option(_('Content'),'',self.full_date_option)
        dialog.add_frame_option(_('Content'),'',self.list_children_option)
        dialog.add_frame_option(_('Content'),'',self.include_notes_option)
        dialog.add_frame_option(_('Content'),'',self.place_option)
        dialog.add_frame_option(_('Content'),'',self.date_option)
        dialog.add_frame_option(_('Content'),'',self.age_option)
        dialog.add_frame_option(_('Content'),'',self.dupPersons_option)
        dialog.add_frame_option(_('Content'),'',self.childRef_option)
        dialog.add_frame_option(_('Content'),'',self.image_option)

    def parse_user_options(self,dialog):
        """
        Parses the custom options that we have added.
        """

        self.options_dict['firstnameiop'] = int(self.first_name_option.get_active())
        self.options_dict['fulldates'] = int(self.full_date_option.get_active())
        self.options_dict['listc'] = int(self.list_children_option.get_active())
        self.options_dict['incnotes'] = int(self.include_notes_option.get_active())
        self.options_dict['repplace'] = int(self.place_option.get_active())
        self.options_dict['repdate'] = int(self.date_option.get_active())
        self.options_dict['computeage'] = int(self.age_option.get_active())
        self.options_dict['omitda'] = int(self.dupPersons_option.get_active())
        self.options_dict['desref'] = int(self.childRef_option.get_active())
        self.options_dict['incphotos'] = int(self.image_option.get_active())

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
from Plugins import register_report
register_report(
    name = 'det_descendant_report',
    category = const.CATEGORY_TEXT,
    report_class = DetDescendantReport,
    options_class = DetDescendantOptions,
    modes = Report.MODE_GUI | Report.MODE_BKI | Report.MODE_CLI,
    translated_name = _("Detailed Descendant Report"),
    status=(_("Beta")),
    description= _("Produces a detailed descendant report"),
    author_name="Bruce DeGrasse",
    author_email="bdegrasse1@attbi.com"
    )
