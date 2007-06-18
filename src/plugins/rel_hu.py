# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
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

#
# Written by Egyeki Gergely <egeri@elte.hu>, 2004
#
#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import RelLib
import Relationship
from PluginUtils import register_relcalc
import types
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Shared constants
#
#-------------------------------------------------------------------------

_level =\
    ["", "", "másod", "harmad", "negyed", "ötöd", "hatod",
     "heted", "nyolcad", "kilenced", "tized", "tizenegyed", "tizenketted",
     "tizenharmad", "tizennegyed", "tizenötöd", "tizenhatod",
     "tizenheted", "tizennyolcad", "tizenkilenced", "huszad","huszonegyed"]


#-------------------------------------------------------------------------
#
# Specific relationship functions
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self,db):
        Relationship.RelationshipCalculator.__init__(self,db)


    def get_parents (self,level):
        if   level == 0: return ""
        elif level == 1: return "szülei"
        elif level == 2: return "nagyszülei"
        elif level == 3: return "dédszülei"
        elif level == 4: return "ükszülei"
        else           : return "%s szülei" % _level[level]



    def get_father (self,level):
        if   level == 0: return ""
        elif level == 1: return "apja"
        elif level == 2: return "nagyapja"
        elif level == 3: return "dédapja"
        elif level == 4: return "ükapja"
        else           : return "%s ükapja" % (_level[level])

    def get_mother (self,level):
        if   level == 0: return ""
        elif level == 1: return "anyja"
        elif level == 2: return "nagyanyja"
        elif level == 3: return "dédanyja"
        elif level == 4: return "ükanyja"
        else           : return "%s ükanyja" % (_level[level])



    def get_son (self,level):
        if   level == 0: return ""
        elif level == 1: return "fia"
        elif level == 2: return "unokája"
        elif level == 3: return "dédunokája"
        elif level == 4: return "ükunokája"
        else           : return "%s unokája" % (_level[level])


    def get_daughter (self,level):
        if   level == 0: return ""
        elif level == 1: return "lánya"
        else           : return self.get_son(level)





    def get_uncle (self,level):
        if   level == 0: return ""
        elif level == 1: return "testvére"
        elif level == 2: return "nagybátyja"
        else           : return "%s nagybátyja" % (_level[level])


    def get_aunt (self,level):
        if   level == 0: return ""
        elif level == 1: return "testvére"
        elif level == 2: return "nagynénje"
        else           : return "%s nagynénje" % (_level[level])




    def get_nephew (self,level):
        if   level == 0: return ""
        elif level == 1: return "unokája"
        else           : return "%s unokája" % (_level[level])

    def get_niece(self,level):
        return self.get_nephew(level)




    def get_male_cousin (self,level):
        if   level == 0: return ""
        elif level == 1: return "unokatestvére"
        else           : return "%s unokatestvére" % (_level[level])

    def get_female_cousin (self,level):
        return self.get_male_cousin(level)

    #----------------------------------------------
    #
    # brother and sister age differences
    #
    #----------------------------------------------

    def get_age_comp(self,orig_person,other_person):
        # 0=nothing, -1=other is younger 1=other is older
        orig_birth_event = orig_person.get_birth()
        orig_birth_date = orig_birth_event.get_date_object()
        other_birth_event = other_person.get_birth()
        other_birth_date = other_birth_event.get_date_object()
        if (orig_birth_date == "")or(other_birth_date == "") :return 0
        else  :return orig_birth_date>other_birth_date
          

    def get_age_brother (self,level):
        if   level == 0  : return "testvére"
        elif level == 1  : return "öccse"
        else             : return "bátyja"

    def get_age_sister (self,level):
        if   level == 0  : return "testvére"
        elif level == 1  : return "húga"
        else             : return "nővére"

    #---------------------------------------------
    #
    # en: father-in-law, mother-in-law, son-in-law, daughter-in-law  
    # hu: após, anyós, vő, meny
    #
    #---------------------------------------------

    def is_fathermother_in_law(self,orig,other):
        for f in other.get_family_handle_list():
            family = self.db.get_family_from_handle(f)
            sp_id = None
            if family:
                if other == family.get_father_handle(): 
                    sp_id = family.get_mother_handle()
                elif other == family.get_mother_handle(): 
                    sp_id = family.get_father_handle()
                for g in orig.get_family_handle_list():
                    family = self.db.get_family_from_handle(g)
                    if family:
                        if sp_id in family.get_child_handle_list(): 
                            return 1
        return 0

    def get_fathermother_in_law_common(self,orig,other):
        for f in other.get_family_handle_list():
            family = self.db.get_family_from_handle(f)
            sp_id = None
            if family:
                if other == family.get_father_handle(): 
                    sp_id = family.get_mother_handle()
                elif other == family.get_mother_handle(): 
                    sp_id = family.get_father_handler()
                for g in orig.get_family_handle_list():
                    family = self.db.get_family_from_handle(g)
                    if family:
                        if sp_id in family.get_child_handle_list(): 
                            return [sp_id]
        return []

    #------------------------------------------------------------------------
    #
    # hu: sógor, sógornő
    # en: brother-in-law, sister-in-law
    #
    #------------------------------------------------------------------------

    def is_brothersister_in_law(self,orig,other):
        for f in orig.get_family_handle_list():
            family = self.db.get_family_from_handle(f)
            sp_id = None
            if family:
                if orig ==  family.get_father_handle(): 
                    sp_id = family.get_mother_handle()
                elif other == family.get_mother_handle(): 
                    sp_id = family.get_father_handler()

                p = other.get_main_parents_family_handle()
                family = self.db.get_family_from_handle(p)
                if family:
                    c = family.get_child_handle_list()
                    if (other.get_handle() in c) and (sp_id in c): 
                        return 1
        return 0

    def get_brothersister_in_law_common(self,orig,other):
        for f in orig.get_family_handle_list():
            family = self.db.get_family_from_handle(f)
            sp_id = None
            if family:
                if orig ==  family.get_father_handle(): 
                    sp_id = family.get_mother_handle()
                elif other == family.get_mother_handle(): 
                    sp_id = family.get_father_handler()

                p = other.get_main_parents_family_handle()
                family = self.db.get_family_from_handle(p)
                if family:
                    c = family.get_child_handle_list()
                if (other.get_handle() in c) and (sp_id in c): 
                    return [sp_id]
        return []

    #-------------------------------------------------------------------------
    #
    # get_relationship
    #
    #-------------------------------------------------------------------------

    def get_relationship(self,orig_person,other_person):
        """
        returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother)
        """

        if orig_person == None:
            return ("undefined",[])

        if orig_person.get_handle() == other_person.get_handle():
            return ('', [])

        is_spouse = self.is_spouse(orig_person,other_person)
        if is_spouse:
            return (is_spouse,[])

        if self.is_fathermother_in_law(other_person,orig_person):
            if other_person.getGender() == RelLib.Person.MALE:
                return ("apósa",self.get_fathermother_in_law_common(other_person,orig_person))
            elif other_person.getGender() == RelLib.Person.FEMALE:
                return ("anyósa",self.get_fathermother_in_law_common(other_person,orig_person))
            elif other_person.getGender() == 2 :
                return ("apósa vagy anyósa",self.get_fathermother_in_law_common(other_person,orig_person))

        if self.is_fathermother_in_law(orig_person,other_person):
            if orig_person.getGender() == RelLib.Person.MALE:
                return ("veje",self.get_fathermother_in_law_common(orig_person,other_person))
            elif orig_person.getGender() == RelLib.Person.FEMALE:
                return ("menye",self.get_fathermother_in_law_common(orig_person,other_person))
            elif orig_person.getGender() == 2 :
                return ("veje vagy menye",self.get_fathermother_in_law_common(orig_person,other_person))

        if self.is_brothersister_in_law(orig_person,other_person):
            if other_person.getGender() == RelLib.Person.MALE:
                return ("sógora",self.get_brothersister_in_law_common(orig_person,other_person))
            elif other_person.getGender() == RelLib.Person.FEMALE:
                return ("sógornője",self.get_brothersister_in_law_common(orig_person,other_person))
            elif other_person.getGender() == 2 :
                return ("sógora vagy sógornője",self.get_brothersister_in_law_common(orig_person,other_person))


        (firstRel,secondRel,common) = self.get_relationship_distance(orig_person,other_person)
        
        if type(common) == types.StringType or type(common) == types.UnicodeType:
            return (common,[])
        elif common:
            person_handle = common[0]
        else:
            return ("",[])

        firstRel = len(firstRel)
        secondRel = len(secondRel)

        if firstRel == 0:
            if secondRel == 0:
                return ('',common)
            elif other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_father(secondRel),common)
            else:
                return (self.get_mother(secondRel),common)

        elif secondRel == 0:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_son(firstRel),common)
            else:
                return (self.get_daughter(firstRel),common)

        elif firstRel == 1:
            if other_person.get_gender() == RelLib.Person.MALE:
                if secondRel == 1:
                    return (self.get_age_brother(self.get_age_comp(orig_person,other_person)),common)
                else :return (self.get_uncle(secondRel),common)
            else:
                if secondRel == 1:
                    return (self.get_age_sister(self.get_age_comp(orig_person,other_person)),common)
                else :return (self.get_aunt(secondRel),common)

        elif secondRel == 1:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_nephew(firstRel-1),common)
            else:
                return (self.get_niece(firstRel-1),common)

        else:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_male_cousin(firstRel-1), common)
            else:
                return (self.get_female_cousin(firstRel-1), common)


#-------------------------------------------------------------------------
#
# Function registration
#
#-------------------------------------------------------------------------

register_relcalc(RelationshipCalculator,
    ["hu", "HU", "hu_HU", "hu_HU.utf8", "hu_HU.UTF8"])

# Local variables:
# buffer-file-coding-system: utf-8
# End:
