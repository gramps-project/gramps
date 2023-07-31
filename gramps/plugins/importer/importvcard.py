#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Martin Hawlisch, Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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

"Import from vCard (RFC 2426)"

# -------------------------------------------------------------------------
#
# standard python modules
#
# -------------------------------------------------------------------------
import sys
import re
import time

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
import logging

LOG = logging.getLogger(".ImportvCard")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
ngettext = glocale.translation.ngettext  # else "nearby" comments are ignored
from gramps.gen.errors import GrampsImportError
from gramps.gen.lib import (
    Address,
    Date,
    DateError,
    Event,
    EventRef,
    EventType,
    Name,
    NameType,
    Person,
    Surname,
    Url,
    UrlType,
)
from gramps.gen.db import DbTxn
from gramps.gen.plug.utils import OpenFileOrStdin
from gramps.gen.utils.libformatting import ImportInfo


# -------------------------------------------------------------------------
#
# Support Functions
#
# -------------------------------------------------------------------------
def importData(database, filename, user):
    """Function called by Gramps to import data on persons in vCard format."""
    parser = VCardParser(database)
    try:
        with OpenFileOrStdin(filename) as filehandle:
            parser.parse(filehandle, user)
    except EnvironmentError as msg:
        user.notify_error(_("%s could not be opened\n") % filename, str(msg))
        return
    except GrampsImportError as msg:
        user.notify_error(_("%s could not be opened\n") % filename, str(msg))
        return
    ## a "vCard import report" happens in vCardParser so this is not needed:
    ## (but the imports_test.py unittest currently requires it, so here it is)
    return ImportInfo({_("Results"): _("done")})


def splitof_nameprefix(name):
    """
    Return a (prefix, Surname) tuple by splitting on first uppercase char.

    Shame on Python for not supporting [[:upper:]] in re!
    """
    look_for_capital = False
    for i, char in enumerate(name):
        if look_for_capital:
            if char.isupper():
                return (name[:i].rstrip(), name[i:])
            else:
                look_for_capital = False
        if not char.isalpha():
            look_for_capital = True
    return ("", name)


def fitin(prototype, receiver, element):
    """
    Return the index in string receiver at which element should be inserted
    to match part of prototype.

    Assume that the part of receiver that is not tested does match.
    Don't split to work with lists because element may contain a space!
    Example: fitin("Mr. Gaius Julius Caesar", "Gaius Caesar", "Julius") = 6

    :param prototype: Partly to be matched by inserting element in receiver.
    :type prototype: str
    :param receiver: Space separated words that miss words to match prototype.
    :type receiver: str
    :param element: Words that need to be inserted; error if not in prototype.
    :type element: str
    :returns: Returns index where element fits in receiver, -1 if receiver
              not in prototype, or throws IndexError if element at end receiver.
    :rtype: int
    """
    receiver_idx = 0
    receiver_chunks = receiver.split()
    element_idx = prototype.index(element)
    i = 0
    idx = prototype.find(receiver_chunks[i])
    while idx < element_idx:
        if idx == -1:
            return -1
        receiver_idx += len(receiver_chunks[i]) + 1
        i += 1
        idx = prototype.find(receiver_chunks[i])
    return receiver_idx


