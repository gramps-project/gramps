#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
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
#
# $Id$
#
#

"""
Display filtered data
"""

from Simple import SimpleAccess, SimpleDoc, SimpleTable
from Utils import media_path_full
from QuickReports import run_quick_report_by_name_direct
from gen.lib import Person
import DateHandler

import posixpath
from TransUtils import sgettext as _
from gettext import ngettext

fname_map = {'all people': _('Filtering_on|all people'), 
             'males': _('Filtering_on|males'), 
             'females': _('Filtering_on|females'),
             'people with unknown gender': 
                _('Filtering_on|people with unknown gender'), 
             'people with incomplete names': 
                _('Filtering_on|people with incomplete names'),
             'people with missing birth dates': 
                _('Filtering_on|people with missing birth dates'), 
             'disconnected people': _('Filtering_on|disconnected people'),
             'all families': _('Filtering_on|all families'), 
             'unique surnames': _('Filtering_on|unique surnames'),
             'people with media': _('Filtering_on|people with media'), 
             'media references': _('Filtering_on|media references'),
             'unique media': _('Filtering_on|unique media'), 
             'missing media': _('Filtering_on|missing media'),
             'media by size': _('Filtering_on|media by size'), 
             'list of people': _('Filtering_on|list of people')}

def run(database, document, filter_name, *args, **kwargs):
    """
    Loops through the families that the person is a child in, and display
    the information about the other children.
    """
    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = SimpleTable(sdb)
    # display the title
    if filter_name in fname_map:
        sdoc.title(_("Filtering on %s") % fname_map[filter_name]) # listed above
    else:
        sdoc.title(_("Filtering on %s") % _(filter_name))
    sdoc.paragraph("")
    matches = 0
    if (filter_name == 'all people'):
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        for person in database.iter_people():
            stab.row(person, sdb.birth_date_obj(person),
                     str(person.get_primary_name().get_type()))
            matches += 1
    elif (filter_name == 'males'):
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        for person in database.iter_people():
            if person.gender == Person.MALE:
                stab.row(person, sdb.birth_date_obj(person),
                         str(person.get_primary_name().get_type()))
                matches += 1
    elif (filter_name == 'females'):
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        for person in database.iter_people():
            if person.gender == Person.FEMALE:
                stab.row(person, sdb.birth_date_obj(person),
                         str(person.get_primary_name().get_type()))
                matches += 1
    elif (filter_name == 'people with unknown gender'):
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        for person in database.iter_people():
            if person.gender not in [Person.FEMALE, Person.MALE]:
                stab.row(person, sdb.birth_date_obj(person),
                         str(person.get_primary_name().get_type()))
                matches += 1
    elif (filter_name == 'people with incomplete names'):
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        for person in database.iter_people():
            for name in [person.get_primary_name()] + person.get_alternate_names():
                if name.get_group_name() == "" or name.get_first_name() == "":
                    stab.row(person, sdb.birth_date_obj(person),
                             str(person.get_primary_name().get_type()))
                    matches += 1
    elif (filter_name == 'people with missing birth dates'):
        stab.columns(_("Person"), _("Type"))
        for person in database.iter_people():
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = database.get_event_from_handle(birth_ref.ref)
                if not DateHandler.get_date(birth):
                    stab.row(person, _("birth event but no date"))
                    matches += 1
            else:
                stab.row(person, _("missing birth event"))
                matches += 1
    elif (filter_name == 'disconnected people'):
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        for person in database.iter_people():
            if ((not person.get_main_parents_family_handle()) and 
                (not len(person.get_family_handle_list()))):
                stab.row(person, sdb.birth_date_obj(person),
                         str(person.get_primary_name().get_type()))
                matches += 1
    elif (filter_name == 'all families'):
        stab.columns(_("Family"))
        for family in database.iter_families():
            stab.row(family)
            matches += 1
    elif (filter_name == 'unique surnames'):
        namelist = {}
        for person in database.iter_people():
            names = [person.get_primary_name()] + person.get_alternate_names()
            surnames = list(set([name.get_group_name() for name in names]))
            for surname in surnames:
                namelist[surname] = namelist.get(surname, 0) + 1
        stab.columns(_("Surname"), _("Count"))
        for name in sorted(namelist):
            stab.row(name, namelist[name])
            matches += 1
        stab.set_callback("leftdouble", 
            lambda name: run_quick_report_by_name_direct("samesurnames",
                                                         database,
                                                         document,
                                                         name))
    elif (filter_name == 'people with media'):
        stab.columns(_("Person"), _("Media count"))
        for person in database.iter_people():
            length = len(person.get_media_list())
            if length > 0:
                stab.row(person, length)
                matches += 1
    elif (filter_name == 'media references'):
        stab.columns(_("Person"), _("Reference"))
        for person in database.iter_people():
            medialist = person.get_media_list()
            for item in medialist:
                stab.row(person, _("media"))
                matches += 1
    elif (filter_name == 'unique media'):
        stab.columns(_("Unique Media"))
        for photo in database.iter_media_objects():
            fullname = media_path_full(database, photo.get_path())
            stab.row(fullname)
            matches += 1
    elif (filter_name == 'missing media'):
        stab.columns(_("Missing Media"))
        for photo in database.iter_media_objects():
            fullname = media_path_full(database, photo.get_path())
            try:
                posixpath.getsize(fullname)
            except:
                stab.row(fullname)
                matches += 1
    elif (filter_name == 'media by size'):
        stab.columns(_("Media"), _("Size in bytes"))
        for photo in database.iter_media_objects():
            fullname = media_path_full(database, photo.get_path())
            try:
                bytes = posixpath.getsize(fullname)
                stab.row(fullname, bytes)
                matches += 1
            except:
                pass
    elif (filter_name == 'list of people'):
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        handles = kwargs["handles"]
        for person_handle in handles:
            person = database.get_person_from_handle(person_handle)
            stab.row(person, sdb.birth_date_obj(person),
                     str(person.get_primary_name().get_type()))
            matches += 1
    else:
        raise AttributeError, ("invalid filter name: '%s'" % filter_name)
    sdoc.paragraph(ngettext("Filter matched %d record."
                   ,
                   "Filter matched %d records.", matches) % matches)
    sdoc.paragraph("")
    if matches > 0:
        stab.write(sdoc)
