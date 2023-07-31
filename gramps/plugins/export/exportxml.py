#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2008       Robert Cheramy <robert@cheramy.net>
# Copyright (C) 2009       Douglas S. Blank
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2010-2011  Nick Hall
# Copyright (C) 2013  Benny Malengier
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
Contains the interface to allow a database to get written using
Gramps' XML file format.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import time
import shutil
import os
import codecs
from xml.sax.saxutils import escape

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
import logging

LOG = logging.getLogger(".WriteXML")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.const import URL_HOMEPAGE
from gramps.gen.lib import Date, Person
from gramps.gen.updatecallback import UpdateCallback
from gramps.gen.db.exceptions import DbWriteFailure
from gramps.version import VERSION
from gramps.gen.constfunc import win
from gramps.gui.plug.export import WriterOptionBox, WriterOptionBoxWithCompression
import gramps.plugins.lib.libgrampsxml as libgrampsxml

# -------------------------------------------------------------------------
#
# Attempt to load the GZIP library. Some version of python do not seem
# to be compiled with this available.
#
# -------------------------------------------------------------------------
try:
    import gzip

    _gzip_ok = 1
except:
    _gzip_ok = 0

# table for skipping control chars from XML except 09, 0A, 0D
strip_dict = dict.fromkeys(list(range(9)) + list(range(11, 13)) + list(range(14, 32)))


