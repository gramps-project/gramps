#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004  Martin Hawlisch
# Copyright (C) 2005-2008  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Michiel D. Nauta
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

"Export Persons to vCard (RFC 2426)."

# -------------------------------------------------------------------------
#
# Standard Python Modules
#
# -------------------------------------------------------------------------
import sys
from textwrap import TextWrapper

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
import logging
from collections import abc

log = logging.getLogger(".ExportVCard")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.const import PROGRAM_NAME
from gramps.version import VERSION
from gramps.gen.lib import Date, Person
from gramps.gen.lib.urltype import UrlType
from gramps.gui.plug.export import WriterOptionBox
from gramps.gen.lib.eventtype import EventType
from gramps.gen.display.name import displayer as _nd
from gramps.gen.plug.utils import OpenFileOrStdout


# -------------------------------------------------------------------------
#
# Support Functions
#
# -------------------------------------------------------------------------
def exportData(database, filename, user, option_box=None):
    """Function called by Gramps to export data on persons in VCard format."""
    cardw = VCardWriter(database, filename, option_box, user)
    try:
        cardw.export_data()
    except EnvironmentError as msg:
        user.notify_error(_("Could not create %s") % filename, str(msg))
        return False
    except:
        # Export shouldn't bring Gramps down.
        user.notify_error(_("Could not create %s") % filename)
        return False
    return True


