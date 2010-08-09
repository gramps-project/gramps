#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Peter G. Landgren
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

"""
Provide the SubstKeywords class that will replace keywords in a passed
string with information about the person. For sample:

foo = SubstKeywords(person)
print foo.replace('$n was born on $b.')

Will return a value such as:

Mary Smith was born on 3/28/1923.
"""

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gen.display.name import displayer as name_displayer
import DateHandler
import gen.lib
from gen.utils import get_birth_or_fallback, get_death_or_fallback

#------------------------------------------------------------------------
#
# SubstKeywords
#
#------------------------------------------------------------------------
class SubstKeywords(object):
    """
    Produce an object that will substitute information about a person
    into a passed string.

    $n -> Name - FirstName LastName
    $N -> Name - LastName, FirstName
    $nC -> Name - FirstName LastName in UPPER case
    $NC -> Name - LastName in UPPER case, FirstName
    $f -> Name - as by Gramps name display under Preferences
    $i -> GRAMPS ID
    $by -> Date of birth, year only
    $b -> Date of birth
    $B -> Place of birth
    $d -> Date of death
    $dy -> Date of death, year only
    $D -> Place of death
    $p -> Preferred spouse's name as by Gramps name display under Preferences
    $s -> Preferred spouse's name - FirstName LastName
    $S -> Preferred spouse's name - LastName, FirstName
    $sC -> Preferred spouse's name - FirstName LastName in UPPER case
    $SC -> Preferred spouse's name - LastName in UPPER case, FirstName
    $my -> Date of preferred marriage, year only
    $m -> Date of preferred marriage
    $M -> Place of preferred marriage
    """
    
    def __init__(self, database, person_handle):
        """Create a new object and associates a person with it."""

        person = database.get_person_from_handle(person_handle)
        self.n = person.get_primary_name().get_first_name() + " " + \
            person.get_primary_name().get_surname() #Issue ID:  2878
        self.N = person.get_primary_name().get_surname() + ", " + \
            person.get_primary_name().get_first_name()
        self.nC = person.get_primary_name().get_first_name() + " " + \
            person.get_primary_name().get_surname().upper() #Issue ID:  4124
        self.NC = person.get_primary_name().get_surname().upper() + ", " + \
            person.get_primary_name().get_first_name()      #Issue ID:  4124
        self.f = name_displayer.display_formal(person)      #Issue ID:  4124
        self.by = ""
        self.b = ""
        self.B = ""
        self.dy = ""
        self.d = ""
        self.D = ""
        self.s = ""
        self.S = ""
        self.sC = ""
        self.SC = ""
        self.p = ""
        self.my = ""
        self.m = ""
        self.M = ""
        
        birth = get_birth_or_fallback(database, person)
        if birth:
            self.b = DateHandler.get_date(birth)
            tempdate = birth.get_date_object().get_year()
            if tempdate != 0:
                self.by = unicode(tempdate)
            bplace_handle = birth.get_place_handle()
            if bplace_handle:
                self.B = database.get_place_from_handle(bplace_handle).get_title()
        death = get_death_or_fallback(database, person)
        if death:
            self.d = DateHandler.get_date(death)
            tempdate = death.get_date_object().get_year()
            if tempdate != 0:
                self.dy = unicode(tempdate)
            dplace_handle = death.get_place_handle()
            if dplace_handle:
                self.D = database.get_place_from_handle(dplace_handle).get_title()
        self.i = person.get_gramps_id()

        if person.get_family_handle_list():
            f_id = person.get_family_handle_list()[0]
            f = database.get_family_from_handle(f_id)
            father_handle = f.get_father_handle()
            mother_handle = f.get_mother_handle()
            if father_handle == person_handle:
                if mother_handle:
                    mother = database.get_person_from_handle(mother_handle)
                    self.s = mother.get_primary_name().get_first_name() + " " + \
                        mother.get_primary_name().get_surname() #Issue ID:  2878
                    self.S = mother.get_primary_name().get_surname() + ", " + \
                        mother.get_primary_name().get_first_name()
                    self.sC = mother.get_primary_name().get_first_name() + " " + \
                        mother.get_primary_name().get_surname().upper() #Issue ID:  4124
                    self.SC = mother.get_primary_name().get_surname().upper() + ", " + \
                        mother.get_primary_name().get_first_name()      #Issue ID:  4124
                    self.p = name_displayer.display_formal(mother)      #Issue ID:  4124
      
            else:
                if father_handle:
                    father = database.get_person_from_handle(father_handle)
                    self.s = father.get_primary_name().get_first_name() + " " + \
                        father.get_primary_name().get_surname() #Issue ID:  2878
                    self.S = father.get_primary_name().get_surname() + ", " + \
                        father.get_primary_name().get_first_name()
                    self.sC = father.get_primary_name().get_first_name() + " " + \
                        father.get_primary_name().get_surname().upper() #Issue ID:  4124
                    self.SC = father.get_primary_name().get_surname().upper() + ", " + \
                        father.get_primary_name().get_first_name()      #Issue ID:  4124
                    self.p = name_displayer.display_formal(father)      #Issue ID:  4124

            for e_ref in f.get_event_ref_list():
                if not e_ref:
                    continue
                e = database.get_event_from_handle(e_ref.ref)
                if e.get_type() == gen.lib.EventType.MARRIAGE:
                    self.m = DateHandler.get_date(e)
                    tempdate = e.get_date_object().get_year()
                    if tempdate != 0:
                        self.my = unicode(tempdate)
                    mplace_handle = e.get_place_handle()
                    if mplace_handle:
                        self.M = database.get_place_from_handle(mplace_handle).get_title()

    def replace(self, line):
        """Return a new line of text with the substitutions performed."""
        array = [
                    ("$nC", self.nC), ("$NC", self.NC),
                    ("$n", self.n), ("$N", self.N),
                    ("$f", self.f), 
                    ("$by", self.by), 
                    ("$b", self.b), ("$B", self.B),
                    ("$dy", self.dy), 
                    ("$d", self.d), ("$D", self.D), 
                    ("$i", self.i),
                    ("$sC", self.sC), ("$SC", self.SC), 
                    ("$S", self.S), ("$s", self.s), 
                    ("$p", self.p), 
                    ("$my", self.my), 
                    ("$m", self.m), ("$M", self.M),
                    ("$$", "$") ]

        for (key, value) in array:
            line = line.replace(key, value)
        return line

    def replace_and_clean(self, lines):
        array = [
                    ("%nC", self.nC), ("%NC", self.NC),
                    ("%n", self.n), ("%N", self.N),
                    ("%f", self.f), 
                    ("%by", self.by), 
                    ("%b", self.b), ("%B", self.B),
                    ("%dy", self.dy), 
                    ("%d", self.d), ("%D", self.D), 
                    ("%i", self.i),
                    ("%sC", self.sC), ("%SC", self.SC), 
                    ("%S", self.S), ("%s", self.s), 
                    ("%p", self.p),
                    ("%my", self.my), 
                    ("%m", self.m), ("%M", self.M) ]

        new = []
        for line in lines:
            remove = False
            for (key, value) in array:
                if line.find(key) != -1:
                    if value:
                        line = line.replace(key, value)
                    else:
                        remove = True
            if not remove:
                new.append(self.replace(line))
        if len(new) == 0:
            return [ u"" ]
        else:
            return new
            
        
        