def escxml(d):
    return (
        escape(
            d,
            {
                '"': "&quot;",
                "<": "&lt;",
                ">": "&gt;",
            },
        )
        if d
        else ""
    )


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------
class GrampsXmlWriter(UpdateCallback):
    """
    Writes a database to the XML file.
    """

    def __init__(self, db, strip_photos=0, compress=1, version="unknown", user=None):
        """
        Initialize, but does not write, an XML file.

        db - database to write
        strip_photos - remove paths off of media object paths
        >              0: do not touch the paths
        >              1: remove everything expect the filename (eg gpkg)
        >              2: remove leading slash (quick write)
        compress - attempt to compress the database
        """
        UpdateCallback.__init__(self, user.callback)
        self.user = user
        self.compress = compress
        if not _gzip_ok:
            self.compress = False
        self.db = db
        self.strip_photos = strip_photos
        self.version = version

        self.status = None

    def write(self, filename):
        """
        Write the database to the specified file.
        """
        if filename == "-":
            import sys

            try:
                g = sys.stdout.buffer
            except:
                g = sys.stdout
            self.compress = False
        else:
            base = os.path.dirname(filename)
            if os.path.isdir(base):
                if not os.access(base, os.W_OK) or not os.access(base, os.R_OK):
                    raise DbWriteFailure(
                        _("Failure writing %s") % filename,
                        _(
                            "The database cannot be saved because you do "
                            "not have permission to write to the directory. "
                            "Please make sure you have write access to the "
                            "directory and try again."
                        ),
                    )
                    return 0
            else:
                raise DbWriteFailure(
                    _("No directory"),
                    _(
                        "There is no directory %s.\n\n"
                        "Please select another directory "
                        "or create it."
                    )
                    % base,
                )
                return 0

            if os.path.exists(filename):
                if not os.access(filename, os.W_OK):
                    raise DbWriteFailure(
                        _("Failure writing %s") % filename,
                        _(
                            "The database cannot be saved because you do "
                            "not have permission to write to the file. "
                            "Please make sure you have write access to the "
                            "file and try again."
                        ),
                    )
                    return 0

            self.fileroot = os.path.dirname(filename)
            try:
                if self.compress and _gzip_ok:
                    try:
                        g = gzip.open(filename, "wb")
                    except:
                        g = open(filename, "wb")
                else:
                    g = open(filename, "wb")
            except IOError as msg:
                LOG.warning(str(msg))
                raise DbWriteFailure(_("Failure writing %s") % filename, str(msg))
                return 0

        self.g = codecs.getwriter("utf8")(g)

        self.write_xml_data()
        if filename != "-":
            g.close()
        return 1

    def write_handle(self, handle):
        """
        Write the database to the specified file handle.
        """

        if self.compress and _gzip_ok:
            try:
                g = gzip.GzipFile(mode="wb", fileobj=handle)
            except:
                g = handle
        else:
            g = handle

        self.g = codecs.getwriter("utf8")(g)

        self.write_xml_data()
        g.close()
        return 1

    def write_xml_data(self):
        date = time.localtime(time.time())
        owner = self.db.get_researcher()

        person_len = self.db.get_number_of_people()
        family_len = self.db.get_number_of_families()
        event_len = self.db.get_number_of_events()
        citation_len = self.db.get_number_of_citations()
        source_len = self.db.get_number_of_sources()
        place_len = self.db.get_number_of_places()
        repo_len = self.db.get_number_of_repositories()
        obj_len = self.db.get_number_of_media()
        note_len = self.db.get_number_of_notes()
        tag_len = self.db.get_number_of_tags()

        total_steps = (
            person_len
            + family_len
            + event_len
            + citation_len
            + source_len
            + place_len
            + repo_len
            + obj_len
            + note_len
            + tag_len
        )

        self.set_total(total_steps)

        self.g.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.g.write(
            "<!DOCTYPE database "
            'PUBLIC "-//Gramps//DTD Gramps XML %s//EN"\n'
            '"%sxml/%s/grampsxml.dtd">\n'
            % (
                libgrampsxml.GRAMPS_XML_VERSION,
                URL_HOMEPAGE,
                libgrampsxml.GRAMPS_XML_VERSION,
            )
        )
        self.g.write(
            '<database xmlns="%sxml/%s/">\n'
            % (URL_HOMEPAGE, libgrampsxml.GRAMPS_XML_VERSION)
        )
        self.g.write("  <header>\n")
        self.g.write('    <created date="%04d-%02d-%02d"' % date[:3])
        self.g.write(' version="' + self.version + '"')
        self.g.write("/>\n")
        self.g.write("    <researcher>\n")
        self.write_line("resname", owner.get_name(), 3)
        self.write_line("resaddr", owner.get_address(), 3)
        self.write_line("reslocality", owner.get_locality(), 3)
        self.write_line("rescity", owner.get_city(), 3)
        self.write_line("resstate", owner.get_state(), 3)
        self.write_line("rescountry", owner.get_country(), 3)
        self.write_line("respostal", owner.get_postal_code(), 3)
        self.write_line("resphone", owner.get_phone(), 3)
        self.write_line("resemail", owner.get_email(), 3)
        self.g.write("    </researcher>\n")
        self.write_metadata()
        self.g.write("  </header>\n")

        # First write name formats: we need to know all formats
        # by the time we get to person's names
        self.write_name_formats()

        # Write table objects
        if tag_len > 0:
            self.g.write("  <tags>\n")
            for key in sorted(self.db.get_tag_handles()):
                tag = self.db.get_tag_from_handle(key)
                if tag:
                    self.write_tag(tag, 2)
                self.update()
            self.g.write("  </tags>\n")

        # Write primary objects
        if event_len > 0:
            self.g.write("  <events>\n")
            for handle in sorted(self.db.get_event_handles()):
                event = self.db.get_event_from_handle(handle)
                if event:
                    self.write_event(event, 2)
                self.update()
            self.g.write("  </events>\n")

        if person_len > 0:
            self.g.write("  <people")
            person = self.db.get_default_person()
            if person:
                self.g.write(' home="_%s"' % person.handle)
            self.g.write(">\n")

            for handle in sorted(self.db.get_person_handles()):
                person = self.db.get_person_from_handle(handle)
                if person:
                    self.write_person(person, 2)
                self.update()
            self.g.write("  </people>\n")

        if family_len > 0:
            self.g.write("  <families>\n")
            for handle in sorted(self.db.iter_family_handles()):
                family = self.db.get_family_from_handle(handle)
                if family:
                    self.write_family(family, 2)
                self.update()
            self.g.write("  </families>\n")

        if citation_len > 0:
            self.g.write("  <citations>\n")
            for handle in sorted(self.db.get_citation_handles()):
                citation = self.db.get_citation_from_handle(handle)
                if citation:
                    self.write_citation(citation, 2)
                self.update()
            self.g.write("  </citations>\n")

        if source_len > 0:
            self.g.write("  <sources>\n")
            for handle in sorted(self.db.get_source_handles()):
                source = self.db.get_source_from_handle(handle)
                if source:
                    self.write_source(source, 2)
                self.update()
            self.g.write("  </sources>\n")

        if place_len > 0:
            self.g.write("  <places>\n")
            for key in sorted(self.db.get_place_handles()):
                # try:
                place = self.db.get_place_from_handle(key)
                if place:
                    self.write_place_obj(place, 2)
                self.update()
            self.g.write("  </places>\n")

        if obj_len > 0:
            self.g.write("  <objects>\n")
            for handle in sorted(self.db.get_media_handles()):
                obj = self.db.get_media_from_handle(handle)
                if obj:
                    self.write_object(obj, 2)
                self.update()
            self.g.write("  </objects>\n")

        if repo_len > 0:
            self.g.write("  <repositories>\n")
            for key in sorted(self.db.get_repository_handles()):
                repo = self.db.get_repository_from_handle(key)
                if repo:
                    self.write_repository(repo, 2)
                self.update()
            self.g.write("  </repositories>\n")

        if note_len > 0:
            self.g.write("  <notes>\n")
            for key in sorted(self.db.get_note_handles()):
                note = self.db.get_note_from_handle(key)
                if note:
                    self.write_note(note, 2)
                self.update()
            self.g.write("  </notes>\n")

        # Data is written, now write bookmarks.
        self.write_bookmarks()
        self.write_namemaps()

        self.g.write("</database>\n")

    #        self.status.end()
    #        self.status = None

    def write_metadata(self):
        """Method to write out metadata of the database"""
        mediapath = self.db.get_mediapath()
        if mediapath is not None:
            self.write_line("mediapath", mediapath, 2)

    def write_namemaps(self):
        group_map = self.db.get_name_group_keys()
        name_len = len(group_map)

        if name_len > 0:
            self.g.write("  <namemaps>\n")
            for key in group_map:
                value = self.db.get_name_group_mapping(key)
                self.g.write(
                    '    <map type="group_as" key="%s" value="%s"/>\n'
                    % (self.fix(key), self.fix(value))
                )
            self.g.write("  </namemaps>\n")

    def write_bookmarks(self):
        bm_person_len = len(self.db.bookmarks.get())
        bm_family_len = len(self.db.family_bookmarks.get())
        bm_event_len = len(self.db.event_bookmarks.get())
        bm_source_len = len(self.db.source_bookmarks.get())
        bm_citation_len = len(self.db.citation_bookmarks.get())
        bm_place_len = len(self.db.place_bookmarks.get())
        bm_repo_len = len(self.db.repo_bookmarks.get())
        bm_obj_len = len(self.db.media_bookmarks.get())
        bm_note_len = len(self.db.note_bookmarks.get())

        bm_len = (
            bm_person_len
            + bm_family_len
            + bm_event_len
            + bm_source_len
            + bm_place_len
            + bm_repo_len
            + bm_citation_len
            + bm_obj_len
            + bm_note_len
        )

        if bm_len > 0:
            self.g.write("  <bookmarks>\n")

            for handle in self.db.get_bookmarks().get():
                self.g.write('    <bookmark target="person" hlink="_%s"/>\n' % handle)
            for handle in self.db.get_family_bookmarks().get():
                self.g.write('    <bookmark target="family" hlink="_%s"/>\n' % handle)
            for handle in self.db.get_event_bookmarks().get():
                self.g.write('    <bookmark target="event" hlink="_%s"/>\n' % handle)
            for handle in self.db.get_source_bookmarks().get():
                self.g.write('    <bookmark target="source" hlink="_%s"/>\n' % handle)
            for handle in self.db.get_citation_bookmarks().get():
                self.g.write('    <bookmark target="citation" hlink="_%s"/>\n' % handle)
            for handle in self.db.get_place_bookmarks().get():
                self.g.write('    <bookmark target="place" hlink="_%s"/>\n' % handle)
            for handle in self.db.get_media_bookmarks().get():
                self.g.write('    <bookmark target="media" hlink="_%s"/>\n' % handle)
            for handle in self.db.get_repo_bookmarks().get():
                self.g.write(
                    '    <bookmark target="repository" hlink="_%s"/>\n' % handle
                )
            for handle in self.db.get_note_bookmarks().get():
                self.g.write('    <bookmark target="note" hlink="_%s"/>\n' % handle)

            self.g.write("  </bookmarks>\n")

    def write_name_formats(self):
        if len(self.db.name_formats) > 0:
            self.g.write("  <name-formats>\n")
            for number, name, fmt_str, active in self.db.name_formats:
                self.g.write(
                    '%s<format number="%d" name="%s" '
                    'fmt_str="%s" active="%d"/>\n'
                    % ("    ", number, escxml(name), escxml(fmt_str), int(active))
                )
            self.g.write("  </name-formats>\n")

    def write_tag(self, tag, index=2):
        """
        Write a tag definition.
        """
        if not tag:
            return

        self.write_table_tag("tag", tag, index, close=False)
        self.g.write(' name="%s"' % escxml(tag.get_name()))
        self.g.write(' color="%s"' % tag.get_color())
        self.g.write(' priority="%d"' % tag.get_priority())
        self.g.write("/>\n")

    def fix(self, line):
        l = str(line)
        l = l.strip().translate(strip_dict)
        return escxml(l)

    def write_note_list(self, note_list, indent=0):
        for handle in note_list:
            self.write_ref("noteref", handle, indent)

    def write_note(self, note, index=2):
        if not note:
            return

        self.write_primary_tag("note", note, index, close=False)

        ntype = escxml(note.get_type().xml_str())
        format = note.get_format()
        text = note.get_styledtext()
        styles = text.get_tags()
        text = str(text)

        self.g.write(' type="%s"' % ntype)
        if format != note.FLOWED:
            self.g.write(' format="%d"' % format)
        self.g.write(">\n")

        self.write_text("text", text, index + 1)

        if styles:
            self.write_styles(styles, index + 1)

        for tag_handle in note.get_tag_list():
            self.write_ref("tagref", tag_handle, index + 1)

        self.g.write("  " * index + "</note>\n")

    def write_styles(self, styles, index=3):
        for style in styles:
            name = style.name.xml_str()
            value = style.value

            self.g.write("  " * index + '<style name="%s"' % name)
            if value:
                self.g.write(' value="%s"' % escxml(str(value)))
            self.g.write(">\n")

            for start, end in style.ranges:
                self.g.write(
                    ("  " * (index + 1))
                    + '<range start="%d" end="%d"/>\n' % (start, end)
                )

            self.g.write("  " * index + "</style>\n")

    def write_text(self, val, text, indent=0):
        if not text:
            return

        if indent:
            self.g.write("  " * indent)

        self.g.write("<%s>" % val)
        self.g.write(escxml(str(text).translate(strip_dict)))
        self.g.write("</%s>\n" % val)

    def write_person(self, person, index=1):
        sp = "  " * index
        self.write_primary_tag("person", person, index)
        if person.get_gender() == Person.MALE:
            self.write_line("gender", "M", index + 1)
        elif person.get_gender() == Person.FEMALE:
            self.write_line("gender", "F", index + 1)
        elif person.get_gender() == Person.OTHER:
            self.write_line("gender", "X", index + 1)
        else:
            self.write_line("gender", "U", index + 1)
        self.dump_name(person.get_primary_name(), False, index + 1)
        for name in person.get_alternate_names():
            self.dump_name(name, True, index + 1)

        # self.dump_event_ref(person.get_birth_ref(),index+1)
        # self.dump_event_ref(person.get_death_ref(),index+1)
        for event_ref in person.get_event_ref_list():
            self.dump_event_ref(event_ref, index + 1)

        for lds_ord in person.lds_ord_list:
            self.dump_ordinance(lds_ord, index + 1)

        self.write_media_list(person.get_media_list(), index + 1)

        self.write_address_list(person, index + 1)
        self.write_attribute_list(person.get_attribute_list())
        self.write_url_list(person.get_url_list(), index + 1)

        for family_handle in person.get_parent_family_handle_list():
            self.write_ref("childof", family_handle, index + 1)

        for family_handle in person.get_family_handle_list():
            self.write_ref("parentin", family_handle, index + 1)

        for person_ref in person.get_person_ref_list():
            self.dump_person_ref(person_ref, index + 1)

        self.write_note_list(person.get_note_list(), index + 1)

        for citation_handle in person.get_citation_list():
            self.write_ref("citationref", citation_handle, index + 1)

        for tag_handle in person.get_tag_list():
            self.write_ref("tagref", tag_handle, index + 1)

        self.g.write("%s</person>\n" % sp)

    def write_family(self, family, index=1):
        sp = "  " * index
        self.write_family_handle(family, index)
        fhandle = family.get_father_handle()
        mhandle = family.get_mother_handle()
        if fhandle:
            self.write_ref("father", fhandle, index + 1)
        if mhandle:
            self.write_ref("mother", mhandle, index + 1)
        for event_ref in family.get_event_ref_list():
            self.dump_event_ref(event_ref, 3)
        for lds_ord in family.lds_ord_list:
            self.dump_ordinance(lds_ord, index + 1)

        self.write_media_list(family.get_media_list(), index + 1)

        for child_ref in family.get_child_ref_list():
            self.dump_child_ref(child_ref, index + 1)
        self.write_attribute_list(family.get_attribute_list())
        self.write_note_list(family.get_note_list(), index + 1)
        for citation_handle in family.get_citation_list():
            self.write_ref("citationref", citation_handle, index + 1)

        for tag_handle in family.get_tag_list():
            self.write_ref("tagref", tag_handle, index + 1)

        self.g.write("%s</family>\n" % sp)

    def write_citation(self, citation, index=1):
        sp = "  " * index
        self.write_primary_tag("citation", citation, index)
        self.write_date(citation.get_date_object(), index + 1)
        self.write_line("page", citation.get_page(), index + 1)
        self.write_line_always("confidence", citation.get_confidence_level(), index + 1)
        self.write_note_list(citation.get_note_list(), index + 1)
        self.write_media_list(citation.get_media_list(), index + 1)
        self.write_srcattribute_list(citation.get_attribute_list(), index + 1)
        self.write_ref("sourceref", citation.get_reference_handle(), index + 1)

        for tag_handle in citation.get_tag_list():
            self.write_ref("tagref", tag_handle, index + 1)

        self.g.write("%s</citation>\n" % sp)

    def write_source(self, source, index=1):
        sp = "  " * index
        self.write_primary_tag("source", source, index)
        self.write_force_line("stitle", source.get_title(), index + 1)
        self.write_line("sauthor", source.get_author(), index + 1)
        self.write_line("spubinfo", source.get_publication_info(), index + 1)
        self.write_line("sabbrev", source.get_abbreviation(), index + 1)
        self.write_note_list(source.get_note_list(), index + 1)
        self.write_media_list(source.get_media_list(), index + 1)
        self.write_srcattribute_list(source.get_attribute_list(), index + 1)
        self.write_reporef_list(source.get_reporef_list(), index + 1)

        for tag_handle in source.get_tag_list():
            self.write_ref("tagref", tag_handle, index + 1)

        self.g.write("%s</source>\n" % sp)

    def write_repository(self, repo, index=1):
        sp = "  " * index
        self.write_primary_tag("repository", repo, index)
        # name
        self.write_line("rname", repo.name, index + 1)
        rtype = repo.type.xml_str()
        if rtype:
            self.write_line("type", rtype, index + 1)
        # address list
        self.write_address_list(repo, index + 1)
        # url list
        self.write_url_list(repo.get_url_list(), index + 1)
        self.write_note_list(repo.get_note_list(), index + 1)

        for tag_handle in repo.get_tag_list():
            self.write_ref("tagref", tag_handle, index + 1)

        self.g.write("%s</repository>\n" % sp)

    def write_address_list(self, obj, index=1):
        if len(obj.get_address_list()) == 0:
            return
        sp = "  " * index
        for address in obj.get_address_list():
            self.g.write("%s<address%s>\n" % (sp, conf_priv(address)))
            self.write_date(address.get_date_object(), index + 1)
            self.write_line("street", address.get_street(), index + 1)
            self.write_line("locality", address.get_locality(), index + 1)
            self.write_line("city", address.get_city(), index + 1)
            self.write_line("county", address.get_county(), index + 1)
            self.write_line("state", address.get_state(), index + 1)
            self.write_line("country", address.get_country(), index + 1)
            self.write_line("postal", address.get_postal_code(), index + 1)
            self.write_line("phone", address.get_phone(), index + 1)
            self.write_note_list(address.get_note_list(), index + 1)
            for citation_handle in address.get_citation_list():
                self.write_ref("citationref", citation_handle, index + 1)
            self.g.write("%s</address>\n" % sp)

    def dump_person_ref(self, personref, index=1):
        if not personref or not personref.ref:
            return
        sp = "  " * index
        priv_text = conf_priv(personref)
        rel_text = ' rel="%s"' % escxml(personref.get_relation())

        citation_list = personref.get_citation_list()
        nreflist = personref.get_note_list()
        if len(citation_list) + len(nreflist) == 0:
            self.write_ref(
                "personref",
                personref.ref,
                index,
                close=True,
                extra_text=priv_text + rel_text,
            )
        else:
            self.write_ref(
                "personref",
                personref.ref,
                index,
                close=False,
                extra_text=priv_text + rel_text,
            )
            for citation_handle in citation_list:
                self.write_ref("citationref", citation_handle, index + 1)

            self.write_note_list(nreflist, index + 1)
            self.g.write("%s</personref>\n" % sp)

    def dump_child_ref(self, childref, index=1):
        if not childref or not childref.ref:
            return
        sp = "  " * index
        priv_text = conf_priv(childref)
        if childref.frel.is_default():
            frel_text = ""
        else:
            frel_text = ' frel="%s"' % escxml(childref.frel.xml_str())
        if childref.mrel.is_default():
            mrel_text = ""
        else:
            mrel_text = ' mrel="%s"' % escxml(childref.mrel.xml_str())
        citation_list = childref.get_citation_list()
        nreflist = childref.get_note_list()
        if len(citation_list) + len(nreflist) == 0:
            self.write_ref(
                "childref",
                childref.ref,
                index,
                close=True,
                extra_text=priv_text + mrel_text + frel_text,
            )
        else:
            self.write_ref(
                "childref",
                childref.ref,
                index,
                close=False,
                extra_text=priv_text + mrel_text + frel_text,
            )
            for citation_handle in citation_list:
                self.write_ref("citationref", citation_handle, index + 1)
            self.write_note_list(nreflist, index + 1)
            self.g.write("%s</childref>\n" % sp)

    def dump_event_ref(self, eventref, index=1):
        if not eventref or not eventref.ref:
            return
        sp = "  " * index
        priv_text = conf_priv(eventref)
        role = escxml(eventref.role.xml_str())
        if role:
            role_text = ' role="%s"' % role
        else:
            role_text = ""

        attribute_list = eventref.get_attribute_list()
        citation_list = eventref.get_citation_list()
        note_list = eventref.get_note_list()
        if len(citation_list) + len(attribute_list) + len(note_list) == 0:
            self.write_ref(
                "eventref",
                eventref.ref,
                index,
                close=True,
                extra_text=priv_text + role_text,
            )
        else:
            self.write_ref(
                "eventref",
                eventref.ref,
                index,
                close=False,
                extra_text=priv_text + role_text,
            )
            self.write_attribute_list(attribute_list, index + 1)
            self.write_note_list(note_list, index + 1)
            for citation_handle in citation_list:
                self.write_ref("citationref", citation_handle, index + 1)
            self.g.write("%s</eventref>\n" % sp)

    def dump_place_ref(self, placeref, index=1):
        sp = "  " * index
        date = placeref.get_date_object()
        if date.is_empty():
            self.write_ref("placeref", placeref.ref, index, close=True)
        else:
            self.write_ref("placeref", placeref.ref, index, close=False)
            self.write_date(date, index + 1)
            self.g.write("%s</placeref>\n" % sp)

    def dump_place_name(self, place_name, index=1):
        sp = "  " * index
        value = place_name.get_value()
        date = place_name.get_date_object()
        lang = place_name.get_language()
        self.g.write('%s<pname value="%s"' % (sp, self.fix(value)))
        if lang:
            self.g.write(' lang="%s"' % self.fix(lang))
        if date.is_empty():
            self.g.write("/>\n")
        else:
            self.g.write(">\n")
            self.write_date(date, index + 1)
            self.g.write("%s</pname>\n" % sp)

    def write_event(self, event, index=1):
        if not event:
            return

        self.write_primary_tag("event", event, 2)

        sp = "  " * index
        etype = event.get_type().xml_str()
        self.g.write("  %s<type>%s</type>\n" % (sp, self.fix(etype)))
        self.write_date(event.get_date_object(), index + 1)
        self.write_ref("place", event.get_place_handle(), index + 1)
        self.write_line("description", event.get_description(), index + 1)
        self.write_attribute_list(event.get_attribute_list(), index + 1)
        self.write_note_list(event.get_note_list(), index + 1)

        for citation_handle in event.get_citation_list():
            self.write_ref("citationref", citation_handle, index + 1)
        self.write_media_list(event.get_media_list(), index + 1)

        for tag_handle in event.get_tag_list():
            self.write_ref("tagref", tag_handle, index + 1)

        self.g.write("%s</event>\n" % sp)

    def dump_ordinance(self, ord, index=1):
        name = ord.type2xml()

        sp = "  " * index
        sp2 = "  " * (index + 1)

        priv = conf_priv(ord)
        self.g.write('%s<lds_ord type="%s"%s>\n' % (sp, name, priv))
        dateobj = ord.get_date_object()
        if dateobj and not dateobj.is_empty():
            self.write_date(dateobj, index + 1)
        if ord.get_temple():
            self.g.write('%s<temple val="%s"/>\n' % (sp2, self.fix(ord.get_temple())))
        self.write_ref("place", ord.get_place_handle(), index + 1)
        if ord.get_status() != 0:
            self.g.write('%s<status val="%s"/>\n' % (sp2, ord.status2xml()))
        if ord.get_family_handle():
            self.g.write(
                '%s<sealed_to hlink="%s"/>\n' % (sp2, "_" + ord.get_family_handle())
            )
        self.write_note_list(ord.get_note_list(), index + 1)
        for citation_handle in ord.get_citation_list():
            self.write_ref("citationref", citation_handle, index + 1)
        self.g.write("%s</lds_ord>\n" % sp)

    def write_ref(self, tagname, handle, index=1, close=True, extra_text=""):
        if handle:
            if close:
                close_tag = "/"
            else:
                close_tag = ""
            sp = "  " * index
            self.g.write(
                '%s<%s hlink="_%s"%s%s>\n'
                % (sp, tagname, handle, extra_text, close_tag)
            )

    def write_primary_tag(self, tagname, obj, index=1, close=True):
        """
        Write the tag attributes common to all primary objects.
        """
        if not obj:
            return
        priv_text = conf_priv(obj)
        id_text = ' id="%s"' % escxml(obj.gramps_id)

        self.write_table_tag(tagname, obj, index, False)
        self.g.write(id_text + priv_text)
        if close:
            self.g.write(">\n")

    def write_table_tag(self, tagname, obj, index=1, close=True):
        """
        Write the tag attributes common to all table objects.
        """
        if not obj:
            return
        sp = "  " * index
        try:
            change_text = ' change="%d"' % obj.get_change_time()
        except:
            change_text = ' change="%d"' % 0

        handle_text = ' handle="_%s"' % obj.get_handle()

        obj_text = "%s<%s" % (sp, tagname)
        self.g.write(obj_text + handle_text + change_text)
        if close:
            self.g.write(">\n")

    def write_family_handle(self, family, index=1):
        sp = "  " * index
        self.write_primary_tag("family", family, index)
        if family:
            rel = escxml(family.get_relationship().xml_str())
            if rel != "":
                self.g.write('  %s<rel type="%s"/>\n' % (sp, rel))

    def write_surname(self, surname, indent=1):
        """
        Writes a surname of the name
        """
        pre = surname.get_prefix()
        con = surname.get_connector()
        nam = surname.get_surname()
        der = surname.get_origintype().xml_str()
        pri = surname.get_primary()
        self.g.write("%s<surname" % ("  " * indent))
        if pre:
            self.g.write(' prefix="%s"' % escxml(pre))
        if not pri:
            self.g.write(' prim="0"')
        if con:
            self.g.write(' connector="%s"' % escxml(con))
        if der:
            self.g.write(' derivation="%s"' % escxml(der))

        self.g.write(">%s</surname>\n" % self.fix(nam))

    def write_line(self, tagname, value, indent=1):
        if value:
            self.g.write(
                "%s<%s>%s</%s>\n" % ("  " * indent, tagname, self.fix(value), tagname)
            )

    def write_line_nofix(self, tagname, value, indent=1):
        """Writes a line, but does not escape characters.
        Use this instead of write_line if the value is already fixed,
        this avoids &amp; becoming &amp;amp;
        """
        if value:
            self.g.write("%s<%s>%s</%s>\n" % ("  " * indent, tagname, value, tagname))

    def write_line_always(self, tagname, value, indent=1):
        """Writes a line, always, even with a zero value."""
        self.g.write(
            "%s<%s>%s</%s>\n" % ("  " * indent, tagname, self.fix(value), tagname)
        )

    def get_iso_date(self, date):
        if date[2] == 0:
            y = "????"
        else:
            y = "%04d" % date[2]

        if date[1] == 0:
            if date[0] == 0:
                m = ""
            else:
                m = "-??"
        else:
            m = "-%02d" % (date[1])
        if date[0] == 0:
            d = ""
        else:
            d = "-%02d" % date[0]
        ret = "%s%s%s" % (y, m, d)
        # If the result does not contain anything beyond dashes
        # and question marks then it's as good as empty
        if ret.replace("-", "").replace("?", "") == "":
            ret = ""
        return ret

    def write_date(self, date, indent=1):
        sp = "  " * indent

        cal = date.get_calendar()
        if cal != Date.CAL_GREGORIAN:
            calstr = ' cformat="%s"' % Date.calendar_names[cal]
        else:
            calstr = ""

        qual = date.get_quality()
        if qual == Date.QUAL_ESTIMATED:
            qual_str = ' quality="estimated"'
        elif qual == Date.QUAL_CALCULATED:
            qual_str = ' quality="calculated"'
        else:
            qual_str = ""

        dualdated = date.get_slash()
        if dualdated:
            dualdated_str = ' dualdated="1"'
        else:
            dualdated_str = ""

        newyear = date.newyear_to_str()
        if newyear:
            newyear_str = ' newyear="%s"' % newyear
        else:
            newyear_str = ""

        mode = date.get_modifier()

        if date.is_compound():
            if mode == Date.MOD_RANGE:
                tagname = "daterange"
            else:
                tagname = "datespan"

            d1 = self.get_iso_date(date.get_start_date())
            d2 = self.get_iso_date(date.get_stop_date())
            if d1 != "" or d2 != "":
                self.g.write(
                    '%s<%s start="%s" stop="%s"%s%s%s%s/>\n'
                    % (
                        sp,
                        tagname,
                        d1,
                        d2,
                        qual_str,
                        calstr,
                        dualdated_str,
                        newyear_str,
                    )
                )
        elif mode != Date.MOD_TEXTONLY:
            date_str = self.get_iso_date(date.get_start_date())
            if date_str == "":
                return

            if mode == Date.MOD_BEFORE:
                mode_str = ' type="before"'
            elif mode == Date.MOD_AFTER:
                mode_str = ' type="after"'
            elif mode == Date.MOD_ABOUT:
                mode_str = ' type="about"'
            elif mode == Date.MOD_FROM:
                mode_str = ' type="from"'
            elif mode == Date.MOD_TO:
                mode_str = ' type="to"'
            else:
                mode_str = ""

            self.g.write(
                '%s<dateval val="%s"%s%s%s%s%s/>\n'
                % (sp, date_str, mode_str, qual_str, calstr, dualdated_str, newyear_str)
            )
        else:
            self.g.write('%s<datestr val="%s"/>\n' % (sp, self.fix(date.get_text())))

    def write_force_line(self, label, value, indent=1):
        if value is not None:
            self.g.write(
                "%s<%s>%s</%s>\n" % ("  " * indent, label, self.fix(value), label)
            )

    def dump_name(self, name, alternative=False, index=1):
        sp = "  " * index
        name_type = name.get_type().xml_str()
        # bug 9242
        if len(name.get_first_name().splitlines()) != 1:
            firstname = "".join(name.get_first_name().splitlines())
        else:
            firstname = name.get_first_name()
        self.g.write("%s<name" % sp)
        if alternative:
            self.g.write(' alt="1"')
        if name_type:
            self.g.write(' type="%s"' % escxml(name_type))
        if name.get_privacy() != 0:
            self.g.write(' priv="%d"' % name.get_privacy())
        if name.get_sort_as() != 0:
            self.g.write(' sort="%d"' % name.get_sort_as())
        if name.get_display_as() != 0:
            self.g.write(' display="%d"' % name.get_display_as())
        self.g.write(">\n")
        self.write_line("first", firstname, index + 1)
        self.write_line("call", name.get_call_name(), index + 1)
        for surname in name.get_surname_list():
            self.write_surname(surname, index + 1)
        self.write_line("suffix", name.get_suffix(), index + 1)
        self.write_line("title", name.get_title(), index + 1)
        self.write_line("nick", name.get_nick_name(), index + 1)
        self.write_line("familynick", name.get_family_nick_name(), index + 1)
        self.write_line("group", name.get_group_as(), index + 1)
        if name.date:
            self.write_date(name.date, 4)
        self.write_note_list(name.get_note_list(), index + 1)
        for citation_handle in name.get_citation_list():
            self.write_ref("citationref", citation_handle, index + 1)

        self.g.write("%s</name>\n" % sp)

    def append_value(self, orig, val):
        if orig:
            return "%s, %s" % (orig, val)
        else:
            return val

    def build_place_title(self, loc):
        "Builds a title from a location"
        street = self.fix(loc.get_street())
        locality = self.fix(loc.get_locality())
        city = self.fix(loc.get_city())
        parish = self.fix(loc.get_parish())
        county = self.fix(loc.get_county())
        state = self.fix(loc.get_state())
        country = self.fix(loc.get_country())

        value = ""

        if street:
            value = street
        if locality:
            value = self.append_value(value, locality)
        if city:
            value = self.append_value(value, city)
        if parish:
            value = self.append_value(value, parish)
        if county:
            value = self.append_value(value, county)
        if state:
            value = self.append_value(value, state)
        if country:
            value = self.append_value(value, country)
        return value

    def dump_location(self, loc):
        "Writes the location information to the output file"
        if loc.is_empty():
            return
        street = self.fix(loc.get_street())
        locality = self.fix(loc.get_locality())
        city = self.fix(loc.get_city())
        parish = self.fix(loc.get_parish())
        county = self.fix(loc.get_county())
        state = self.fix(loc.get_state())
        country = self.fix(loc.get_country())
        zip_code = self.fix(loc.get_postal_code())
        phone = self.fix(loc.get_phone())

        self.g.write("      <location")
        if street:
            self.g.write(' street="%s"' % street)
        if locality:
            self.g.write(' locality="%s"' % locality)
        if city:
            self.g.write(' city="%s"' % city)
        if parish:
            self.g.write(' parish="%s"' % parish)
        if county:
            self.g.write(' county="%s"' % county)
        if state:
            self.g.write(' state="%s"' % state)
        if country:
            self.g.write(' country="%s"' % country)
        if zip_code:
            self.g.write(' postal="%s"' % zip_code)
        if phone:
            self.g.write(' phone="%s"' % phone)
        self.g.write("/>\n")

    def write_attribute_list(self, list, indent=3):
        sp = "  " * indent
        for attr in list:
            self.g.write(
                '%s<attribute%s type="%s" value="%s"'
                % (
                    sp,
                    conf_priv(attr),
                    escxml(attr.get_type().xml_str()),
                    self.fix(attr.get_value()),
                )
            )
            citation_list = attr.get_citation_list()
            nlist = attr.get_note_list()
            if (len(nlist) + len(citation_list)) == 0:
                self.g.write("/>\n")
            else:
                self.g.write(">\n")
                for citation_handle in citation_list:
                    self.write_ref("citationref", citation_handle, indent + 1)
                self.write_note_list(attr.get_note_list(), indent + 1)
                self.g.write("%s</attribute>\n" % sp)

    def write_srcattribute_list(self, list, indent=3):
        sp = "  " * indent
        for srcattr in list:
            self.g.write(
                '%s<srcattribute%s type="%s" value="%s"'
                % (
                    sp,
                    conf_priv(srcattr),
                    escxml(srcattr.get_type().xml_str()),
                    self.fix(srcattr.get_value()),
                )
            )
            self.g.write("/>\n")

    def write_media_list(self, list, indent=3):
        sp = "  " * indent
        for photo in list:
            mobj_id = photo.get_reference_handle()
            self.g.write('%s<objref hlink="%s"' % (sp, "_" + mobj_id))
            if photo.get_privacy():
                self.g.write(' priv="1"')
            proplist = photo.get_attribute_list()
            citation_list = photo.get_citation_list()
            nreflist = photo.get_note_list()
            rect = photo.get_rectangle()
            if rect is not None:
                corner1_x = rect[0]
                corner1_y = rect[1]
                corner2_x = rect[2]
                corner2_y = rect[3]
                if corner1_x is None:
                    corner1_x = 0
                if corner1_y is None:
                    corner1_y = 0
                if corner2_x is None:
                    corner2_x = 100
                if corner2_y is None:
                    corner2_y = 100
                # don't output not set rectangle
                if (
                    corner1_x == corner1_y == corner2_x == corner2_y == 0
                    or corner1_x == corner1_y == 0
                    and corner2_x == corner2_y == 100
                ):
                    rect = None
            if len(proplist) + len(nreflist) + len(citation_list) == 0 and rect is None:
                self.g.write("/>\n")
            else:
                self.g.write(">\n")
                if rect is not None:
                    self.g.write(
                        ' %s<region corner1_x="%d" corner1_y="%d" '
                        'corner2_x="%d" corner2_y="%d"/>\n'
                        % (sp, corner1_x, corner1_y, corner2_x, corner2_y)
                    )
                self.write_attribute_list(proplist, indent + 1)
                for citation_handle in citation_list:
                    self.write_ref("citationref", citation_handle, indent + 1)
                self.write_note_list(nreflist, indent + 1)
                self.g.write("%s</objref>\n" % sp)

    def write_reporef_list(self, rrlist, index=1):
        for reporef in rrlist:
            if not reporef or not reporef.ref:
                continue

            if reporef.get_privacy():
                priv_text = ' priv="1"'
            else:
                priv_text = ""

            if reporef.call_number == "":
                callno_text = ""
            else:
                callno_text = ' callno="%s"' % escxml(reporef.call_number)

            mtype = reporef.media_type.xml_str()
            if mtype:
                type_text = ' medium="%s"' % escxml(mtype)
            else:
                type_text = ""

            note_list = reporef.get_note_list()
            if len(note_list) == 0:
                self.write_ref(
                    "reporef",
                    reporef.ref,
                    index,
                    close=True,
                    extra_text=priv_text + callno_text + type_text,
                )
            else:
                self.write_ref(
                    "reporef",
                    reporef.ref,
                    index,
                    close=False,
                    extra_text=priv_text + callno_text + type_text,
                )
                self.write_note_list(note_list, index + 1)
                sp = "  " * index
                self.g.write("%s</reporef>\n" % sp)

    def write_url_list(self, list, index=1):
        sp = "  " * index
        for url in list:
            url_type = url.get_type().xml_str()
            if url_type:
                type_text = ' type="%s"' % escxml(url_type)
            else:
                type_text = ""
            priv_text = conf_priv(url)
            if url.get_description() != "":
                desc_text = ' description="%s"' % self.fix(url.get_description())
            else:
                desc_text = ""
            path_text = '  href="%s"' % self.fix(url.get_path())
            self.g.write(
                "%s<url%s%s%s%s/>\n" % (sp, priv_text, path_text, type_text, desc_text)
            )

    def write_place_obj(self, place, index=1):
        self.write_primary_tag("placeobj", place, index, close=False)
        ptype = self.fix(place.get_type().xml_str())
        self.g.write(' type="%s"' % ptype)
        self.g.write(">\n")

        title = self.fix(place.get_title())
        code = self.fix(place.get_code())
        self.write_line_nofix("ptitle", title, index + 1)
        self.write_line_nofix("code", code, index + 1)

        self.dump_place_name(place.get_name(), index + 1)
        for pname in place.get_alternative_names():
            self.dump_place_name(pname, index + 1)

        longitude = self.fix(place.get_longitude())
        lat = self.fix(place.get_latitude())
        if longitude or lat:
            self.g.write(
                '%s<coord long="%s" lat="%s"/>\n' % ("  " * (index + 1), longitude, lat)
            )
        for placeref in place.get_placeref_list():
            self.dump_place_ref(placeref, index + 1)
        list(map(self.dump_location, place.get_alternate_locations()))
        self.write_media_list(place.get_media_list(), index + 1)
        self.write_url_list(place.get_url_list())
        self.write_note_list(place.get_note_list(), index + 1)
        for citation_handle in place.get_citation_list():
            self.write_ref("citationref", citation_handle, index + 1)

        for tag_handle in place.get_tag_list():
            self.write_ref("tagref", tag_handle, index + 1)

        self.g.write("%s</placeobj>\n" % ("  " * index))

    def write_object(self, obj, index=1):
        self.write_primary_tag("object", obj, index)
        handle = obj.get_gramps_id()
        mime_type = obj.get_mime_type()
        path = obj.get_path()
        desc = obj.get_description()
        if desc:
            desc_text = ' description="%s"' % self.fix(desc)
        else:
            desc_text = ""
        checksum = obj.get_checksum()
        if checksum:
            checksum_text = ' checksum="%s"' % checksum
        else:
            checksum_text = ""
        if self.strip_photos == 1:
            path = os.path.basename(path)
        elif self.strip_photos == 2 and (len(path) > 0 and os.path.isabs(path)):
            drive, path = os.path.splitdrive(path)
            path = path[1:]
        if win():
            # Always export path with \ replaced with /. Otherwise import
            # from Windows to Linux of gpkg's path to images does not work.
            path = path.replace("\\", "/")
        self.g.write(
            '%s<file src="%s" mime="%s"%s%s/>\n'
            % (
                "  " * (index + 1),
                self.fix(path),
                self.fix(mime_type),
                checksum_text,
                desc_text,
            )
        )
        self.write_attribute_list(obj.get_attribute_list())
        self.write_note_list(obj.get_note_list(), index + 1)
        dval = obj.get_date_object()
        if not dval.is_empty():
            self.write_date(dval, index + 1)
        for citation_handle in obj.get_citation_list():
            self.write_ref("citationref", citation_handle, index + 1)

        for tag_handle in obj.get_tag_list():
            self.write_ref("tagref", tag_handle, index + 1)

        self.g.write("%s</object>\n" % ("  " * index))


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------
def sortById(first, second):
    fid = first.get_gramps_id()
    sid = second.get_gramps_id()

    if fid < sid:
        return -1
    else:
        return fid != sid


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------
def conf_priv(obj):
    if obj.get_privacy() != 0:
        return ' priv="%d"' % obj.get_privacy()
    else:
        return ""


