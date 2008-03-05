#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Brian G. Matherly
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
Display filtered data
"""

from Simple import SimpleAccess, SimpleDoc, SimpleTable
from PluginUtils import register_quick_report
from Utils import media_path_full
from QuickReports import run_quick_report_by_name_direct
from gen.lib import Person
import DateHandler

import posixpath
from gettext import gettext as _

def run(database, document, filter_name):
    """
    Loops through the families that the person is a child in, and display
    the information about the other children.
    """
    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = SimpleTable(sdb, sdoc)
    # display the title
    sdoc.title(_("Filtering on %s") % filter_name)
    sdoc.paragraph("")
    matches = 0
    if (filter_name == 'all people'):
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        people = database.get_person_handles(sort_handles=False)
        for person_handle in people:
            person = database.get_person_from_handle(person_handle)
            stab.row(person, sdb.birth_date_obj(person),
                     str(person.get_primary_name().get_type()))
            matches += 1
    elif (filter_name == 'males'):
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        people = database.get_person_handles(sort_handles=False)
        for person_handle in people:
            person = database.get_person_from_handle(person_handle)
            if person.gender == Person.MALE:
                stab.row(person, sdb.birth_date_obj(person),
                         str(person.get_primary_name().get_type()))
                matches += 1
    elif (filter_name == 'females'):
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        people = database.get_person_handles(sort_handles=False)
        for person_handle in people:
            person = database.get_person_from_handle(person_handle)
            if person.gender == Person.FEMALE:
                stab.row(person, sdb.birth_date_obj(person),
                         str(person.get_primary_name().get_type()))
                matches += 1
    elif (filter_name == 'people with unknown gender'):
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        people = database.get_person_handles(sort_handles=False)
        for person_handle in people:
            person = database.get_person_from_handle(person_handle)
            if person.gender not in [Person.FEMALE, Person.MALE]:
                stab.row(person, sdb.birth_date_obj(person),
                         str(person.get_primary_name().get_type()))
                matches += 1
    elif (filter_name == 'people with incomplete names'):
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        people = database.get_person_handles(sort_handles=False)
        for person_handle in people:
            person = database.get_person_from_handle(person_handle)
            for name in [person.get_primary_name()] + person.get_alternate_names():
                if name.get_surname() == "" or name.get_first_name() == "":
                    stab.row(person, sdb.birth_date_obj(person),
                             str(person.get_primary_name().get_type()))
                    matches += 1
    elif (filter_name == 'people with missing birth dates'):
        stab.columns(_("Person"), _("Type"))
        people = database.get_person_handles(sort_handles=False)
        for person_handle in people:
            person = database.get_person_from_handle(person_handle)
            if person:
                birth_ref = person.get_birth_ref()
                if birth_ref:
                    birth = database.get_event_from_handle(birth_ref.ref)
                    if not DateHandler.get_date(birth):
                        stab.row(person, "birth event but no date")
                        matches += 1
                else:
                    stab.row(person, "missing birth event")
                    matches += 1
    elif (filter_name == 'disconnected people'):
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        people = database.get_person_handles(sort_handles=False)
        for person_handle in people:
            person = database.get_person_from_handle(person_handle)
            if person:
                if ((not person.get_main_parents_family_handle()) and 
                    (not len(person.get_family_handle_list()))):
                    stab.row(person, sdb.birth_date_obj(person),
                             str(person.get_primary_name().get_type()))
                    matches += 1
    elif (filter_name == 'all families'):
        familyList = database.get_family_handles()
        stab.columns(_("Family"))
        for family_handle in familyList:
            family = database.get_family_from_handle(family_handle)
            if family:
                stab.row(family)
                matches += 1
    elif (filter_name == 'unique surnames'):
        namelist = {}
        people = database.get_person_handles(sort_handles=False)
        for person_handle in people:
            person = database.get_person_from_handle(person_handle)
            if person:
                name = person.get_primary_name()
                if name:
                    surname = name.get_surname()
                    if surname:
                        namelist[surname] = namelist.get(surname, 0) + 1
        surnames = namelist.keys()
        surnames.sort()
        stab.columns(_("Surname"), _("Count"))
        for name in surnames:
            stab.row(name, namelist[name])
            matches += 1
        stab.set_callback("leftdouble", 
            lambda name: run_quick_report_by_name_direct("samesurnames",
                                                         database,
                                                         document,
                                                         name))
    elif (filter_name == 'people with media'):
        stab.columns(_("Person"), _("Media count"))
        people = database.get_person_handles(sort_handles=False)
        for person_handle in people:
            person = database.get_person_from_handle(person_handle)
            if not person:
                continue
            length = len(person.get_media_list())
            if length > 0:
                stab.row(person, length)
                matches += 1
    elif (filter_name == 'media references'):
        stab.columns(_("Person"), _("Reference"))
        people = database.get_person_handles(sort_handles=False)
        for person_handle in people:
            person = database.get_person_from_handle(person_handle)
            if not person:
                continue
            medialist = person.get_media_list()
            for item in medialist:
                stab.row(person, "media")
                matches += 1
    elif (filter_name == 'unique media'):
        stab.columns(_("Unique Media"))
        pobjects = database.get_media_object_handles()
        for photo_id in database.get_media_object_handles():
            photo = database.get_object_from_handle(photo_id)
            fullname = media_path_full(database, photo.get_path())
            stab.row(fullname)
            matches += 1
    elif (filter_name == 'missing media'):
        stab.columns(_("Missing Media"))
        pobjects = database.get_media_object_handles()
        for photo_id in database.get_media_object_handles():
            photo = database.get_object_from_handle(photo_id)
            fullname = media_path_full(database, photo.get_path())
            try:
                posixpath.getsize(fullname)
            except:
                stab.row(fullname)
                matches += 1
    elif (filter_name == 'media by size'):
        stab.columns(_("Media"), _("Size in bytes"))
        pobjects = database.get_media_object_handles()
        for photo_id in database.get_media_object_handles():
            photo = database.get_object_from_handle(photo_id)
            fullname = media_path_full(database, photo.get_path())
            try:
                bytes = posixpath.getsize(fullname)
                stab.row(fullname, bytes)
                matches += 1
            except:
                pass
    else:
        raise AttributeError, ("invalid filter name: '%s'" % filter_name)
    sdoc.paragraph(_("Filter matched %d records.") % matches)
    sdoc.paragraph("")
    if matches > 0:
        stab.write()
                    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_quick_report(
    name = 'filterbyname',
    category = -1, # stand-alone
    run_func = run,
    translated_name = _("Filter"),
    status = _("Stable"),
    description= _("Display filtered data"),
    author_name="Douglas S. Blank",
    author_email="dblank@cs.brynmawr.edu"
    )