# -------------------------------------------------------------------------
#
# VCardWriter class
#
# -------------------------------------------------------------------------
class VCardWriter:
    """Class to create a file with data in VCard format."""

    LINELENGTH = 73  # unclear if the 75 chars of spec includes \r\n.
    ESCAPE_CHAR = "\\"
    TOBE_ESCAPED = ["\\", ",", ";"]  # order is important
    LINE_CONTINUATION = [" ", "\t"]

    @staticmethod
    def esc(data):
        """Escape the special chars of the VCard protocol."""
        if isinstance(data, str):
            for char in VCardWriter.TOBE_ESCAPED:
                data = data.replace(char, VCardWriter.ESCAPE_CHAR + char)
            return data
        elif type(data) == type([]):
            return list(map(VCardWriter.esc, data))
        elif type(data) == type(()):
            return tuple(map(VCardWriter.esc, data))
        else:
            raise TypeError(
                "VCard escaping is not implemented for "
                "data type %s." % str(type(data))
            )

    def __init__(self, database, filename, option_box=None, user=None):
        self.db = database
        self.filename = filename
        self.user = user
        self.filehandle = None
        self.option_box = option_box
        if isinstance(self.user.callback, abc.Callable):  # is really callable
            self.update = self.update_real
        else:
            self.update = self.update_empty

        if option_box:
            self.option_box.parse_options()
            self.db = option_box.get_filtered_database(self.db)

        self.txtwrp = TextWrapper(
            width=self.LINELENGTH,
            expand_tabs=False,
            replace_whitespace=False,
            drop_whitespace=False,
            subsequent_indent=self.LINE_CONTINUATION[0],
        )
        self.count = 0
        self.total = 0

    def update_empty(self):
        """Progress can't be reported."""
        pass

    def update_real(self):
        """Report progress."""
        self.count += 1
        newval = int(100 * self.count / self.total)
        if newval != self.oldval:
            self.user.callback(newval)
            self.oldval = newval

    def writeln(self, text):
        """
        Write a property of the VCard to file.

        Can't cope with nested VCards, section 2.4.2 of RFC 2426.
        """
        self.filehandle.write(
            "%s\r\n" % "\r\n".join([line for line in self.txtwrp.wrap(text)])
        )

    def export_data(self):
        """Open the file and loop over everyone too write their VCards."""
        with OpenFileOrStdout(
            self.filename, encoding="utf-8", errors="strict", newline=""
        ) as self.filehandle:
            if self.filehandle:
                self.count = 0
                self.oldval = 0
                self.total = self.db.get_number_of_people()
                for key in sorted(list(self.db.iter_person_handles())):
                    self.write_person(key)
                    self.update()
        return True

    def write_person(self, person_handle):
        """Create a VCard for the specified person."""
        person = self.db.get_person_from_handle(person_handle)
        if person:
            self.write_header()
            prname = person.get_primary_name()
            self.write_formatted_name(prname)
            self.write_name(prname)
            self.write_sortstring(prname)
            self.write_nicknames(person, prname)
            self.write_gender(person)
            self.write_birthdate(person)
            self.write_addresses(person)
            self.write_urls(person)
            self.write_occupation(person)
            self.write_footer()

    def write_header(self):
        """Write the opening lines of a VCard."""
        self.writeln("BEGIN:VCARD")
        self.writeln("VERSION:3.0")
        self.writeln("PRODID:-//Gramps//NONSGML %s %s//EN" % (PROGRAM_NAME, VERSION))

    def write_footer(self):
        """Write the closing lines of a VCard."""
        self.writeln("END:VCARD")
        self.writeln("")

    def write_formatted_name(self, prname):
        """Write the compulsory FN property of VCard."""
        regular_name = prname.get_regular_name().strip()
        title = prname.get_title()
        if title:
            regular_name = "%s %s" % (title, regular_name)
        self.writeln("FN:%s" % self.esc(regular_name))

    def write_name(self, prname):
        """Write the compulsory N property of a VCard."""
        family_name = ""
        given_name = ""
        additional_names = ""
        hon_prefix = ""
        suffix = ""

        primary_surname = prname.get_primary_surname()
        surname_list = prname.get_surname_list()
        if not surname_list[0].get_primary():
            surname_list.remove(primary_surname)
            surname_list.insert(0, primary_surname)
        family_name = ",".join(
            self.esc(
                [
                    (
                        "%s %s %s"
                        % (
                            surname.get_prefix(),
                            surname.get_surname(),
                            surname.get_connector(),
                        )
                    ).strip()
                    for surname in surname_list
                ]
            )
        )

        call_name = prname.get_call_name()
        if call_name:
            given_name = self.esc(call_name)
            additional_name_list = prname.get_first_name().split()
            if call_name in additional_name_list:
                additional_name_list.remove(call_name)
            additional_names = ",".join(self.esc(additional_name_list))
        else:
            name_list = prname.get_first_name().split()
            if len(name_list) > 0:
                given_name = self.esc(name_list[0])
                if len(name_list) > 1:
                    additional_names = ",".join(self.esc(name_list[1:]))
        # Alternate names are ignored because names just don't add up:
        # if one name is Jean and an alternate is Paul then you can't
        # conclude the Jean Paul is also an alternate name of that person.

        # Assume all titles/suffixes that apply are present in primary name.
        hon_prefix = ",".join(self.esc(prname.get_title().split()))
        suffix = ",".join(self.esc(prname.get_suffix().split()))

        self.writeln(
            "N:%s;%s;%s;%s;%s"
            % (family_name, given_name, additional_names, hon_prefix, suffix)
        )

    def write_sortstring(self, prname):
        """Write the SORT-STRING property of a VCard."""
        # TODO only add sort-string if needed
        self.writeln("SORT-STRING:%s" % self.esc(_nd.sort_string(prname)))

    def write_nicknames(self, person, prname):
        """Write the NICKNAME property of a VCard."""
        nicknames = [
            x.get_nick_name() for x in person.get_alternate_names() if x.get_nick_name()
        ]
        if prname.get_nick_name():
            nicknames.insert(0, prname.get_nick_name())
        if len(nicknames) > 0:
            self.writeln("NICKNAME:%s" % (",".join(self.esc(nicknames))))

    def write_gender(self, person):
        """Write the X-GENDER property of a VCard (X- dropped in 4.0, we're at 3.0)."""
        gender = person.get_gender()
        gender_value = ""
        if gender == Person.MALE:
            gender_value = "Male"
        elif gender == Person.FEMALE:
            gender_value = "Female"
        elif gender == Person.OTHER:
            gender_value = "Other"
        log.info("gender: %s -> %s" % (gender, gender_value))
        if gender_value:
            self.writeln("X-GENDER:%s" % (gender_value))

    def write_birthdate(self, person):
        """Write the BDAY property of a VCard."""
        birth_ref = person.get_birth_ref()
        if birth_ref:
            birth = self.db.get_event_from_handle(birth_ref.ref)
            if birth:
                b_date = birth.get_date_object()
                mod = b_date.get_modifier()
                if (
                    mod != Date.MOD_TEXTONLY
                    and not b_date.is_empty()
                    and not mod == Date.MOD_SPAN
                    and not mod == Date.MOD_FROM
                    and not mod == Date.MOD_TO
                    and not mod == Date.MOD_RANGE
                ):
                    (day, month, year, slash) = b_date.get_start_date()
                    if day > 0 and month > 0 and year > 0:
                        self.writeln("BDAY:%s-%02d-%02d" % (year, month, day))

    def write_addresses(self, person):
        """Write ADR and TEL properties of a VCard."""
        address_list = person.get_address_list()
        for address in address_list:
            postbox = ""
            ext = ""
            street = address.get_street()
            city = address.get_city()
            state = address.get_state()
            zipcode = address.get_postal_code()
            country = address.get_country()
            if street or city or state or zipcode or country:
                self.writeln(
                    "ADR:%s;%s;%s;%s;%s;%s;%s"
                    % self.esc((postbox, ext, street, city, state, zipcode, country))
                )

            phone = address.get_phone()
            if phone:
                self.writeln("TEL:%s" % phone)

    def write_urls(self, person):
        """Write URL and EMAIL properties of a VCard."""
        url_list = person.get_url_list()
        for url in url_list:
            href = url.get_path()
            if href:
                if url.get_type() == UrlType(UrlType.EMAIL):
                    if href.startswith("mailto:"):
                        href = href[len("mailto:") :]
                    self.writeln("EMAIL:%s" % self.esc(href))
                else:
                    self.writeln("URL:%s" % self.esc(href))

    def write_occupation(self, person):
        """
        Write ROLE property of a VCard.

        Use the most recent occupation event.
        """
        event_refs = person.get_primary_event_ref_list()
        events = [
            event
            for event in [self.db.get_event_from_handle(ref.ref) for ref in event_refs]
            if event.get_type() == EventType(EventType.OCCUPATION)
        ]
        if len(events) > 0:
            events.sort(key=lambda x: x.get_date_object())
            occupation = events[-1].get_description()
            if occupation:
                self.writeln("ROLE:%s" % occupation)