# -------------------------------------------------------------------------
#
# export_data
#
# -------------------------------------------------------------------------
def export_data(database, filename, user, option_box=None):
    """
    Call the XML writer with the syntax expected by the export plugin.
    """
    if os.path.isfile(filename):
        try:
            shutil.copyfile(filename, filename + ".bak")
            shutil.copystat(filename, filename + ".bak")
        except:
            pass

    compress = _gzip_ok == 1

    if option_box:
        option_box.parse_options()
        database = option_box.get_filtered_database(database)
        compress = compress and option_box.get_use_compression()

    g = XmlWriter(database, user, 0, compress)
    return g.write(filename)


# -------------------------------------------------------------------------
#
# XmlWriter
#
# -------------------------------------------------------------------------
class XmlWriter(GrampsXmlWriter):
    """
    Writes a database to the XML file.
    """

    def __init__(self, dbase, user, strip_photos, compress=1):
        GrampsXmlWriter.__init__(self, dbase, strip_photos, compress, VERSION, user)
        self.user = user

    def write(self, filename):
        """
        Write the database to the specified file.
        """
        ret = 0  # False
        try:
            ret = GrampsXmlWriter.write(self, filename)
        except DbWriteFailure as msg:
            (m1, m2) = msg.messages()
            self.user.notify_error("%s\n%s" % (m1, m2))
        return ret
