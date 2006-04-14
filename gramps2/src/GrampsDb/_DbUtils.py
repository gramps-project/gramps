#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006 Donald N. Allingham
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

# $Id: __init__.py 6086 2006-03-06 03:54:58Z dallingham $


import RelLib

def remove_family_relationships(db, family_handle, trans=None):
    family = db.get_family_from_handle(family_handle)

    if trans == None:
        need_commit = True
        trans = db.transaction_begin()
    else:
        need_commit = False

    for phandle in [ family.get_father_handle(),
                     family.get_mother_handle()]:
        if phandle:
            person = db.get_person_from_handle(phandle)
            person.remove_family_handle(family_handle)
            db.commit_person(person, trans)

    for phandle in family.get_child_handle_list():
        person = db.get_person_from_handle(phandle)
        person.remove_parent_family_handle(family_handle)
        db.commit_person(person, trans)

    db.remove_family(family_handle, trans)
    
    if need_commit:
        db.transaction_commit(trans, _("Remove Family"))

def remove_parent_from_family(db, person_handle, family_handle, trans=None):
    """
    Removes a person as either the father or mother of a family,
    deleting the family if it becomes empty.
    """
    person = db.get_person_from_handle(person_handle)
    family = db.get_family_from_handle(family_handle)

    if trans == None:
        need_commit = True
        trans = db.transaction_begin()
    else:
        need_commit = False

    person.remove_family_handle(family_handle)
    if family.get_father_handle() == person_handle:
        family.set_father_handle(None)
    elif family.get_mother_handle() == person_handle:
        family.set_mother_handle(None)

    child_list = family.get_child_handle_list()
    if (not family.get_father_handle() and not family.get_mother_handle() and
        len(child_list) <= 1):
        db.remove_family(family_handle, trans)
        if child_list:
            child = db.get_person_from_handle(child_list[0])
            child.remove_parent_family_handle(family_handle)
            db.commit_person(child, trans)
        msg = _("Remove father from family")
    else:
        db.commit_family(family, trans)
        msg = _("Remove mother from family")
    db.commit_person(person, trans)
    
    if need_commit:
        db.transaction_commit(trans,msg)

def remove_child_from_family(db, person_handle, family_handle, trans=None):
    """
    Removes a person as a child of the family, deleting the family if
    it becomes empty.
    """
    person = db.get_person_from_handle(person_handle)
    family = db.get_family_from_handle(family_handle)
    person.remove_parent_family_handle(family_handle)
    family.remove_child_handle(person_handle)

    if trans == None:
        need_commit = True
        trans = db.transaction_begin()
    else:
        need_commit = False
        
    child_list = family.get_child_handle_list()
    if (not family.get_father_handle() and not family.get_mother_handle() and
        len(child_list) <= 1):
        db.remove_family(family_handle, trans)
        if child_list:
            child = db.get_person_from_handle(child_list[0])
            child.remove_parent_family_handle(family_handle)
            db.commit_person(child, trans)
    else:
        db.commit_family(family, trans)
    db.commit_person(person, trans)
    
    if need_commit:
        db.transaction_commit(trans,_("Remove child from family"))


def add_child_to_family(db, family, child,
                        mrel=RelLib.ChildRefType(),
                        frel=RelLib.ChildRefType(),
                        trans=None):

    family.add_child_handle(child.handle)
    child.add_parent_family_handle(family.handle, mrel, frel )

    if trans == None:
        need_commit = True
        trans = db.transaction_begin()
    else:
        need_commit = False

    db.commit_family(family,trans)
    db.commit_person(person,trans)

    if need_commit:
        db.transaction_commit(trans, _('Add child to family') )
