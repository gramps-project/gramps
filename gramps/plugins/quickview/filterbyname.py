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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#
#

"""
Display filtered data
"""

from gramps.gen.simple import SimpleAccess, SimpleDoc
from gramps.gui.plug.quick import QuickTable
from gramps.gen.utils.file import media_path_full
from gramps.gui.plug.quick import run_quick_report_by_name_direct
from gramps.gen.lib import Person
from gramps.gen.datehandler import get_date

import os
from collections import defaultdict
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
ngettext = glocale.translation.ngettext  # else "nearby" comments are ignored

fname_map = {
    "all": _("all", "Filtering_on"),
    "Inverse Person": _("Inverse Person", "Filtering_on"),
    "Inverse Family": _("Inverse Family", "Filtering_on"),
    "Inverse Event": _("Inverse Event", "Filtering_on"),
    "Inverse Place": _("Inverse Place", "Filtering_on"),
    "Inverse Source": _("Inverse Source", "Filtering_on"),
    "Inverse Repository": _("Inverse Repository", "Filtering_on"),
    "Inverse Media": _("Inverse Media", "Filtering_on"),
    "Inverse Note": _("Inverse Note", "Filtering_on"),
    "all people": _("all people", "Filtering_on"),
    "all families": _("all families", "Filtering_on"),
    "all events": _("all events", "Filtering_on"),
    "all places": _("all places", "Filtering_on"),
    "all sources": _("all sources", "Filtering_on"),
    "all repositories": _("all repositories", "Filtering_on"),
    "all media": _("all media", "Filtering_on"),
    "all notes": _("all notes", "Filtering_on"),
    "males": _("males", "Filtering_on"),
    "females": _("females", "Filtering_on"),
    "people with other gender": _("people with other gender", "Filtering_on"),
    "people with unknown gender": _("people with unknown gender", "Filtering_on"),
    "incomplete names": _("incomplete names", "Filtering_on"),
    "people with missing birth dates": _(
        "people with missing birth dates", "Filtering_on"
    ),
    "disconnected people": _("disconnected people", "Filtering_on"),
    "unique surnames": _("unique surnames", "Filtering_on"),
    "people with media": _("people with media", "Filtering_on"),
    "media references": _("media references", "Filtering_on"),
    "unique media": _("unique media", "Filtering_on"),
    "missing media": _("missing media", "Filtering_on"),
    "media by size": _("media by size", "Filtering_on"),
    "list of people": _("list of people", "Filtering_on"),
}


