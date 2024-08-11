#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
Parses the lds.xml file to build the temple/code maps
"""

from ..const import DATA_DIR
import os
import logging

from xml.parsers.expat import ParserCreate
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

LOG = logging.getLogger(".")


class LdsTemples:
    """
    Parsing class for the LDS temples file
    """

    def __init__(self):
        """
        Parses the lds.xml file to load the LDS temple code to name
        maps
        """
        self.__temple_codes = {}
        self.__temple_to_abrev = {}
        self.__current_temple = ""
        self.__tlist = []

        lds_filename = os.path.expanduser(os.path.join(DATA_DIR, "lds.xml"))

        try:
            parser = ParserCreate()
            parser.StartElementHandler = self.__start_element
            parser.EndElementHandler = self.__end_element
            parser.CharacterDataHandler = self.__characters
            with open(lds_filename, "rb") as xml_file:
                parser.ParseFile(xml_file)
        except Exception as msg:
            LOG.error(str(msg))

    def is_valid_code(self, code):
        """
        returns True if the code is a valid LDS temple code according
        to the lds.xml file
        """
        return self.__temple_to_abrev.get(code) is not None

    def is_valid_name(self, name):
        """
        returns True if the name matches a temple name (not code) in
        the lds.xml file
        """
        return self.__temple_codes.get(name) is not None

    def code(self, name):
        """
        returns the LDS Temple code that corresponds to the name
        """
        return self.__temple_codes.get(name, _("Unknown"))

    def name(self, code):
        """
        returns the name associated with the LDS Temple code
        """
        return self.__temple_to_abrev.get(code, _("Unknown"))

    def name_code_data(self):
        """
        returns a list of temple codes, temple name tuples
        """
        return sorted(
            [(code, name) for name, code in self.__temple_codes.items()],
            key=lambda v: v[1],
        )

    def __start_element(self, tag, attrs):
        """
        XML parsing function that is called when an XML element is first found
        """
        self.__tlist = []
        if tag == "temple":
            self.__current_temple = attrs.get("name")

    def __end_element(self, tag):
        """
        XML parsing function that is called when an XML element is closed
        """

        text = "".join(self.__tlist)

        if tag == "code":
            if self.__temple_codes.get(self.__current_temple) is None:
                self.__temple_codes[self.__current_temple] = text
            self.__temple_to_abrev[text] = self.__current_temple

    def __characters(self, data):
        """
        XML parsing function that collects text data
        """
        self.__tlist.append(data)


TEMPLES = LdsTemples()
