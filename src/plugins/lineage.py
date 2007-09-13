#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Jerome Rapinat, B. Malengier
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

# $Id: _FamilyList.py 8897 2007-08-30 19:49:04Z bmcage $

"""
Display a person's father or mother lineage
"""

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------

import RelLib
from Simple import SimpleAccess, SimpleDoc
from gettext import gettext as _
from PluginUtils import register_quick_report
from ReportBase import CATEGORY_QR_PERSON

__FMT     = "%-30s\t%-12s\t%-12s"
__FMT_REM = "   %s: %s"
__MAX_GEN = 100

def run_father(database, document, person):
    """ Function writing the father lineage quick report
    """
    sa = SimpleAccess(database)
    sd = SimpleDoc(document)

    # display the results

    sd.title(_("Father lineage for %s") % sa.name(person))
    sd.paragraph("")
    sd.paragraph(_(""
        "This report shows the father lineage, also called patronymic lineage"
        " or Y-line."
        " People in this lineage all share the same Y-chromosone."
        ))
    sd.paragraph("")
    
    sd.header2(__FMT %(_("Name Father"), _("Birth Date"), _("Death Date")))
    sd.paragraph("")
    
    make_details(RelLib.Person.MALE, person, sa, sd, database)
    
    sd.paragraph("")
    sd.paragraph("")
    
    if person.gender == RelLib.Person.FEMALE :
        return
    
    sd.header2((_("Direct line male descendants")))
    sd.paragraph("")
    
    make_details_child(RelLib.Person.MALE, person, sa, sd, database)
    
def run_mother(database, document, person):
    """ Function writing the mother lineage quick report
    """
    sa = SimpleAccess(database)
    sd = SimpleDoc(document)

    # display the results

    sd.title(_("Mother lineage for %s") % sa.name(person))
    sd.paragraph("")
    sd.paragraph(_(""
        "This report shows the mother lineage, also called matronymic lineage "
        "or M-line."
        " People in this lineage all share the same RNA."
        ))
    sd.paragraph("")
    
    sd.header2(__FMT %(_("Name Mother"), _("Birth"), _("Death Date")))
    sd.paragraph("")
    
    make_details(RelLib.Person.FEMALE, person, sa, sd, database)
    
    sd.paragraph("")
    sd.paragraph("")
    
    if person.gender == RelLib.Person.MALE :
        return
    
    sd.header2((_("Direct line female descendants")))
    sd.paragraph("")
    
    make_details_child(RelLib.Person.FEMALE, person, sa, sd, database)
    
def make_details(gender, person, sa, sd, database) :
    """ Function writing one line of ancestry on the document in 
        direct lineage
    """
    # avoid infinite loop: 
    personsprinted = 0
    
    # loop as long as there are fathers/mothers
    rem_str = ""
    while person:
        person_handle = person.handle
        sd.paragraph(__FMT % (sa.name(person), sa.birth_date(person),
                            sa.death_date(person)))
        if rem_str:
            sd.paragraph(__FMT_REM % (_("Remark"), rem_str))

        personsprinted += 1
        if personsprinted > __MAX_GEN :
            sd.paragraph("")
            sd.paragraph(_("ERROR : Too many levels in the tree "
                        "(perhaps a loop?)."))
            return
            
        # obtain the first father/mother we find in the list
        parent_handle_list = person.get_parent_family_handle_list()
        person = None
        for parent in parent_handle_list:
            rem_str = ""
            family_id = parent_handle_list[0]
            family = database.get_family_from_handle(family_id)
            childrel = [(ref.get_mother_relation(), 
                            ref.get_father_relation()) for ref in 
                            family.get_child_ref_list() 
                            if ref.ref == person_handle]
            if gender == RelLib.Person.MALE :
                person = database.get_person_from_handle(
                            family.get_father_handle())
                refnr  = 1
            else :
                person = database.get_person_from_handle(
                            family.get_mother_handle())
                refnr  = 0
            
            #We do not allow for same sex marriages when going up
            # that would complicate the code
            #Also, we assume the birth relation is in the FIRST
            # family of the person, so we go up on non-birth
            if not childrel[0][refnr] == RelLib.ChildRefType.BIRTH :
                rem_str = add_rem(rem_str, _("No birth relation with child"))
            if person and person.gender == gender :
                break
            elif person and person.gender == RelLib.Person.UNKNOWN :
                rem_str = add_rem(rem_str, _("Unknown gender"))
                break
            else :
                person = None

def make_details_child(gender, person, sa, sd, database) :
    """ Function that prints the details of the children in the 
        male/female lineage
    """
    def make_child_line(child, prepend, gen) :
        """ Recursively called funcion to write one child line
            Person is the child, prepend is the string that preceeds it
            on print. As the recursion grows, prepend is increased
            Gen is the generation level
        """
        if gen > __MAX_GEN :
            raise RuntimeError
        #we use some global var from make_details_child !
        rem_str = ""
        if child.gender == RelLib.Person.UNKNOWN :
            rem_str = add_rem(rem_str, _("Unknown gender"))
            
        if rem_str : 
            rem_str = _("Remark")+": "+rem_str
        front = ""
        if prepend :
            front = prepend + "-"
        sd.paragraph(front + "%s (%s - %s) %s" % (sa.name(child),
                            sa.birth_date(child),
                            sa.death_date(child), rem_str))
        #obtain families in which child is a parent
        family_handles = child.get_family_handle_list()
        for fam_handle in family_handles :
            fam = database.get_family_from_handle(fam_handle)
            #what parent is the previous child? We are fancy and allow
            # for same sex marriage
            if fam.get_father_handle() == child.handle :
                childrelnr = 2
            elif fam.get_mother_handle() == child.handle :
                childrelnr = 1
            else :
                #something wrong with this family, continue with next
                continue
            childrel = [(ref.ref, ref.get_mother_relation(), 
                        ref.get_father_relation()) for ref in 
                            fam.get_child_ref_list()]
            for childdet in childrel: 
                #relation with parent must be by birth
                if not childdet[childrelnr] == RelLib.ChildRefType.BIRTH :
                    continue
                            
                newchild = database.get_person_from_handle(childdet[0])
                # person must have the required gender
                if newchild and newchild.gender == gender :
                    make_child_line(newchild, prepend + '  |', gen+1)
                    
    # loop over all children of gender and output, start with no prepend
    try :
        make_child_line(person, "", 0)
    except RuntimeError:
        sd.paragraph("")
        sd.paragraph(_("ERROR : Too many levels in the tree "
                        "(perhaps a loop?)."))

def add_rem(remark, text):
    """ Allow for extension of remark, return new remark string
    """
    if remark:
        return remark + ', ' + text
    else:
        return text
  
#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------

register_quick_report(
    name = 'father_lineage',
    category = CATEGORY_QR_PERSON,
    run_func = run_father,
    translated_name = _("Father lineage"),
    status = _("Stable"),
    description= _("Display father lineage"),
    author_name="B. Malengier",
    author_email="benny.malengier@gramps-project.org"
    )

register_quick_report(
    name = 'mother_lineage',
    category = CATEGORY_QR_PERSON,
    run_func = run_mother,
    translated_name = _("Mother lineage"),
    status = _("Stable"),
    description= _("Display mother lineage"),
    author_name="B. Malengier",
    author_email="benny.malengier@gramps-project.org"
    )
    