def run(database, document, filter_name, *args, **kwargs):
    """
    Loops through the families that the person is a child in, and display
    the information about the other children.
    """
    # setup the simple access functions
    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = QuickTable(sdb)
    if filter_name == "all":
        sdoc.title(_("Summary counts of current selection"))
        sdoc.paragraph("")
        sdoc.paragraph(_("Right-click row (or press ENTER) to see selected items."))
        sdoc.paragraph("")
        stab.columns(_("Object"), _("Count/Total"))
        if hasattr(database, "db"):
            stab.row(
                [_("People"), "Filter", "Person"],
                "%d/%d"
                % (
                    len(database.get_person_handles()),
                    len(database.db.get_person_handles()),
                ),
            )
            stab.row(
                [_("Families"), "Filter", "Family"],
                "%d/%d"
                % (
                    len(database.get_family_handles()),
                    len(database.db.get_family_handles()),
                ),
            )
            stab.row(
                [_("Events"), "Filter", "Event"],
                "%d/%d"
                % (
                    len(database.get_event_handles()),
                    len(database.db.get_event_handles()),
                ),
            )
            stab.row(
                [_("Places"), "Filter", "Place"],
                "%d/%d"
                % (
                    len(database.get_place_handles()),
                    len(database.db.get_place_handles()),
                ),
            )
            stab.row(
                [_("Sources"), "Filter", "Source"],
                "%d/%d"
                % (
                    len(database.get_source_handles()),
                    len(database.db.get_source_handles()),
                ),
            )
            stab.row(
                [_("Repositories"), "Filter", "Repository"],
                "%d/%d"
                % (
                    len(database.get_repository_handles()),
                    len(database.db.get_repository_handles()),
                ),
            )
            stab.row(
                [_("Media"), "Filter", "Media"],
                "%d/%d"
                % (
                    len(database.get_media_handles()),
                    len(database.db.get_media_handles()),
                ),
            )
            stab.row(
                [_("Notes"), "Filter", "Note"],
                "%d/%d"
                % (
                    len(database.get_note_handles()),
                    len(database.db.get_note_handles()),
                ),
            )
        else:
            stab.row(
                [_("People"), "Filter", "Person"],
                "%d/%d"
                % (
                    len(database.get_person_handles()),
                    len(database.basedb.get_person_handles()),
                ),
            )
            stab.row(
                [_("Families"), "Filter", "Family"],
                "%d/%d"
                % (
                    len(database.get_family_handles()),
                    len(database.basedb.get_family_handles()),
                ),
            )
            stab.row(
                [_("Events"), "Filter", "Event"],
                "%d/%d"
                % (
                    len(database.get_event_handles()),
                    len(database.basedb.get_event_handles()),
                ),
            )
            stab.row(
                [_("Places"), "Filter", "Place"],
                "%d/%d"
                % (
                    len(database.get_place_handles()),
                    len(database.basedb.get_place_handles()),
                ),
            )
            stab.row(
                [_("Sources"), "Filter", "Source"],
                "%d/%d"
                % (
                    len(database.get_source_handles()),
                    len(database.basedb.get_source_handles()),
                ),
            )
            stab.row(
                [_("Repositories"), "Filter", "Repository"],
                "%d/%d"
                % (
                    len(database.get_repository_handles()),
                    len(database.basedb.get_repository_handles()),
                ),
            )
            stab.row(
                [_("Media"), "Filter", "Media"],
                "%d/%d"
                % (
                    len(database.get_media_handles()),
                    len(database.basedb.get_media_handles()),
                ),
            )
            stab.row(
                [_("Notes"), "Filter", "Note"],
                "%d/%d"
                % (
                    len(database.get_note_handles()),
                    len(database.basedb.get_note_handles()),
                ),
            )
        sdoc.paragraph("")
        stab.write(sdoc)
        return

    # display the title
    if filter_name in fname_map:
        sdoc.title(_("Filtering on %s") % fname_map[filter_name])  # listed above
    else:
        sdoc.title(_("Filtering on %s") % _(filter_name))
    sdoc.paragraph("")
    matches = 0

    if filter_name == "Inverse Person":
        sdb.dbase = database.db
        stab.columns(_("Person"), _("Gramps ID"), _("Birth Date"))
        proxy_handles = set(database.iter_person_handles())

        for person in database.db.iter_people():
            if person.handle not in proxy_handles:
                stab.row(person, person.gramps_id, sdb.birth_or_fallback(person))
                matches += 1

    elif filter_name == "Inverse Family":
        sdb.dbase = database.db
        stab.columns(_("Family"), _("Gramps ID"))
        proxy_handles = set(database.iter_family_handles())

        for family in database.db.iter_families():
            if family.handle not in proxy_handles:
                stab.row(family, family.gramps_id)
                matches += 1

    elif filter_name == "Inverse Event":
        sdb.dbase = database.db
        stab.columns(_("Event"), _("Gramps ID"))
        proxy_handles = set(database.iter_event_handles())

        for event in database.db.iter_events():
            if event.handle not in proxy_handles:
                stab.row(event, event.gramps_id)
                matches += 1

    elif filter_name == "Inverse Place":
        sdb.dbase = database.db
        stab.columns(_("Place"), _("Gramps ID"))
        proxy_handles = set(database.iter_place_handles())

        for place in database.db.iter_places():
            if place.handle not in proxy_handles:
                stab.row(place, place.gramps_id)
                matches += 1

    elif filter_name == "Inverse Source":
        sdb.dbase = database.db
        stab.columns(_("Source"), _("Gramps ID"))
        proxy_handles = set(database.iter_source_handles())

        for source in database.db.iter_sources():
            if source.handle not in proxy_handles:
                stab.row(source, source.gramps_id)
                matches += 1

    elif filter_name == "Inverse Repository":
        sdb.dbase = database.db
        stab.columns(_("Repository"), _("Gramps ID"))
        proxy_handles = set(database.iter_repository_handles())

        for repository in database.db.iter_repositories():
            if repository.handle not in proxy_handles:
                stab.row(repository, repository.gramps_id)
                matches += 1

    elif filter_name == "Inverse Media":
        sdb.dbase = database.db
        stab.columns(_("Media"), _("Gramps ID"))
        proxy_handles = set(database.iter_media_handles())

        for media in database.db.iter_media():
            if media.handle not in proxy_handles:
                stab.row(media, media.gramps_id)
                matches += 1

    elif filter_name == "Inverse Note":
        sdb.dbase = database.db
        stab.columns(_("Note"), _("Gramps ID"))
        proxy_handles = set(database.iter_note_handles())

        for note in database.db.iter_notes():
            if note.handle not in proxy_handles:
                stab.row(note, note.gramps_id)
                matches += 1

    elif filter_name in ["all people", "Person"]:
        stab.columns(_("Person"), _("Gramps ID"), _("Birth Date"))
        for person in database.iter_people():
            stab.row(person, person.gramps_id, sdb.birth_or_fallback(person))
            matches += 1

    elif filter_name in ["all families", "Family"]:
        stab.columns(_("Family"), _("Gramps ID"))
        for family in database.iter_families():
            stab.row(family, family.gramps_id)
            matches += 1

    elif filter_name in ["all events", "Event"]:
        stab.columns(_("Event"), _("Gramps ID"))
        for obj in database.iter_events():
            stab.row(obj, obj.gramps_id)
            matches += 1

    elif filter_name in ["all places", "Place"]:
        stab.columns(_("Place"), _("Gramps ID"))
        for obj in database.iter_places():
            stab.row(obj, obj.gramps_id)
            matches += 1

    elif filter_name in ["all sources", "Source"]:
        stab.columns(_("Source"), _("Gramps ID"))
        for obj in database.iter_sources():
            stab.row(obj, obj.gramps_id)
            matches += 1

    elif filter_name in ["all repositories", "Repository"]:
        stab.columns(_("Repository"), _("Gramps ID"))
        for obj in database.iter_repositories():
            stab.row(obj, obj.gramps_id)
            matches += 1

    elif filter_name in ["all media", "Media"]:
        stab.columns(_("Media"), _("Gramps ID"))
        for obj in database.iter_media():
            stab.row(obj, obj.gramps_id)
            matches += 1

    elif filter_name in ["all notes", "Note"]:
        stab.columns(_("Note"), _("Gramps ID"))
        for obj in database.iter_notes():
            stab.row(obj, obj.gramps_id)
            matches += 1

    elif filter_name == "males":
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        for person in database.iter_people():
            if person.gender == Person.MALE:
                stab.row(
                    person,
                    sdb.birth_or_fallback(person),
                    str(person.get_primary_name().get_type()),
                )
                matches += 1

    elif filter_name == "females":
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        for person in database.iter_people():
            if person.gender == Person.FEMALE:
                stab.row(
                    person,
                    sdb.birth_or_fallback(person),
                    str(person.get_primary_name().get_type()),
                )
                matches += 1

    elif filter_name == "people with other gender":
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        for person in database.iter_people():
            if person.gender == Person.OTHER:
                stab.row(
                    person,
                    sdb.birth_or_fallback(person),
                    str(person.get_primary_name().get_type()),
                )
                matches += 1

    elif filter_name == "people with unknown gender":
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        for person in database.iter_people():
            if person.gender == Person.UNKNOWN:
                stab.row(
                    person,
                    sdb.birth_or_fallback(person),
                    str(person.get_primary_name().get_type()),
                )
                matches += 1

    elif filter_name == "incomplete names":
        stab.columns(_("Name"), _("Birth Date"), _("Name type"))
        for person in database.iter_people():
            for name in [person.get_primary_name()] + person.get_alternate_names():
                if name.get_first_name().strip() == "":
                    stab.row(
                        [name.get_name(), "Person", person.handle],
                        sdb.birth_or_fallback(person),
                        str(name.get_type()),
                    )
                    matches += 1
                else:
                    if name.get_surname_list():
                        for surname in name.get_surname_list():
                            if surname.get_surname().strip() == "":
                                stab.row(
                                    [name.get_first_name(), "Person", person.handle],
                                    sdb.birth_or_fallback(person),
                                    str(name.get_type()),
                                )
                                matches += 1
                    else:
                        stab.row(
                            [name.get_first_name(), "Person", person.handle],
                            sdb.birth_or_fallback(person),
                            str(name.get_type()),
                        )
                        matches += 1

    elif filter_name == "people with missing birth dates":
        stab.columns(_("Person"), _("Type"))
        for person in database.iter_people():
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = database.get_event_from_handle(birth_ref.ref)
                if not get_date(birth):
                    stab.row(person, _("birth event but no date"))
                    matches += 1
            else:
                stab.row(person, _("missing birth event"))
                matches += 1

    elif filter_name == "disconnected people":
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        for person in database.iter_people():
            if (not person.get_main_parents_family_handle()) and (
                not len(person.get_family_handle_list())
            ):
                stab.row(
                    person,
                    sdb.birth_or_fallback(person),
                    str(person.get_primary_name().get_type()),
                )
                matches += 1

    elif filter_name == "unique surnames":
        namelist = defaultdict(int)
        for person in database.iter_people():
            names = [person.get_primary_name()] + person.get_alternate_names()
            surnames = list(set([name.get_group_name() for name in names]))
            for surname in surnames:
                namelist[surname] += 1
        stab.columns(_("Surname"), _("Count"))
        for name in sorted(namelist):
            stab.row(name, namelist[name])
            matches += 1
        stab.set_callback(
            "leftdouble",
            lambda name: run_quick_report_by_name_direct(
                "samesurnames", database, document, name
            ),
        )

    elif filter_name == "people with media":
        stab.columns(_("Person"), _("Media count"))
        for person in database.iter_people():
            length = len(person.get_media_list())
            if length > 0:
                stab.row(person, str(length))
                matches += 1

    elif filter_name == "media references":
        stab.columns(_("Person"), _("Reference"))
        for person in database.iter_people():
            medialist = person.get_media_list()
            for item in medialist:
                stab.row(person, _("media"))
                matches += 1

    elif filter_name == "unique media":
        stab.columns(_("Unique Media"))
        for photo in database.iter_media():
            fullname = media_path_full(database, photo.get_path())
            stab.row(fullname)
            matches += 1

    elif filter_name == "missing media":
        stab.columns(_("Missing Media"))
        for photo in database.iter_media():
            fullname = media_path_full(database, photo.get_path())
            try:
                os.path.getsize(fullname)
            except:
                stab.row(fullname)
                matches += 1

    elif filter_name == "media by size":
        stab.columns(_("Media"), _("Size in bytes"))
        for photo in database.iter_media():
            fullname = media_path_full(database, photo.get_path())
            try:
                bytes = os.path.getsize(fullname)
                stab.row(fullname, str(bytes))
                matches += 1
            except:
                pass

    elif filter_name == "list of people":
        stab.columns(_("Person"), _("Birth Date"), _("Name type"))
        handles = kwargs["handles"]
        for person_handle in handles:
            person = database.get_person_from_handle(person_handle)
            stab.row(
                person,
                sdb.birth_or_fallback(person),
                str(person.get_primary_name().get_type()),
            )
            matches += 1

    else:
        raise AttributeError("invalid filter name: '%s'" % filter_name)
    # Translators: leave all/any {...} untranslated
    sdoc.paragraph(
        ngettext(
            "Filter matched {number_of} record.",
            "Filter matched {number_of} records.",
            matches,
        ).format(number_of=matches)
    )
    sdoc.paragraph("")
    document.has_data = matches > 0
    if matches > 0:
        stab.write(sdoc)
