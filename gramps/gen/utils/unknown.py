#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
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
Make an 'Unknown' primary object
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from time import strftime, localtime, time
import os

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..lib import (Person, Surname, Name, NameType, Family, FamilyRelType,
                   Event, EventType, Source, Place, Citation,
                   Repository, RepositoryType, Media, Note, NoteType,
                   StyledText, StyledTextTag, StyledTextTagType, Tag,
                   ChildRef, ChildRefType)
from .id import create_id
from ..const import IMAGE_DIR
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# make_unknown
#
#-------------------------------------------------------------------------
def make_unknown(class_arg, explanation, class_func, commit_func, transaction,
                 **argv):
    """
    Make a primary object and set some property so that it qualifies as
    "Unknown".

    Some object types need extra parameters:
    Family: db, Event: type (optional),
    Citation: methods to create/store source.

    Some theoretical underpinning
    This function exploits the fact that all import methods basically do the
    same thing: Create an object of the right type, fill it with some
    attributes, store it in the database. This function does the same, so
    the observation is why not use the creation and storage methods that the
    import routines use themselves, that makes nice reuse of code. To do this
    formally correct we would need to specify a interface (in the OOP sence)
    which the import methods would need to implement. For now, that is deemed
    too restrictive and here we just slip through because of the similarity in
    code of both GEDCOM and XML import methods.

    :param class_arg: The argument the class_func needs, typically a kind of id.
    :type class_arg: unspecified
    :param explanation: Handle of a note that explains the origin of primary obj
    :type explanation: str
    :param class_func: Method to create primary object.
    :type class_func: method
    :param commit_func: Method to store primary object in db.
    :type commit_func: method
    :param transactino: Database transaction handle
    :type transaction: str
    :param argv: Possible additional parameters
    :type param: unspecified
    :returns: List of newly created objects.
    :rtype: list
    """
    retval = []
    obj = class_func(class_arg)
    if isinstance(obj, Person):
        surname = Surname()
        surname.set_surname('Unknown')
        name = Name()
        name.add_surname(surname)
        name.set_type(NameType.UNKNOWN)
        obj.set_primary_name(name)
    elif isinstance(obj, Family):
        obj.set_relationship(FamilyRelType.UNKNOWN)
        handle = obj.handle
        if getattr(argv['db'].transaction, 'no_magic', False):
            backlinks = argv['db'].find_backlink_handles(
                    handle, [Person.__name__])
            for dummy, person_handle in backlinks:
                person = argv['db'].get_person_from_handle(person_handle)
                add_personref_to_family(obj, person)
        else:
            for person in argv['db'].iter_people():
                if person._has_handle_reference('Family', handle):
                    add_personref_to_family(obj, person)
    elif isinstance(obj, Event):
        if 'type' in argv:
            obj.set_type(argv['type'])
        else:
            obj.set_type(EventType.UNKNOWN)
    elif isinstance(obj, Place):
        obj.set_title(_('Unknown'))
        obj.name.set_value(_('Unknown'))
    elif isinstance(obj, Source):
        obj.set_title(_('Unknown'))
    elif isinstance(obj, Citation):
        #TODO create a new source for every citation?
        obj2 = argv['source_class_func'](argv['source_class_arg'])
        obj2.set_title(_('Unknown'))
        obj2.add_note(explanation)
        argv['source_commit_func'](obj2, transaction, time())
        retval.append(obj2)
        obj.set_reference_handle(obj2.handle)
    elif isinstance(obj, Repository):
        obj.set_name(_('Unknown'))
        obj.set_type(RepositoryType.UNKNOWN)
    elif isinstance(obj, Media):
        obj.set_path("image-missing.png")
        obj.set_mime_type('image/png')
        obj.set_description(_('Unknown'))
    elif isinstance(obj, Note):
        obj.set_type(NoteType.UNKNOWN);
        text = _('Unknown, created to replace a missing note object.')
        link_start = text.index(',') + 2
        link_end = len(text) - 1
        tag = StyledTextTag(StyledTextTagType.LINK,
                'gramps://Note/handle/%s' % explanation,
                [(link_start, link_end)])
        obj.set_styledtext(StyledText(text, [tag]))
    elif isinstance(obj, Tag):
        if not hasattr(make_unknown, 'count'):
            make_unknown.count = 1 #primitive static variable
        obj.set_name(_("Unknown, was missing %(time)s (%(count)d)") % {
                'time': strftime('%x %X', localtime()),
                'count': make_unknown.count})
        make_unknown.count += 1
    else:
        raise TypeError("Object if of unsupported type")

    if hasattr(obj, 'add_note'):
        obj.add_note(explanation)
    commit_func(obj, transaction, time())
    retval.append(obj)
    return retval

def create_explanation_note(dbase):
    """
    When creating objects to fill missing primary objects in imported files,
    those objects of type "Unknown" need a explanatory note. This funcion
    provides such a note for import methods.
    """
    note = Note( _('Objects referenced by this note '
                                    'were missing in a file imported on %s.') %
                                    strftime('%x %X', localtime()))
    note.set_handle(create_id())
    note.set_gramps_id(dbase.find_next_note_gramps_id())
    # Use defaults for privacy, format and type.
    return note

def add_personref_to_family(family, person):
    """
    Given a family and person, set the parent/child references in the family,
    that match the person.
    """
    handle = family.handle
    person_handle = person.handle
    if handle in person.get_family_handle_list():
        if ((person.get_gender() == Person.FEMALE) and
                (family.get_mother_handle() is None)):
            family.set_mother_handle(person_handle)
        else:
            # This includes cases of Person.UNKNOWN
            if family.get_father_handle() is None:
                family.set_father_handle(person_handle)
            else:
                family.set_mother_handle(person_handle)
    if handle in person.get_parent_family_handle_list():
        childref = ChildRef()
        childref.set_reference_handle(person_handle)
        childref.set_mother_relation(ChildRefType.UNKNOWN)
        childref.set_father_relation(ChildRefType.UNKNOWN)
        family.add_child_ref(childref)