# -------------------------------------------------------------------------
#
# VCardParser class
#
# -------------------------------------------------------------------------
class VCardParser:
    """Class to read data in vCard format from a file."""

    DATE_RE = re.compile(r"^(\d{4}-\d{1,2}-\d{1,2})|(?:(\d{4})-?(\d\d)-?(\d\d))")
    GROUP_RE = re.compile(r"^(?:[-0-9A-Za-z]+\.)?(.+)$")  # see RFC 2425 sec5.8.2
    ESCAPE_CHAR = "\\"
    TOBE_ESCAPED = ["\\", ",", ";"]  # order is important
    LINE_CONTINUATION = [" ", "\t"]

    @staticmethod
    def name_value_split(data):
        """Property group.name:value split is on first unquoted colon."""
        colon_idx = data.find(":")
        if colon_idx < 1:
            return ()
        quote_count = data.count('"', 0, colon_idx)
        while quote_count % 2 == 1:
            colon_idx = data.find(":", colon_idx + 1)
            quote_count = data.count('"', 0, colon_idx)
        group_name, value = data[:colon_idx], data[colon_idx + 1 :]
        name_parts = VCardParser.GROUP_RE.match(group_name)
        return (name_parts.group(1), value)

    @staticmethod
    def unesc(data):
        """Remove vCard escape sequences."""
        if type(data) == type("string"):
            for char in reversed(VCardParser.TOBE_ESCAPED):
                data = data.replace(VCardParser.ESCAPE_CHAR + char, char)
            return data
        elif type(data) == type([]):
            return list(map(VCardParser.unesc, data))
        else:
            raise TypeError(
                "vCard unescaping is not implemented for "
                "data type %s." % str(type(data))
            )

    @staticmethod
    def count_escapes(strng):
        """Count the number of escape characters at the end of a string."""
        count = 0
        for char in reversed(strng):
            if char != VCardParser.ESCAPE_CHAR:
                return count
            count += 1
        return count

    @staticmethod
    def split_unescaped(strng, sep):
        """Split on sep if sep is unescaped."""
        strng_parts = strng.split(sep)
        for i in reversed(range(len(strng_parts[:]))):
            if VCardParser.count_escapes(strng_parts[i]) % 2 == 1:
                # the sep was escaped so undo split
                appendix = strng_parts.pop(i + 1)
                strng_parts[i] += sep + appendix
        return strng_parts

    def __init__(self, dbase):
        self.database = dbase
        self.formatted_name = ""
        self.name_parts = ""
        self.next_line = None
        self.trans = None
        self.version = None
        self.person = None
        self.errors = []
        self.number_of_errors = 0

    def __get_next_line(self, filehandle):
        """
        Read and return the line with the next property of the vCard.

        Also if it spans multiple lines (RFC 2425 sec.5.8.1).
        """
        line = self.next_line
        self.next_line = filehandle.readline()
        self.line_num = self.line_num + 1
        while self.next_line and self.next_line[0] in self.LINE_CONTINUATION:
            line = line.rstrip("\n")
            # TODO perhaps next lines superflous because of rU open parameter?
            if len(line) > 0 and line[-1] == "\r":
                line = line[:-1]
            line += self.next_line[1:]
            self.next_line = filehandle.readline()
            self.line_num = self.line_num + 1
        if line:
            line = line.strip()
        else:
            line = None
        return line

    def __add_msg(self, problem, line=None):
        if problem != "":
            self.number_of_errors += 1
        if line:
            message = _("Line %(line)5d: %(prob)s\n") % {"line": line, "prob": problem}
        else:
            message = problem + "\n"
        self.errors.append(message)

    def parse(self, filehandle, user):
        """
        Prepare the database and parse the input file.

        :param filehandle: open file handle positioned at start of the file
        """
        tym = time.time()
        self.person = None
        self.database.disable_signals()
        with DbTxn(_("vCard import"), self.database, batch=True) as self.trans:
            self._parse_vCard_file(filehandle)
        self.database.enable_signals()
        self.database.request_rebuild()
        tym = time.time() - tym
        # Translators: leave all/any {...} untranslated
        msg = ngettext(
            "Import Complete: {number_of} second",
            "Import Complete: {number_of} seconds",
            tym,
        ).format(number_of=tym)
        LOG.debug(msg)
        if self.number_of_errors == 0:
            message = _("vCard import report: No errors detected")
        else:
            message = (
                _("vCard import report: %s errors detected\n") % self.number_of_errors
            )
        if hasattr(user.uistate, "window"):
            parent_window = user.uistate.window
        else:
            parent_window = None
        user.info(message, "".join(self.errors), parent=parent_window, monospaced=True)

    def _parse_vCard_file(self, filehandle):
        """Read each line of the input file and act accordingly."""
        self.next_line = filehandle.readline()
        self.line_num = 1

        while True:
            line = self.__get_next_line(filehandle)
            if line is None:
                break
            if line == "":
                continue

            if line.find(":") == -1:
                continue
            line_parts = self.name_value_split(line)
            if not line_parts:
                continue

            # No check for escaped ; because only fields[0] is used.
            fields = line_parts[0].split(";")

            property_name = fields[0].upper()
            if property_name == "BEGIN":
                self.next_person()
            elif property_name == "END":
                self.finish_person()
            elif property_name == "VERSION":
                self.check_version(fields, line_parts[1])
            elif property_name == "FN":
                self.add_formatted_name(fields, line_parts[1])
            elif property_name == "N":
                self.add_name_parts(fields, line_parts[1])
            elif property_name == "NICKNAME":
                self.add_nicknames(fields, line_parts[1])
            elif property_name == "SORT-STRING":
                self.add_sortas(fields, line_parts[1])
            elif property_name == "ADR":
                self.add_address(fields, line_parts[1])
            elif property_name == "TEL":
                self.add_phone(fields, line_parts[1])
            elif property_name == "BDAY":
                self.add_birthday(fields, line_parts[1])
            elif property_name == "ROLE":
                self.add_occupation(fields, line_parts[1])
            elif property_name == "URL":
                self.add_url(fields, line_parts[1])
            elif property_name == "EMAIL":
                self.add_email(fields, line_parts[1])
            elif property_name == "X-GENDER" or property_name == "GENDER":
                # vCard 3.0 only has X-GENDER, GENDER is 4.0 syntax,
                # but we want to be robust here.
                self.add_gender(fields, line_parts[1])
            elif property_name == "PRODID":
                # Included cause vCards made by Gramps have this prop.
                pass
            else:
                self.__add_msg(
                    _("Token >%(token)s< unknown. line skipped: %(line)s")
                    % {"token": (fields[0], line), "line": self.line_num - 1}
                )

    def finish_person(self):
        """All info has been collected, write to database."""
        if self.person is not None:
            if self.add_name():
                self.database.add_person(self.person, self.trans)
        self.person = None

    def next_person(self):
        """A vCard for another person is started."""
        if self.person is not None:
            self.finish_person()
            self.__add_msg(
                _(
                    "BEGIN property not properly closed by END "
                    "property, Gramps can't cope with nested vCards."
                ),
                self.line_num - 1,
            )
        self.person = Person()
        self.formatted_name = ""
        self.name_parts = ""

    def check_version(self, fields, data):
        """Check the version of the vCard, only version 3.0 is supported."""
        self.version = data
        if self.version != "3.0":
            raise GrampsImportError(
                _("Import of vCards version %s is " "not supported by Gramps.")
                % self.version
            )

    def add_formatted_name(self, fields, data):
        """Read the FN property of a vCard."""
        if not self.formatted_name:
            self.formatted_name = self.unesc(str(data)).strip()

    def add_name_parts(self, fields, data):
        """Read the N property of a vCard."""
        if not self.name_parts:
            self.name_parts = data.strip()

    def add_name(self):
        """
        Add the name to the person.

        Returns True on success, False on failure.
        """
        if not self.name_parts.strip():
            self.__add_msg(
                _(
                    "The vCard is malformed. It is missing the compulsory N "
                    "property, so there is no name; skip it."
                ),
                self.line_num - 1,
            )
            return False
        if not self.formatted_name:
            self.__add_msg(
                _(
                    "The vCard is malformed. It is missing the compulsory FN "
                    "property, get name from N alone."
                ),
                self.line_num - 1,
            )
        data_fields = self.split_unescaped(self.name_parts, ";")
        if len(data_fields) != 5:
            self.__add_msg(
                _("The vCard is malformed. Wrong number of name " "components."),
                self.line_num - 1,
            )

        name = Name()
        name.set_type(NameType(NameType.BIRTH))

        if data_fields[0].strip():
            # assume first surname is primary
            for surname_str in self.split_unescaped(data_fields[0], ","):
                surname = Surname()
                prefix, sname = splitof_nameprefix(self.unesc(surname_str))
                surname.set_surname(sname.strip())
                surname.set_prefix(prefix.strip())
                name.add_surname(surname)
            name.set_primary_surname()

        if len(data_fields) > 1 and data_fields[1].strip():
            given_name = " ".join(self.unesc(self.split_unescaped(data_fields[1], ",")))
        else:
            given_name = ""
        if len(data_fields) > 2 and data_fields[2].strip():
            additional_names = " ".join(
                self.unesc(self.split_unescaped(data_fields[2], ","))
            )
        else:
            additional_names = ""
        self.add_firstname(given_name.strip(), additional_names.strip(), name)

        if len(data_fields) > 3 and data_fields[3].strip():
            name.set_title(
                " ".join(self.unesc(self.split_unescaped(data_fields[3], ",")))
            )
        if len(data_fields) > 4 and data_fields[4].strip():
            name.set_suffix(
                " ".join(self.unesc(self.split_unescaped(data_fields[4], ",")))
            )

        self.person.set_primary_name(name)
        return True

    def add_firstname(self, given_name, additional_names, name):
        """
        Combine given_name and additional_names and add as firstname to name.

        If possible try to add given_name as call name.
        """
        default = "%s %s" % (given_name, additional_names)
        if self.formatted_name:
            if given_name:
                if additional_names:
                    given_name_pos = self.formatted_name.find(given_name)
                    if given_name_pos != -1:
                        add_names_pos = self.formatted_name.find(additional_names)
                        if add_names_pos != -1:
                            if given_name_pos <= add_names_pos:
                                firstname = default
                                # Uncertain if given name is used as callname
                            else:
                                firstname = "%s %s" % (additional_names, given_name)
                                name.set_call_name(given_name)
                        else:
                            idx = fitin(
                                self.formatted_name, additional_names, given_name
                            )
                            if idx == -1:
                                # Additional names is not in formatted name
                                firstname = default
                            else:  # Given name in middle of additional names
                                firstname = "%s%s %s" % (
                                    additional_names[:idx],
                                    given_name,
                                    additional_names[idx:],
                                )
                                name.set_call_name(given_name)
                    else:  # Given name is not in formatted name
                        firstname = default
                else:  # There are no additional_names
                    firstname = given_name
            else:  # There is no given_name
                firstname = additional_names
        else:  # There is no formatted name
            firstname = default
        name.set_first_name(firstname.strip())
        return

    def add_nicknames(self, fields, data):
        """Read the NICKNAME property of a vCard."""
        for nick in self.split_unescaped(data, ","):
            nickname = nick.strip()
            if nickname:
                name = Name()
                name.set_nick_name(self.unesc(nickname))
                self.person.add_alternate_name(name)

    def add_sortas(self, fields, data):
        """Read the SORT-STRING property of a vCard."""
        # TODO
        pass

    def add_address(self, fields, data):
        """Read the ADR property of a vCard."""
        data_fields = self.split_unescaped(data, ";")
        data_fields = [x.strip() for x in self.unesc(data_fields)]
        if "".join(data_fields):
            addr = Address()

            def add_street(strng):
                if strng:
                    already = addr.get_street()
                    if already:
                        addr.set_street("%s %s" % (already, strng))
                    else:
                        addr.set_street(strng)

            addr.add_street = add_street
            set_func = [
                "add_street",
                "add_street",
                "add_street",
                "set_city",
                "set_state",
                "set_postal_code",
                "set_country",
            ]
            for i, data in enumerate(data_fields):
                if i >= len(set_func):
                    break
                getattr(addr, set_func[i])(data)
            self.person.add_address(addr)

    def add_phone(self, fields, data):
        """Read the TEL property of a vCard."""
        tel = data.strip()
        if tel:
            addr = Address()
            addr.set_phone(self.unesc(tel))
            self.person.add_address(addr)

    def add_birthday(self, fields, data):
        """Read the BDAY property of a vCard."""
        date_str = data.strip()
        date_match = VCardParser.DATE_RE.match(date_str)
        date = Date()
        if date_match:
            if date_match.group(2):
                date_str = "%s-%s-%s" % (
                    date_match.group(2),
                    date_match.group(3),
                    date_match.group(4),
                )
            else:
                date_str = date_match.group(1)
            y, m, d = [int(x, 10) for x in date_str.split("-")]
            try:
                date.set(value=(d, m, y, False))
            except DateError:
                # Translators: leave the {vcard_snippet} untranslated
                # in the format string, but you may re-order it if needed.
                self.__add_msg(
                    _(
                        "Invalid date in BDAY {vcard_snippet}, "
                        "preserving date as text."
                    ).format(vcard_snippet=data),
                    self.line_num - 1,
                )
                date.set(modifier=Date.MOD_TEXTONLY, text=data)
        else:
            if date_str:
                # Translators: leave the {vcard_snippet} untranslated.
                self.__add_msg(
                    _(
                        "Date {vcard_snippet} not in appropriate format "
                        "yyyy-mm-dd, preserving date as text."
                    ).format(vcard_snippet=date_str),
                    self.line_num - 1,
                )
                date.set(modifier=Date.MOD_TEXTONLY, text=date_str)
            else:  # silently ignore an empty BDAY record
                return
        event = Event()
        event.set_type(EventType(EventType.BIRTH))
        event.set_date_object(date)
        self.database.add_event(event, self.trans)

        event_ref = EventRef()
        event_ref.set_reference_handle(event.get_handle())
        self.person.set_birth_ref(event_ref)

    def add_occupation(self, fields, data):
        """Read the ROLE property of a vCard."""
        occupation = data.strip()
        if occupation:
            event = Event()
            event.set_type(EventType(EventType.OCCUPATION))
            event.set_description(self.unesc(occupation))
            self.database.add_event(event, self.trans)

            event_ref = EventRef()
            event_ref.set_reference_handle(event.get_handle())
            self.person.add_event_ref(event_ref)

    def add_url(self, fields, data):
        """Read the URL property of a vCard."""
        href = data.strip()
        if href:
            url = Url()
            url.set_path(self.unesc(href))
            self.person.add_url(url)

    def add_email(self, fields, data):
        """Read the EMAIL property of a vCard."""
        email = data.strip()
        if email:
            url = Url()
            url.set_type(UrlType(UrlType.EMAIL))
            url.set_path(self.unesc(email))
            self.person.add_url(url)

    def add_gender(self, fields, data):
        """Read the GENDER property of a vCard."""
        gender_value = data.strip()
        if gender_value:
            gender_value = gender_value.upper()
            gender_value = gender_value[0]
            if gender_value == "M":
                gender = Person.MALE
            elif gender_value == "F":
                gender = Person.FEMALE
            elif gender_value == "O":
                gender = Person.OTHER
            else:
                return
            self.person.set_gender(gender)
